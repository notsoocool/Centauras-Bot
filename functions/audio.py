

import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
import speech_recognition as sr
import time



def record():
    
    freq = 48000 # sampling frequency
    duration = 5  # recording duraion

    # Start recorder with the given values
    # of duration and sample frequency
    recording = sd.rec(int(duration * freq), samplerate=freq, channels=2)

    # Record audio for the given number of seconds
    sd.wait()

    # This will convert the NumPy array to an audio
    # file with the given sampling frequency
    write("recording0.wav", freq, recording)

    # Convert the NumPy array to audio file
    wv.write("recording1.wav", recording, freq, sampwidth=2)
    
    



