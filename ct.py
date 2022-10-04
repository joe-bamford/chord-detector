# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 12:14:49 2022

@author: bamjoe

INSPIRED BY TUTORIAL BY MEDALLION DATA SCIENCE: https://www.youtube.com/watch?v=ZqpSb5p1xQo
"""

from tools import *

plt.close('all')
# FFT sample rate (Hz)
fft_sr = 10
fft_win = 4096

#%% READ FILE

print("Please choose an audio file")
Tk().withdraw() 
# Prompt user to search for file
file = askopenfilename()
print(file)

raw, sr = lb.load(file)
filename = file.split('/')[-1].split('.')[0]
# Length of audio clip in secs
clip_length = raw.size/sr

# Compress raw time series
# raw = raw[::5]

# Input key
key = tools.get_key()

#%% SPLIT HARMONIC AND PERCUSSIVE COMPONENTS, PLOT TIME SERIES

fig, ax = plt.subplots(nrows=1, sharex=True)
y_harm, y_perc = lb.effects.hpss(raw)
lb.display.waveshow(y_harm, sr=sr, alpha=0.5, ax=ax, label='Harmonic')
lb.display.waveshow(y_perc, sr=sr, color='r', alpha=0.5, ax=ax, label='Percussive')
ax.set(title='Harmonic and percussive waveforms')
ax.legend(loc='best')

raw = y_harm

#%% LOG-FREQ SPECTROGRAM

fig, ax = plt.subplots(nrows=1, ncols=1, sharex=False)
spec_db = lb.amplitude_to_db(np.abs(lb.stft(raw, hop_length=sr//fft_sr, n_fft=fft_win)**2), ref=np.max)
img = lb.display.specshow(spec_db, y_axis='fft_note', sr=sr, hop_length=sr//fft_sr, x_axis='time', ax=ax, n_fft=fft_win)
ax.set(title='Log-frequency power spectrogram')
ax.label_outer()
# ax.grid(visible=True, which='major', axis='x', alpha=1, color='white')
fig.colorbar(img, ax=ax, format="%+2.f dB")
yl = ax.get_ylim()

#%% LOAD CHROMA DECOMP AND PLOT

# #%% COMPUTE CHROMA STFT AND SAVE TO CSV

S = np.abs(lb.stft(y=raw, n_fft=2048))**2
chroma = lb.feature.chroma_stft(S=S, sr=sr, hop_length=sr//fft_sr, n_chroma=12)
chroma = np.delete(chroma, 0, axis=1)
fig, ax = plt.subplots(nrows=1, sharex=True)
img = lb.display.specshow(chroma, y_axis='chroma', x_axis='time', ax=ax, hop_length=sr//fft_sr, key=key, fmin=frdown, fmax=frup)

#%% FIND PEAK FREQS

frange = np.linspace(yl[0], yl[1], len(spec_db[:,0]))
subsamples = np.arange(0, len(spec_db[0]), 1)
sps = {}
# pkp = {}
i=0
for sample in subsamples:
    sp = spec_db[:,sample]
    peaks = sg.find_peaks(sp, prominence=30)[0]
    freqs = frange[peaks]
    # peakvals = sp[peaks]
    # Remove values outside frequency range of the piano
    freqs = freqs[(freqs > frdown) & (freqs < frup)]
    # Check if list not empty, and if so dump into dict
    if peaks.tolist():
        sps[i] = {'indices':peaks,'freqs':freqs,'notes':[],'chord':[]}
        # pkp[i] = peakvals
    i+=1
    
#%% PLOT ANY SPECTRUM

s = input('Spectrum to plot (0-'+str(len(subsamples)-1)+'): ')
if type(s) is int:
    spectime = np.around(clip_length*s/(len(subsamples)-1),2)
    sp = spec_db[:,s]
    idxs = sps[s]['indices']
    
    # melfreqs = lb.mel_frequencies(n_mels=len(sp), fmin=lb.note_to_hz('A0'), fmax=lb.note_to_hz('C8'))
    fftfreqs = lb.fft_frequencies(sr=sr, n_fft=fft_win)
    
    specfig = plt.figure(figsize=(12,8))
    plt.plot(fftfreqs, sp, label='Spectrum')
    plt.xscale('log')
    plt.xlabel('Freq / Hz')
    plt.ylabel('dB')
    plt.scatter(fftfreqs[idxs], sp[idxs],c='r',label='Strongest frequencies')
    plt.title('Spectrum '+str(s)+' at t = '+str(spectime)+'s', fontsize=20)
    plt.legend(loc='best')
elif type(s) is None:
    pass

#%% IDENTIFY NOTES THEN USE PYCHORD TO GET CHORDS FROM NOTES
from tools import *

sps = tools.get_notes(sps)

rap = {}
# New dict containing only entries with 3 or more notes
cd = {key: entries for key, entries in sps.items() if len(sps[key]['notes']) >= 3}
# Find simpler chords on first pass and write to dict
for key in cd:
    cd[key]['chord'] = pc.find_chords_from_notes(cd[key]['notes'], rap, key, slash='n')

#%%

# Now deal with awkward slash chords
empties = [key for key in cd.keys() if not cd[key]['chord']]
for key in empties:
    notes = np.array(cd[key]['notes'])
    top_notes = notes[1:].tolist()
    cd[key]['chord'] = pc.find_chords_from_notes(top_notes, rap, key, slash=notes[0])

#%% TEST CELL

duffs = {key: entries for key, entries in cd.items() if not cd[key]['chord']}















    
    
    