import numpy as np
from matplotlib import pylab as pl
from scipy.io.wavfile import read


if __name__ == "__main__":
    wavfile = "./static/audio/2020-12-15-08-57-58.wav"
    fs, data = read(wavfile)

    fig = pl.figure()
    seek = int(0.9 * fs)
    duration = int(0.05 * fs)
    d = data[seek:seek + duration]
    x_tick = np.linspace(seek / fs, (seek + d.shape[0]) / fs, num=d.shape[0])
    pl.plot(x_tick, d)

    pl.xlabel("time[s]")
    pl.ylabel("")
    pl.xlim([x_tick[0], x_tick[-1]])
    pl.ylim([-32768, 32767])
    pl.savefig("time-slice.png")
