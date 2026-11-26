import soundfile as sf
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

# User input
INPUT_TIME = 6*60+5 # seconds
INPUT_DURATION = 16 # seconds
INPUT_RMS = 500     # samples - for calculating moving average
INPUT_THRESHOLD = -60  # dB
INPUT_MINIMUM_LENGTH = 1/10 # seconds

class AudioSplitter:
    """
    Splits an mp3 audio file containing speech into a number of individual mp3 chunks. Splits are optimized for silent intervals between words.
    
    Args:
        num_chunks: Number of individual chunks. Integer value.
        max_chunk_duration: Maximum duration of each chunk. Float value in seconds.
    """
    def __init__(self, file_path: str|Path, *, num_chunks: int|None=None, max_chunk_duration: float|None=None):
        self.file_path = file_path
        self.audio, self.sample_rate = sf.read(self.file_path)
        self.length = len(self.audio) / self.sample_rate # length of audio file in seconds

def split_audio(file_path: str|Path, *, num_chunks: int|None=None, max_chunk_duration: float|None=None, time_start: float=0, time_end: float|None=None, SILENCE_THRESHOLD: float=-60, RMS_MOVING_AVG: int|None=None, MIN_SILENCE_DURATION: float=1/10):
    """
    Splits an mp3 audio file containing speech into a number of individual mp3 chunks. Splits are optimized for silent intervals between words. The mp3 file may be trimmed to an audio slice prior to splitting.
    
    Args:
        num_chunks: Number of individual chunks. Integer value.
        max_chunk_duration: Maximum duration of each chunk. Float value in seconds.
        
        time_start: Start time of trimmed audio slice. Float value in seconds.
        time_end: End time of trimmed audio slice. Float value in seconds.

        SILENCE_THRESHOLD: Definition of max sound intensity for silent periods. Float value in decibel (dB).
        RMS_MOVING_AVG: Number of samples used for moving average when calculating root mean square (rms). Integer value defaulting to sample_rate/100.
        MIN_SILENCE_DURATION: Minimum duration of silence that will be considered for potential splitting. Float value in seconds defaulting to 1/10.

    Returns: 
        bingo bongo
    """
    audio, sample_rate = _load_file(file_path)
    
    # trim and convert to dB
    audio_slice_rms, audio_slice_dB, t_slice = _process_audio(audio, sample_rate, time_start, time_end, RMS_MOVING_AVG) # trim and convert to dB

    # TODO: find all periods below silence threshold

    # TODO: add plot

    # TODO: implement splitter algorithms

    # TODO: adjust obtained splits

    # TODO: add short beep at each split

    # TODO: split and output mp3 chunks
    
    ...

def _load_file(file_path: str|Path):
    audio, sample_rate = sf.read(file_path)
    audio_duration = len(audio) / sample_rate # duration of audio file in seconds
    print("Duration of mp3 file:") #{np.round(audio_duration, decimals=2)} seconds ({np.floor(audio_duration/60):.0f} min {round(audio_duration%60, ndigits=1)} sec)\nSample rate:', sample_rate, 'Hz')
    _print_duration(audio_duration, sample_rate)
    return audio, sample_rate

def _process_audio(audio: sf.AudioData|sf.AudioData_2d, sample_rate: int, time_start: float=0, time_end: float|None=None, RMS_MOVING_AVG: int|None=None):
    if RMS_MOVING_AVG is None:
            RMS_MOVING_AVG = round(sample_rate / 100)

    # trim audio and convert to ndarray
    if time_end is None:
        idx_end = len(audio)
        time_end = idx_end / sample_rate
    else:
        idx_end = time_end * sample_rate
        if idx_end > len(audio):
            idx_end = len(audio)
    idx_start = time_start * sample_rate
    slice_duration = time_end - time_start # duration of audio slice in seconds

    audio_slice = audio.T[0,idx_start:idx_end]
    t_slice = np.linspace(0, slice_duration, len(audio_slice))

    if idx_start != 0 and idx_end != len(audio):
            print("Duration of trimmed mp3 file:")
            _print_duration(slice_duration, sample_rate)

    # calculate moving RMS envelope of the audio signal and convert amplitude to decibel (dB)
    audio_slice_rms =  np.sqrt(np.convolve(audio_slice**2, np.ones(RMS_MOVING_AVG)/RMS_MOVING_AVG, mode="same"))
    audio_slice_dB = 20 * np.log10(audio_slice_rms) # convert amplitude to decibel (dB)
    return audio_slice_rms, audio_slice_dB, t_slice

