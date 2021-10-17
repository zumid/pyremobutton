# PyRemoButton

## 説明

ダイソーのリモートシャッター AB Shutter3 をIoTボタンにしよう!

このプログラムの特徴は下記のとおりです。

- 長押し対応
  - 長押しで違うスクリプトを実行可能です。
- 複数のボタンに対応
  - 複数のAB shutterを接続してそれぞれに違うスクリプトの実行が可能です。
- 接続時をトリガー可能
  - AB shutterは電源オンの状態で暫く経つと電源が自動的に切れます。その状態でボタンを押すと電源が入り接続されます。
  - そのため実質２回押さないとトリガーしなかったのですが、１回目（接続時）をトリガー可能にしています。
- iOSボタンとAndroidボタンの区別 (未検証)
  - iOSボタンとAndroidボタンを区別可能・・・にしたつもりですが、自分が持っているデバイスは同じイベントしか返さないため区別できていません。

### 使い方

Bluetoothが使えるRaspberry Pi にAB shutter3を接続
 (Raspberry Pi 3, Raspberry Pi Zero W など)
 
 

#### インストール

'''
git clone https://github.com/zumid/pyremobutton.git 
'''
