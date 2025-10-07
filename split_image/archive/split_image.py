import os
import cv2
import numpy as np
from PIL import Image

def split_cards_by_background_difference(input_image_path, output_dir, card_padding=5, min_card_area=5000):
    """
    白い背景に配置された白いカード（アイコンを囲む部分）を検出し、
    個別の画像に分割して保存する関数。

    :param input_image_path: 分割したい元の画像のパス
    :param output_dir: 分割した画像の保存先ディレクトリ
    :param card_padding: 切り出すカード領域の周囲に追加する余白のピクセル数
    :param min_card_area: 検出するカードの最小ピクセル面積。ノイズ除去に利用。
    """
    # 出力先ディレクトリがなければ作成する
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # OpenCVで画像を読み込む (BGR形式)
        img_bgr = cv2.imread(input_image_path)
        if img_bgr is None:
            print(f"エラー: 画像ファイルが読み込めません - {input_image_path}")
            return

        # グレースケールに変換
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # 全体の白い背景とカードの白い背景のわずかな違いを検出するため、
        # Adaptive Thresholdingや、背景除去に近い処理を試みる。
        # または、背景が最も明るい色であると仮定し、そこからわずかに暗い領域（カード）を検出する。
        
        # ここでは、固定閾値で試す（背景255、カードが240-250くらいの想定）
        # 画像によってこの閾値は調整が必要かもしれない
        # まず、背景とカードの境目を強調するために、白い部分を反転させる
        _, thresh_inv = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY_INV) 
        # ↑245より明るい(白い)部分を0(黒)に、それ以外を255(白)にする
        # これにより、背景が黒、カード部分が白になる（アイコンはカード部分に含まれる）

        # ノイズ除去とカードの形状を結合するためのモルフォロジー処理
        kernel = np.ones((5,5),np.uint8) # カーネルサイズはカードの大きさに合わせて調整
        thresh_inv = cv2.morphologyEx(thresh_inv, cv2.MORPH_CLOSE, kernel) # 閉処理
        thresh_inv = cv2.morphologyEx(thresh_inv, cv2.MORPH_OPEN, kernel)  # 開処理

        # 輪郭を検出
        # cv2.RETR_EXTERNAL で一番外側の輪郭のみ検出
        contours, _ = cv2.findContours(thresh_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        card_rects = []
        for cnt in contours:
            # 輪郭の面積が小さすぎるものはノイズとして除外
            if cv2.contourArea(cnt) < min_card_area:
                continue

            # 輪郭を囲む最小の直立矩形を取得 (x, y, w, h)
            x, y, w, h = cv2.boundingRect(cnt)
            card_rects.append((x, y, w, h))

        # カードの矩形をY座標、次にX座標でソートして、左上から順に処理できるようにする
        card_rects.sort(key=lambda r: (r[1], r[0]))

        # PIL形式に変換して切り出す
        img_pil = Image.open(input_image_path)
        img_width, img_height = img_pil.size
        
        count = 0
        for x, y, w, h in card_rects:
            # パディングを追加して切り出す範囲を決定
            x1_padded = max(0, x - card_padding)
            y1_padded = max(0, y - card_padding)
            x2_padded = min(img_width, x + w + card_padding)
            y2_padded = min(img_height, y + h + card_padding)

            # 画像を切り出す
            cropped_img_pil = img_pil.crop((x1_padded, y1_padded, x2_padded, y2_padded))
            
            # 保存するファイル名を設定
            output_filename = os.path.join(output_dir, f"card_icon_{count}.png")
            
            # 画像を保存
            cropped_img_pil.save(output_filename)
            print(f"保存しました: {output_filename}")
            
            count += 1

    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません - {input_image_path}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == '__main__':
    # --- 設定項目 ---
    
    # 1. 元の画像ファイルのパスを指定
    input_image = 'split_image/pic_8bit/Gemini_Generated_Image_7javto7javto7jav.png' 
    
    # 2. 分割した画像の保存先フォルダ名を指定
    output_folder = 'split_image/split_icons'
    
    # 3. 切り出すカード領域の周囲に追加する余白のピクセル数 (調整可能)
    # カードの端からどれくらい余白を持たせて切り出すかを設定
    card_crop_padding = 10 

    # 4. 検出するカードの最小ピクセル面積 (調整可能)
    # 小さすぎるノイズの輪郭を除去するために使用。画像の解像度に合わせて調整してください。
    # 例: 100x100pxのカードなら10000が目安。
    min_card_area_threshold = 5000 

    # --- 処理の実行 ---
    split_cards_by_background_difference(input_image, output_folder, card_crop_padding, min_card_area_threshold)