def _print_duration(audio_duration, sample_rate: int) -> None:
    # TODO: add logic for print when duration < 1 sec and when duration > 60 min
    print(f'{np.round(audio_duration, decimals=2)} seconds ({np.floor(audio_duration/60):.0f} min {round(audio_duration%60, ndigits=1)} sec)\nSample rate:', sample_rate, 'Hz')
    
###############################################################
# OLD CODE BELOW THIS POINT
###############################################################

def main():
    # Import and read ---------------------------
    audio, samplerate = sf.read('Millionærklubben 2025-01-15 Er kvantecomputere investorernes næste yndlingstema.mp3')

    length = len(audio) / samplerate
    length_min = np.floor(length/60)
    print(f'Length: {np.round(length, decimals=2)} seconds ({np.floor(length/60):.0f} min {round(length%60, ndigits=1)} sec)')
    print('Sample rate:', samplerate, 'Hz')
    # print(audio)

    # Analysis ----------------------------------
    idx_start = INPUT_TIME * samplerate
    idx_end = (INPUT_TIME + INPUT_DURATION) * samplerate

    audio_slice = audio.T[0,idx_start:idx_end]
    t = np.linspace(0, INPUT_DURATION, len(audio_slice))

    audio_slice_rms =  np.sqrt(np.convolve(audio_slice**2, np.ones(INPUT_RMS)/INPUT_RMS, mode="same"))
    audio_slice_dB = 20 * np.log10(audio_slice_rms)

    print(len(audio_slice))
    print(len(audio_slice_rms))

    below_length, below_idxs = count_below_treshold(audio_slice_dB, min_length=INPUT_MINIMUM_LENGTH*samplerate)
    print(len(below_length))
    print(below_length)
    print(len(below_idxs))
    print(below_idxs)

    add_beep(audio_slice, samplerate, below_idxs, below_length)

    plt.rcParams['figure.constrained_layout.use']=True
    # plt.plot(t, audio_slice_dB)
    fig, axes = plt.subplots(2, sharex=True)
    axes: list[Axes]
    # axes[0].plot(t, audio_slice_dB)
    # axes[0].axhline(input_cutoff, c='r', ls=':')
    axes[0].plot(t, audio_slice_dB<INPUT_THRESHOLD)
    axes[0].yaxis.set_ticks([0,1])
    axes[0].set_xlim(0, INPUT_DURATION)
    axes[1].plot(t, audio_slice_dB)
    axes[1].axhline(INPUT_THRESHOLD, c='r', ls=':')

    for lengh, idx in zip(below_length, below_idxs): # zips -> list containing tuples
        axes[1].axvspan(idx/samplerate, (idx+lengh)/samplerate, color=(1, 0, 0, 0.3))
    plt.show()

def count_below_treshold(data: np.ndarray, threshold=INPUT_THRESHOLD, min_length: float = 0):
    data_below_treshold = data < threshold # find values below treshold
    change_bool = data_below_treshold[1:] != data_below_treshold[:-1] # find bool value changes ('edges')
    change_bool_with_markers = np.concat([[data_below_treshold[0]], change_bool, [data_below_treshold[-1]]]) # add start and end markers for calculating difference in indices; if start value is "False", a null marker is inserted
    # print(len(change_bool_with_markers))
    # print(change_bool_with_markers)
    # print('-----')
    change_bool_idxs = np.flatnonzero(change_bool_with_markers) # returns indices of bool value changes
    change_bool_diff = np.diff(change_bool_idxs) # obtain length of each group of bool values
    
    # removing "False" groups/runs and their corresponding indices
    change_bool_true_len = change_bool_diff[::2]
    change_bool_true_idxs = change_bool_idxs[::2]

    return change_bool_true_len[change_bool_true_len>min_length], change_bool_true_idxs[change_bool_true_len>min_length]

def add_beep(audio_data: np.ndarray, samplerate, beep_idx, beep_length):
    length = len(audio_data) / samplerate
    periods = length * 1000 * 2 * np.pi # number of periods for 1 kHz sound wave over duration of data
    beep = np.sin(np.linspace(0, periods, len(audio_data)))

    mask = np.zeros_like(audio_data)
    for lengh, idx in zip(beep_length, beep_idx):
        mask[range(idx, idx+lengh)] = 1

    audio_output = audio_data + beep * mask
    sf.write("bongo.mp3", audio_output, samplerate)

def audio_split_calc(split_idxs, split_lengths, max_chunk_length, max_chunks):
    # TODO:
    # step 1: is it possible to divide into chunks with specified max length?
    # step 2: score splits after lengths and least number of chunks
    ...

if __name__ == "__main__":
    main()