from scipy import signal
from scipy.io import wavfile


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = signal.lfilter(b, a, data)
    return y


def main():
    wavfile_name = "./static/audio/2020-12-15-08-57-58.wav"
    fs, data = wavfile.read(wavfile_name)

    wavfile.write(
        'hoge.wav',
        fs,
        butter_bandpass_filter(data, 1, 5400, fs, order=6)
    )


if __name__ == "__main__":
    main()
