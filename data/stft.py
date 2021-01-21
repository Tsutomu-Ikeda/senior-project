from tqdm import tqdm
import numpy as np
from matplotlib import pylab as pl
from scipy.io.wavfile import read


def stft(s, Lf, overlap=None):
    if overlap == None:
        overlap = Lf // 2
    len_s = s.shape[0]
    win = np.hanning(Lf)
    Mf = Lf // 2 + 1
    Nf = int(np.ceil((len_s - overlap) / (Lf - overlap))) - 1
    S = np.empty([Mf, Nf], dtype=np.complex128)
    for n in tqdm(range(Nf)):
        S[:, n] = np.fft.rfft(s[(Lf - overlap) * n:(Lf - overlap) * n + Lf] * win, n=Lf, axis=0)
    return np.abs(S)


if __name__ == "__main__":
    Lf = 20
    # wavfile = "./static/audio/2020-12-15-08-57-58.wav"
    # wavfile = "./static/audio/吾輩は猫である.wav"
    wavfile = "./static/audio/2021-01-19-01-52-15.wav"
    fs, data = read(wavfile)

    spectrogram = stft(data, Lf)
    np.save("arr.npy", spectrogram)
    # spectrogram = np.load("arr.npy")

    fig = pl.figure()
    seek = int(1.2 * fs / (Lf // 2))
    duration = int(0.1 * fs / (Lf // 2))
    d = spectrogram[:, seek:seek + duration]
    x_tick = np.linspace(seek * Lf / (fs * 2), (seek + d.shape[1]) * Lf / (fs * 2), num=d.shape[1])
    y_tick = np.linspace(0, fs / 2, num=d.shape[0])
    pl.pcolormesh(x_tick, y_tick, d, shading='nearest', cmap='OrRd')
    pl.imsave('heatmap.png', spectrogram, cmap='OrRd')

    pl.xlabel("time[s]")
    pl.ylabel("frequency[Hz]")
    pl.xlim([x_tick[0], x_tick[-1]])
    pl.ylim([0, 10000])
    pl.savefig("stft.png")
