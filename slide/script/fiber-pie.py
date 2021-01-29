import matplotlib.pyplot as plt

plt.rcParams['font.size'] = 16
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meirio', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']

fig = plt.figure(figsize=(12, 6))

ratios = [8, 21, 5]
labels = ['知っていて説明できる', '知っているが説明できない', '知らない']
explode = [0, 0, 0]
colors = ['#777', '#cc2b2b', '#d16666']

_, _, autotexts = plt.pie(
    ratios,
    autopct='%1.1f%%',
    startangle=90,
    labels=labels,
    explode=explode,
    colors=colors,
    textprops={'weight': "bold"},
    counterclock=False,
)

for text in autotexts:
    text.set_color('white')

plt.savefig('../assets/images/fiber-pie.png')
