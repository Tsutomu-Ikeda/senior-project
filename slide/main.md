---
marp: true
paginate: true
html: true
style: |
  header {
    font-size: 32px;
    color: #999;
    font-weight: 600;
  }
  section h1 {
    color: #333;
    font-weight: 500;
  }
  img[alt~="center"] {
    display: block;
    margin: 0 auto;
  }
  div {
    text-align: center;
  }
  .toc {
    text-align: left;
    margin: auto 0px;
  }
  .toc div {
    width: 100%;
    margin: 10px 0;
  }
  .toc div h2 {
    float: left;
  }
  .toc div h2:first-child {
    text-align: left;
    width: 60%;
  }
  .toc div h2:nth-child(2) {
    text-align: right;
    width: 20%;
  }
  section::after {
    content: attr(data-marpit-pagination) ' / ' attr(data-marpit-pagination-total) ' ページ';
  }
  section.title {
    justify-content: center;
    text-align: center;
  }
  section.wide-margin-list li{
    margin-bottom: 1.5em;
  }
  section.contents {
    justify-content: start;
  }
  section.contents::before {
    content: '';
    display:block;
    padding-top:10px;
  }
  figure {
    margin: 0;
  }
  figure p {
    margin: 0;
  }
  .image-with-border img {
    border: solid 1px #000;
  }
  ul {
    margin: 0;
  }
  figcaption {
    font-weight: 500;
    font-size: 0.8em;
  }
  table{
    border-collapse: collapse;
    margin: 0 auto;
    display: table;
    width: auto;
  }
  th {
    color: #fff;
    padding: 5px;
    background: #333;
    font-weight: bold;
    line-height: 120%;
    text-align: center;
  }

  th:nth-child(n + 2) {
    border-left: 1px solid #fff;
  }

  th:last-child {
    border-right: 1px solid #333;
  }
---
<!--
class: title
_paginate: skip
-->

# 可搬性に優れた光通信デモシステムの研究

<span style="text-align: right; width: 800px; margin: 0 auto;">

A1778594 池田 力
指導教員 高橋 浩

</span>

---
<!--
_header: 本日の流れ
footer: 可搬性に優れた光通信デモシステムの研究
class: contents
-->

<div class="toc">

<div>
<h2>
研究のモチベーション
</h2>
<h2 style="text-align: right; width: 20%;float: left;">
1分
</h2>
</div>

<div>
<h2>
デモシステムの概要
</h2>
<h2>
2分
</h2>
</div>

<div>
<h2>
直面した課題とその解決手法
</h2>
<h2>
8分
</h2>
</div>

<div>
<h2>
実験結果の紹介
</h2>
<h2>
3分
</h2>
</div>

<div>
<h2>
まとめ
</h2>
<h2>
1分
</h2>
</div>

</div>

---
<!--
_header: 研究のモチベーション
-->

## 「光ファイバー」という単語を説明できる人は多くない

<div>
<figure>

![w:450 center](./assets/images/fiber-pie.png)

<figcaption style="font-size: 0.6em">
あなたは光ファイバーについて知っています/説明できますか？<br>
N=34、アンケート形式: Twitter
</figcaption>
</figure>
</div>

---
<!--
_header: デモシステムの概要
-->
## 以下の手順で光ファイバー通信を再現している
- 送信側ソフトウェアで送信するデータを音声データへ変換する
- 送信側回路で変調信号でLEDを明滅させる
- 受信側回路で光信号を電気信号へ変換する
- 受信側ソフトウェアで元のデータを復元する

![w:750 center](./assets/images/demo-system.png)

---
<!--
_header: デモシステムの概要
-->
## 変調方式について
- サブキャリアによる副搬送波周波数$4{,}800\rm{Hz}$、変調周波数$4{,}800\rm{Hz}$となった

### サブキャリアを採用した理由
- 高周波成分を含まないようにするため
- 同じ信号が連続したときに信号が不安定になる現象を回避するため

<div>
<figure>

![w:800 center](./assets/images/2020-11-09-16-44-29.png)

<figcaption>
同じ信号が連続し、信号が不安定になる例
</figcaption>
</figure>
</div>

---
<!--
_header: 直面した課題とその解決手法
-->

## 受信波形からデータを復元するにあたり、以下のような問題が発生した

- 0Vの位置がずれてしまう
- 上下対称とは限らない
- 最大振幅のブレが大きい
- サンプル落ちが発生する場合がある

<div style="display: flex; justify-content: center; align-items: center;">

<figure>

![w:350 center](./assets/images/stft-raw-wave.png)

<figcaption>
受信波形の例
</figcaption>
</figure>
<figure>

![w:350 center](./assets/images/sample-drop.png)

