# 卒業研究ノート

## 2020年10月6日

面談で研究テーマの候補を聞く。

## 2020年10月7日

研究テーマの希望を提出する。第1希望は案4の「汎用コンピュータを用いた光通信システムの研究」、第2希望は案5の「光ビーム伝搬解析用の大規模フーリエ変換の研究」。

## 2020年10月10日

研究テーマが案4の「汎用コンピュータを用いた光通信システムの研究」に決まる。

## 2020年10月11日

### 環境構築

- Matlabは、以前情報理工学実験でインストールした Matlab R2018aが残っていた。
- Audacityは、新規インストールした。
  ![Audacity 2.4.2](assets/images/2020-10-11-01-46-01.png)

### 音声の入出力する方法について調べた

[PythonでWAVファイルの読み書きを行う](https://docs.python.org/ja/3/library/wave.html)

#### 倍音を足し合わせて正弦波以外の音を作ってみた。
正弦波よりも温かみがある音になった。

<audio controls="controls">
  <source type="audio/mp3" src="assets/audio/overtones.wav"></source>
  <p>https://github.com/Tsutomu-Ikeda/senior-project/blob/main/assets/audio/overtones.wav</p>
</audio>

![](assets/images/overtones.png)

#### 261Hz 329Hz 391Hzの倍音を生成し足し合わせることで、和音を作ってみた
聞いていて心地良い音になった

<audio controls="controls">
  <source type="audio/mp3" src="assets/audio/harmony.wav"></source>
  <p>https://github.com/Tsutomu-Ikeda/senior-project/blob/main/assets/audio/harmony.wav</p>
</audio>

![](assets/images/harmony.png)

## 2020年10月18日

### 画像データをシリアライズして音声に変換する方法について考えてみている

- PythonのPILを使えばJPGやPNGなどの画像フォーマットの違いを気にせずにピクセルの情報を得れそう
- 10Hzの通信で、1つの信号で1bitを送ると考えると、10bit/sの通信速度
- SD画質(640px x 480px)を色深度4bitフルカラーで送る場合、4bit * 3 * 640 * 480 = 3,686,400 bit
- よって通信にかかる時間は 368,640秒 = 約4.2日…
- デモでやるとしたら長くても30秒くらいが良い…？
  - 30秒で送るなら 122,880 bit/s つまり、122kHzの信号にする必要がある。

## 2020年10月20日

### 登校して実験
- 去年の装置が動くか確認した
- 色んな周波数の正弦波、矩形波を生成した
- 結局正弦波を送ることはできなかった

