from tqdm import tqdm
import numpy as np
from matplotlib import pylab as pl
from scipy.io.wavfile import read


def stft(s, Lf, noverlap=None):
    if noverlap == None:
        noverlap = Lf // 2
    len_s = s.shape[0]
    win = np.hanning(Lf)
    Mf = Lf // 2 + 1
    Nf = int(np.ceil((len_s - noverlap) / (Lf - noverlap))) - 1
    S = np.empty([Mf, Nf], dtype=np.complex128)
    for n in tqdm(range(Nf)):
        S[:, n] = np.fft.rfft(s[(Lf - noverlap) * n:(Lf - noverlap) * n + Lf] * win, n=Lf, axis=0)
    return np.abs(S)


if __name__ == "__main__":
    Lf = 20
    # speed = '0.9999-pitch'
    speed = "neko"
    t = 'short'
    # wavfile = f"./static/audio/2020-12-15-08-57-58-{speed}.wav"
    # wavfile = "./static/audio/吾輩は猫である.wav"
    wavfile = "./static/audio/2021-01-19-02-20-18.wav"
    fs, data = read(wavfile)

    spectrogram = stft(data, Lf)

    np.save("arr.npy", spectrogram)
    # spectrogram = np.load("arr.npy")

    # fig = pl.figure(figsize=(80, 4))
    fig = pl.figure()
    if t == 'short':
        duration = int(12 * fs / (Lf // 2))
        seek = int(1.05 * fs / (Lf // 2))
    else:
        duration = spectrogram.shape[1]
        seek = 0
    d = spectrogram[2, seek:seek + duration]
    x_tick = np.linspace(seek * Lf / (fs * 2), (seek + d.shape[0]) * Lf / (fs * 2), num=d.shape[0])
    pl.stem(x_tick, d, linefmt=":", basefmt=" ")

    pl.xlabel("time[s]")
    pl.ylabel("Power")
    pl.xlim([x_tick[0], x_tick[-1]])
    pl.savefig(f"stft-bpf-{speed}-{t}.jpg")