<figcaption>
サンプル落ちの例
</figcaption>
</figure>
</div>

---
<!--
_header: 直面した課題とその解決手法
-->

## 短時間フーリエ変換による特定周波数の抽出

短時間フーリエ変換を用いることで不安定な波形が扱いやすくなった

<div style="display: flex; justify-content: center; align-items: center;">

<figure>

![w:350 center](./assets/images/stft-freq-time.png)

<figcaption>
周波数強度の時間変化
</figcaption>
</figure>

<figure>

![w:350 center](./assets/images/stft-analysis.png)

<figcaption>

$3{,}900\rm{Hz}$ - $5{,}700\rm{Hz}$ の<br>周波数強度の合計

</figcaption>
</figure>
</div>

---
<!--
_header: 直面した課題とその解決手法
-->

## それだけの工夫では大きいサイズのデータを復号できなかった

### 全体40KBのうち、3KB程度を伝送した時点でファイルが壊れてしまった

<div style="display: flex; justify-content: center; align-items: center;">

<figure>

![w:350 center](./assets/images/doraemon-original.jpeg)

<figcaption>
オリジナルの画像
</figcaption>
</figure>

<figure>

![w:350 center](./assets/images/dora-2-10-5.jpg)

<figcaption>
復元された画像
</figcaption>
</figure>
</div>

---
<!--
_header: 直面した課題とその解決手法
-->

## 大きいサイズのデータを復元できない理由
徐々に位相がずれていき、`0`・`1`の境界が近づいていくという現象が発生したから

<div>
<figure>

![w:450 center](./assets/images/phase-slipping.jpg)

<figcaption>
位相がずれ、境界が近づいて行く様子
</figcaption>
</figure>
</div>

---
<!--
_header: 直面した課題とその解決手法
-->

## 短時間フーリエ変換による位相の同期

フーリエ変換の複素数の偏角を求めることで、位相のずれを計算できる

<div>
<figure>

<div style="display: flex; justify-content: center; align-items: center;">

![](./assets/images/phase.png)

![](assets/images/fft.png)

</div>

<figcaption>
フーリエ変換による位相算出のイメージ
</figcaption>
</figure>
</div>

---
<!--
_header: 実験結果の紹介
-->

## 実験用に3種類のデータを用意した

<div style="display: flex; justify-content: center; align-items: center;">

<figure style="width: 800px; padding: 3%">

<div style="font-size: 0.55em;text-align: left;">

吾輩は猫である。名前はまだ無い。
どこで生れたかとんと見当がつかぬ。何でも薄暗いじめじめした所でニャーニャー泣いていた事だけは記憶している。吾輩はここで始めて人間というものを見た。しかもあとで聞くとそれは書生という人間中で一番獰悪な種族であったそうだ。この書生というのは時々我々を捕えて煮て食うという話である。しかしその当時は何という考もなかったから別段恐しいとも思わなかった。ただ彼の掌に載せられてスーと持ち上げられた時何だかフワフワした感じがあったばかりである。掌の上で少し落ちついて書生の顔を見たのがいわゆる人間というものの見始であろう
</div>

<figcaption>
テキストデータ<br>
夏目漱石『吾輩は猫である』の冒頭 (815B)
</figcaption>
</figure>

<figure class="image-with-border">

![](./assets/images/A.jpeg)

<figcaption>
軽量画像 (4.08KB)
</figcaption>
</figure>

<figure class="image-with-border">

![](./assets/images/doraemon-large.jpeg)

<figcaption>
大容量画像 (34.6KB)
</figcaption>
</figure>
</div>



---
<!--
_header: 実験結果の紹介
-->

## 実験結果

<div>
<figure>
<figcaption>
10回ずつデータを送った際の成否と送信時間
</figcaption>

| 種類       | サイズ | 試行回数 | 成功回数 | 伝送にかかった時間 |
| ---------- | -----: | -------: | -------: | -----------------: |
| テキスト   |   815B |     10回 |     10回 |                1秒 |
| 軽量画像   | 4.08KB |     10回 |      9回 |              5.2秒 |
| 大容量画像 | 34.6KB |     10回 |     10回 |               39秒 |

</figure>
</div>

---
<!--
_header: まとめ
-->

## 可搬性に優れた光通信デモシステムの研究

- 通信用途を想定していないデバイスを用いて安定的な通信システムを作るには多くの困難が伴った
- 変調方式を工夫したり、短時間フーリエ変換といった手法を用いたりすることで、可搬性と安定性を両立したデモシステムを構築することができた
- 実験においても基本的な動作確認で高い安定性を確認することができ、完成度が高いデモシステムを作ることができたと言える
