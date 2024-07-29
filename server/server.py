import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from transformers import pipeline
from pyannote.audio import Pipeline

# Set custom cache directories
os.environ["HF_HOME"] = "C:/Users/YourUsername/.cache/huggingface"
os.environ["TRANSFORMERS_CACHE"] = "C:/Users/YourUsername/.cache/huggingface"
os.environ["TORCH_HOME"] = "C:/Users/YourUsername/.cache/torch"

app = Flask(__name__, static_folder='public')
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize pipelines
diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1")
summarization_pipeline = pipeline("summarization")

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    filename = secure_filename(audio_file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    audio_file.save(filepath)

    try:
        # Perform speaker diarization
        diarization = diarization_pipeline(filepath)
        transcription = ""
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segment = f"{speaker}: [{turn.start:.1f}s - {turn.end:.1f}s]\n"
            transcription += segment

        # Perform summarization (assuming you have transcriptions to summarize)
        summary = summarization_pipeline(transcription, max_length=150, min_length=30, do_sample=False)[0]['summary_text']

        response = {
            'transcription': transcription,
            'summary': summary
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        os.remove(filepath)

if __name__ == '__main__':
    app.run(debug=True)
