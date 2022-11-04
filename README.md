# chord-detector (WIP)

## List of module dependencies
- numpy
- matplotlib
- pychord
- pygame
- librosa
- pandas
- scipy
- pyaudio
- struct
- keyboard
- yellowbrick (optional, only for plot aesthetics)


# _ct.py_

## Current functionality
Loads a .wav and splits the waveform into harmonic and percussive components, generates and plots a log-scaled spectrogram, picks out the strongest frequencies in each spectrum and maps these to notes. Where possible, groups of notes are then mapped to chords.

## Desired functionality
Greater reliability with chord identification.

# _ct-stream.py_

## Current functionality
Plots a live waveform and spectrum from microphone input stream, identifies notes and chords from the spectrum.

## Desired functionality
Greater stability in chord detection.

# _midi-stream.py_

## Current functionality
Takes live midi input and displays notes/chords through a matplotlib GUI.

## Desired functionality
Quicker response time.
