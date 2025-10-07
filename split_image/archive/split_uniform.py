import os
import cv2
import numpy as np
from PIL import Image

def split_cards_by_layout(input_image_path, output_dir):
    """
    画像のレイアウトを解析し、全てのカードを同じサイズで分割する関数。

    :param input_image_path: 分割したい元の画像のパス
    :param output_dir: 分割した画像の保存先ディレクトリ
    """
    # 出力先ディレクトリがなければ作成する
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # OpenCVで画像を読み込む
        img_bgr = cv2.imread(input_image_path)
        if img_bgr is None:
            print(f"エラー: 画像ファイルが読み込めません - {input_image_path}")
            return

        # グレースケールに変換し、閾値処理でカード部分を抽出
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        _, thresh_inv = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY_INV)

        # 輪郭を検出
        contours, _ = cv2.findContours(thresh_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 検出した輪郭からカードのバウンディングボックス（位置とサイズ）を取得
        bounding_boxes = []
        for cnt in contours:
            # 小さすぎるノイズは除去
            if cv2.contourArea(cnt) > 1000:
                bounding_boxes.append(cv2.boundingRect(cnt))

        # 6枚のカードが検出できなかった場合はエラー
        if len(bounding_boxes) != 6:
            print(f"エラー: 6枚のカードを検出できませんでした。検出数: {len(bounding_boxes)}")
            print("スクリプト内の 'cv2.threshold' の閾値(245)を調整してみてください。")
            return

        # --- ここからが新しいアプローチ ---

        # 1. 全てのカードの平均サイズを計算する
        avg_w = int(np.mean([box[2] for box in bounding_boxes]))
        avg_h = int(np.mean([box[3] for box in bounding_boxes]))
        print(f"カードの平均サイズを計算しました: 幅 {avg_w}px, 高さ {avg_h}px")

        # 2. カードを位置でソートする (上から下へ、次に左から右へ)
        bounding_boxes.sort(key=lambda r: (r[1], r[0]))

        # 3. 各カードの中心点を基準に、均等なサイズで切り出す
        img_pil = Image.open(input_image_path)
        
        for i, box in enumerate(bounding_boxes):
            # 検出したバウンディングボックスの中心点を計算
            center_x = box[0] + box[2] // 2
            center_y = box[1] + box[3] // 2

            # 平均サイズを使って切り出し範囲を再計算
            # これにより、全ての切り出しサイズが統一される
            x1 = center_x - avg_w // 2
            y1 = center_y - avg_h // 2
            x2 = center_x + avg_w // 2
            y2 = center_y + avg_h // 2
            
            # Pillowのcropメソッドで切り出し
            cropped_img = img_pil.crop((x1, y1, x2, y2))
            
            # 保存
            output_filename = os.path.join(output_dir, f"uniform_card_{i}.png")
            cropped_img.save(output_filename)
            print(f"保存しました: {output_filename} (サイズ: {cropped_img.size})")

    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません - {input_image_path}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == '__main__':
    # --- 設定項目 ---
    
    # 1. 元の画像ファイルのパスを指定
    input_image = 'split_image/pic_8bit/Gemini_Generated_Image_7javto7javto7jav.png' 
    
    # 2. 分割した画像の保存先フォルダ名を指定
    output_folder = 'split_image/plit_uniform_cards'    
    # --- 処理の実行 ---
    split_cards_by_layout(input_image, output_folder)