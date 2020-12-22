"""
This script is used to estimate impulse response in a room the recording was taking place in.

The function responsible for that is  dereverberate
It takes two arguments:
    wave - 1-D ndarray of wave samples
    fs - sampling frequency (int or float)

Copyright to:
    Katarzyna Augustyn
    Dominika Godzisz
    Bartłomiej Piekarz
"""
import numpy as np
import scipy as sp
import pickle

from read_impulse_response import compute_stft
from parameterization import STFT


def dereverberate(wave, fs, expected_response_path="real_impulse_responses/rir_medium.p", preloaded=True):
    """
    Estimates the impulse response in a room the recording took place

    :param wave: 1-D ndarray of wave samples
    :param fs: sampling frequency (int or float)
    :param expected_response_path: path to a file containing expected impulse response (default: rir_medium.p)
    :param preloaded: is the response preloaded (default: True)
    :returns: (h_rir) 1-D ndarray of the impulse response,
              (wave_dry) 1-D ndarray of the dry signal,
              (wave_wet) 1-D ndarray of the wet signal
    """
    # =========== Reference impulse response ===========
    if preloaded:
        with open(expected_response_path, "rb") as f:
            ref_imp = pickle.load(f)

        win_len = ref_imp["window_length"]
        win_ovlap = ref_imp["overlap"]
        nfft = ref_imp["nfft"]
        blocks = ref_imp["blocks"]
        imp_stft = ref_imp["stft"]
    else:
        win_len = 1024
        win_ovlap = 512
        nfft = 1024
        blocks = 400
        imp_stft = compute_stft(expected_response_path, win_len, win_ovlap, nfft, blocks)

    # =================== Signal stft ==================
    window = np.hanning(win_len)
    sig_stft = STFT(wave, window, win_ovlap, nfft)

    # ==================== Constants ===================
    # window step / hop
    win_step = win_len - win_ovlap

    # minimum gain per frequency
    min_gain = np.zeros(nfft)

    # maximum impulse response estimate
    max_h = imp_stft
    # max_h = np.ones((blocks, nfft)) * 0.9

    # bias used to keep magnitudes from getting stuck on a wrong minimum
    bias = np.ones((blocks, nfft)) * 1.01

    # alpha and gamma - smoothing factors for impulse response magnitude and gain
    alpha = np.ones((blocks, nfft)) * 0.2
    gamma = np.ones(nfft) * 0.3

    # ==================== Algorithm ===================
    # dry_stft and wet_stft are the estimated dry and reverberant signals in frequency-time domain
    dry_stft = np.zeros((blocks, nfft))
    wet_stft = np.zeros((blocks, nfft))

    # h_stft is the estimated impulse response in frequency-time domain
    h_stft = max_h / 2
    # h_stft = np.zeros((blocks, nfft))

    # raw_frames and dry_frames are matrices to keep the information of currently estimated raw and dry signal
    raw_frames = np.ones((blocks, nfft))
    dry_frames = np.zeros((blocks, nfft))

    # C is a matrix to keep the raw estimated powers of the impulse response
    c = np.zeros((blocks, nfft))

    # gain_dry and gain_wet are the frequency gains of the dry and wet signals
    gain_dry = np.ones(nfft)
    gain_wet = np.zeros(nfft)


    h_rir = np.zeros(blocks)
    wave_dry = np.zeros(wave.shape)
    wave_wet = np.zeros(wave.shape)

    return h_rir, wave_dry, wave_wet
