# ImgProcKit - 画像分割ツール

`ImgProcKit` は、特定のレイアウトで配置された複数の画像を1枚ずつに自動で分割するためのPythonスクリプト集です。

このツールは、神経衰弱カードのアイコンセットのように、1枚の画像内にグリッド状に配置された複数の要素を、それぞれ個別のファイルとして正確に切り出すことを目的として開発されました。

![サンプル画像](https://samurai-human-go.com/picture/etc_computer_8bit.png)
---

## ✨ 主な機能

- **レイアウト自動解析**: 画像内の各要素（カード）の位置を自動検出し、そのレイアウトを解析します。
- **均一サイズでの分割**: 全ての分割後画像が完全に同じサイズになるように、計算された平均サイズを基に切り出しを行います。
- **一括処理**: 指定したフォルダ内の全ての画像（PNG, JPG）を一度に処理し、元のファイル名ごとのサブフォルダに整理して保存します。

---

## ⚙️ 動作要件

このスクリプトは、以下のPythonライブラリに依存しています。

- `Pillow`
- `OpenCV-Python`
- `NumPy`

`pyproject.toml` に記載の通り、これらのライブラリが必要です。

---

## 🚀 使い方

1.  **リポジトリのクローンまたはダウンロード**
    ```bash
    git clone [https://github.com/git-756/ImgProcKit.git](https://github.com/git-756/ImgProcKit.git)
    cd ImgProcKit
    ```

2.  **画像の準備**
    - 分割したい画像ファイルを、`split_image/pic_8bit` フォルダ（または任意のフォルダ）に配置します。

3.  **スクリプトの編集**
    - `split_image/process_folder.py` を開き、以下の2つの変数を自分の環境に合わせて設定します。

    ```python
    # --- 設定項目 ---

    # 1. 処理したい画像が入っているフォルダのパスを指定
    input_dir = 'split_image/pic_8bit'

    # 2. 分割した画像の保存先となるベースフォルダを指定
    base_output_dir = 'split_image/split_uniform_cards'
    ```

4.  **スクリプトの実行**
    - ターミナルで以下のコマンドを実行します。

    ```bash
    python split_image/process_folder.py
    ```

5.  **結果の確認**
    - 処理が完了すると、`base_output_dir` で指定したフォルダ内に、元の画像ファイル名のサブフォルダが作成され、その中に6枚の画像が分割されて保存されます。

---

## 📜 ライセンス

このプロジェクトは **MIT License** のもとで公開されています。ライセンスの全文については、[LICENSE](LICENSE) ファイルをご覧ください。

また、このプロジェクトはサードパーティ製のライブラリを利用しています。これらのライブラリのライセンス情報については、[NOTICE.md](NOTICE.md) ファイルに記載しています。

## 作成者
[Samurai-Human-Go](mailto:gotechsamurai@samurai-human-go.com)

**ブログ記事**: [単なる画像分割じゃない！位置解析で均一なカード画像を切り出すスクリプト開発記](https://samurai-human-go.com/python-opencv-image-slicing-logic/)