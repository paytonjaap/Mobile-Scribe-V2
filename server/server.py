import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from transformers import pipeline
from pyannote.audio import Pipeline
import time, soundfile, io

# C:\huggingface-cache
# Set custom cache directories
os.environ["HF_HOME"] = "C:/Users/payto/.cache/huggingface"
os.environ["TRANSFORMERS_CACHE"] = "C:/Users/payto/.cache/huggingface"
os.environ["TORCH_HOME"] = "C:/Users/payto/.cache/torch"

app = Flask(__name__, static_folder='../public')
app.config['UPLOAD_FOLDER'] = 'C:/Users/payto/mobile-scribe-V2/uploads/'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize pipelines
diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token="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")
# summarization_pipeline = pipeline("sshleifer/distilbart-cnn-12-6")

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    print(str(request))
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    # audio_file = request.files['audio']
    # audio_file = request.files['audio'].read()
    audio_file = request.files.get('audio')
    # filename = 'recording_'+str(time.time()).split('.')[0]
    filename = 'recording_'+str(time.time()).split('.')[0]+'.wav'
    # filename = secure_filename(audio_file.filename)
    # filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    filepath = app.config['UPLOAD_FOLDER']+filename
    audio_file.save(filename)
    # audio_file.save(filepath)
    audio_file.flush()
    audio_file.close()
    # audio_file.seek(0)

    data,samplerate = soundfile.read(filename)
    soundfile.write('test.wav', 
                    data, 
                    samplerate,
                    subtype="PCM_16",
                    format="wav"
                    )
    # with io.BytesIO() as fio:
    #     soundfile.write(
    #         fio,
    #         data,
    #         samplerate=samplerate,
    #         subtype="PCM_16",
    #         format="wav"
    #     )

    #     data = fio.getvalue()
        
    

    try:
        # Perform speaker diarization
        # diarization = diarization_pipeline(filepath)
        diarization = diarization_pipeline(filename)
        
        with open(filename+".rttm", "w") as rttm:
            diarization.write_rttm(rttm)
        
        
        transcription = ""
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segment = f"{speaker}: [{turn.start:.1f}s - {turn.end:.1f}s]\n"
            transcription += segment

        # Perform summarization (assuming you have transcriptions to summarize)
        # summary = summarization_pipeline(transcription, max_length=150, min_length=30, do_sample=False)[0]['summary_text']

        response = {
            'transcription': transcription,
            # 'summary': summary
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # os.remove(filepath)
        pass

if __name__ == '__main__':
    app.run(debug=True)