import soundfile as sf
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np

# User input
INPUT_TIME = 6*60+5 # seconds
INPUT_DURATION = 16 # seconds
INPUT_RMS = 500     # samples - for calculating moving average
INPUT_THRESHOLD = -60  # dB
INPUT_MINIMUM_LENGTH = 1/10 # seconds

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
    change_bool_with_markers = np.concat([[data_below_treshold[0]], change_bool, [data_below_treshold[-1]]]) # add start and end markers for calculating difference in indices; if start value is false, null marker is inserted
    # print(len(change_bool_with_markers))
    # print(change_bool_with_markers)
    # print('-----')
    change_bool_idxs = np.flatnonzero(change_bool_with_markers) # returns indices of bool value changes
    change_bool_diff = np.diff(change_bool_idxs) # obtain length of each group of bool values
    
    # removing false groups/runs and corresponding indices
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