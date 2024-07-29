# instantiate the pipeline
from pyannote.audio import Pipeline

import soundfile
import wave
import numpy

file_path = "recording_1722282885.wav"

# Read and rewrite the file with soundfile
data, samplerate = soundfile.read(file_path)
soundfile.write(file_path, data, samplerate)

# Now try to open the file with wave
with wave.open(file_path) as file:
    print('File opened!')




# Read file to get buffer                                                                                               
ifile = wave.open(file_path)
samples = ifile.getnframes()
audio = ifile.readframes(samples)

# Convert buffer to float32 using NumPy                                                                                 
audio_as_np_int16 = numpy.frombuffer(audio, dtype=numpy.int16)
audio_as_np_float32 = audio_as_np_int16.astype(numpy.float32)

# Normalise float32 array so that values are between -1.0 and +1.0                                                      
max_int16 = 2**15
audio_normalised = audio_as_np_float32 / max_int16





pipeline = Pipeline.from_pretrained(
  "pyannote/speaker-diarization-3.1",
  use_auth_token="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")

# run the pipeline on an audio file
diarization = pipeline(audio_normalised)

# dump the diarization output to disk using RTTM format
with open("recording_1722282885.rttm", "w") as rttm:
    diarization.write_rttm(rttm)
