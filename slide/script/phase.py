import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure(figsize=(8, 4))

x = np.linspace(0, 2 * np.pi * 2, 500)
x2 = np.linspace(0, 2 * np.pi * 2, 21)
y1 = np.cos(x)
y2 = np.cos(x2 - np.pi / 5)
y3 = np.cos(x2)

plt.plot(
    x,
    y1,
    linestyle="dotted",
    color="gray"
)


plt.scatter(
    x2,
    y2,
)

plt.scatter(
    x2,
    y3,
    marker='x',
)

plt.xlim([x[0], x[-1]])
plt.xticks(color="None")
plt.tick_params(length=0)

plt.savefig('../assets/images/phase.png')

print(
    np.fft.rfft(y2, n=20, axis=0)
)
