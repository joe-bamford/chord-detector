# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 18:54:01 2022

@author: bamjoe
"""

#%% IMPORTS AND SETUP

import numpy as np
import yellowbrick
import librosa as lb
import time
import threading
import os
import scipy
from scipy import signal as sg
from scipy.fftpack import fft
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import librosa.display as lbd
import pychord as pc
import re
import pygame as pg
import pygame.midi
import pyaudio as pa
import struct as st
import keyboard as kb

# Font and style
plt.rcParams.update({
    "text.usetex": False,
    "font.family": "serif",
    'font.size': 14,
    "font.sans-serif": ["Computer Modern Roman"]})

plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['mathtext.rm'] = 'Computer Modern Roman'
plt.rcParams['mathtext.it'] = 'Computer Modern Roman:italic'
plt.rcParams['mathtext.bf'] = 'Computer Modern Roman:bold'
plt.rcParams["axes.grid"] = True

pd.set_option('mode.chained_assignment', None)

#%% VARS

fft_sr = 20
sr = 22050
frdown = 27.5
frup = 5000

#%% FUNCS

class tools(threading.Thread):

    # Convert time from [mins:secs] to secs
    def convert_time(times: list, clip_length: float) -> list:
        if times[0] == '':
            times[0] = '0:0'
        times_secs = []
        for time in times:
            if time == '':
                times_secs.append(clip_length)
            else:
                mins, secs = re.split('[:,.]',time)
                times_secs.append(int(secs) + 60*int(mins))
        return np.array(times_secs)

    
    # Get notes from freqs through librosa and add to dataframe
    def get_notes(df: pd.DataFrame()) -> pd.DataFrame:
        notes_col = []
        for i in df.index:
            notes = lb.hz_to_note(df['Freqs'][i])
            # Remove numbers from note names and replace sharp character with hash
            notes = [re.sub('[0-9]','',j) for j in notes]
            notes = [re.sub('???','#',j) for j in notes]
            notes = [re.sub('???','b',j) for j in notes]            
            # Remove duplicate notes
            notes = list(dict.fromkeys(notes))
            notes_col.append(notes)
        df['Notes'] = notes_col
        return df
    
    
    # Get chords from notes through pychord and add to dataframe
    def get_chords_df(df: pd.DataFrame(), force_slash: bool) -> pd.DataFrame:
        chords_col = []
        for i in df.index:
            notes = df.at[i,'Notes']
            if force_slash == False:
                chord = pc.find_chords_from_notes(notes, slash='n')
            else:
                chord = pc.find_chords_from_notes(notes[1:], slash=notes[0])
            chords_col.append(chord)
        df['Chord'] = chords_col
        return df
    
    
    # Get chords from notes and return as a simple list
    def get_chords(notes):
        main_chord = str(pc.find_chords_from_notes(notes)).split(',')[0]
        slash_chord = str(pc.find_chords_from_notes(notes[1:], slash=notes[0])).split(',')[0]
        chords = [main_chord, slash_chord]
        # if chords == ['[]','[]']:
        #     chords = []
        return chords
    
    # Get manual key input
    def get_key() -> str:        
        key = str(input('Enter key: ').upper())
        # if type(key) is None:
        #     print('none')
        #     key = 'C'
        if 'M' in key:
            key = key.replace('M','')
            key = key+':min'
        else:
            key = key+':maj'
        return key

    # Convert numbers to notes for MIDI input
    def number_to_note(number):
        
        notes = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
        # In case you prefer sharps (weirdo)
        # notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return notes[number % 12]
    
    # Format chords for MIDI stream
    def format_chord(chord):
        
        fmt_dict = {'(':r'$^($',
                    ')':r'$^)$',
                    'b':r'$^{\flat}$',
                    '#':r'$^{\sharp}$',
                    '??':r'$^{\mathrm{o}}$',
                    '??':r'$^{\o}$',
                    '7':r'$^7$',
                    '???':r'$\Delta$',
                    'sus':r'$^{\mathrm{sus}}$',
                    'add':r'$^{\mathrm{add}}$',
                    'dim':r'$^{\mathrm{dim}}$',
                    'omit':r'$^{\mathrm{omit}}$',
                    '2':r'$^2$',
                    '4':r'$^4$',
                    '5':r'$^5$',
                    '6':r'$^6$',
                    '9':r'$^9$',
                    '11':r'$^{11}$',
                    '13':r'$^{13}$'}
        
        if not chord == '':   
            # Remove junk
            chord = re.sub(r'[<>]|[\[\]]','',chord)
            chord = chord.replace('Chord: ','')
            for key in fmt_dict:
                # Ignore already replaced substrings
                if str(fmt_dict[key]) in chord:
                    continue
                # Replace ones not yet done
                if str(key) in chord:
                    chord = chord.replace(key, fmt_dict[key])                
        return chord
