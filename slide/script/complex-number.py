from mpl_toolkits.axisartist.axislines import SubplotZero
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.size'] = 12
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meirio', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
linewidth = 2

fig = plt.figure(figsize=(6, 6))
ax = SubplotZero(fig, 111)
fig.add_subplot(ax)

for direction in ["xzero", "yzero"]:
    ax.axis[direction].set_axisline_style("-|>", size=2)
    print(ax.axis[direction].get_axisline_style().__dir__())
    ax.axis[direction].set_visible(True)

for direction in ["left", "right", "bottom", "top"]:
    ax.axis[direction].set_visible(False)


def plot_circle(radius):
    theta = np.linspace(0, 2 * np.pi, 3600)

    x = radius * np.cos(theta)
    y = radius * np.sin(theta)

    plt.plot(
        x,
        y,
        linestyle="dotted",
        color="gray",
        linewidth=linewidth
    )


def plot_line(x, y):
    np_x = np.linspace(0, x, 100)
    np_y = np.linspace(0, y, 100)

    plt.plot(
        np_x,
        np_y,
        linestyle="dashed",
        color="gray",
        linewidth=linewidth
    )


def plot_xline(x, y):
    plt.text(x - 0.8, 0.2, x)

    np_x = np.linspace(x, x, 100)
    np_y = np.linspace(0, y, 100)

    plt.plot(
        np_x,
        np_y,
        linestyle="dotted",
        color="gray",
        linewidth=linewidth
    )


def plot_yline(x, y):
    plt.text(-3, y - 0.2, y)
    np_x = np.linspace(0, x, 100)
    np_y = np.linspace(y, y, 100)

    plt.plot(
        np_x,
        np_y,
        linestyle="dotted",
        color="gray",
        linewidth=linewidth
    )


def plot_arch(radius=2):
    theta = np.linspace(0, -np.pi / 5, 360)

    x = radius * np.cos(theta)
    y = radius * np.sin(theta)

    plt.plot(
        x,
        y,
        color="black",
        linewidth=linewidth
    )


point = (8.090, -5.878)


plt.text(12 - 0.8, 0.4, "実軸")
plt.text(-2, 12 - 0.2, "虚軸")
plt.text(2, -1.2, "36°")
plot_circle(10)
plot_arch()
plot_line(*point)
plot_xline(*point)
plot_yline(*point)

plt.scatter(
    [point[0]],
    [point[1]],
)

plt.xlim([-12, 12])
plt.ylim([-12, 12])

plt.savefig('../assets/images/complex-number.png')
