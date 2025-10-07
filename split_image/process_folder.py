import os
import glob
import cv2
import numpy as np
from PIL import Image

def split_cards_by_layout(input_image_path, output_dir):
    """
    画像のレイアウトを解析し、全てのカードを同じサイズで分割する関数。
    (この関数自体に変更はありません)
    """
    # 出力先ディレクトリがなければ作成する
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"作成しました: {output_dir}")

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

        # 検出した輪郭からカードのバウンディングボックスを取得
        bounding_boxes = []
        for cnt in contours:
            if cv2.contourArea(cnt) > 1000:
                bounding_boxes.append(cv2.boundingRect(cnt))

        if len(bounding_boxes) != 6:
            print(f"警告: {os.path.basename(input_image_path)} から6枚のカードを検出できませんでした。検出数: {len(bounding_boxes)}。スキップします。")
            return

        # 平均サイズを計算
        avg_w = int(np.mean([box[2] for box in bounding_boxes]))
        avg_h = int(np.mean([box[3] for box in bounding_boxes]))

        # 位置でソート
        bounding_boxes.sort(key=lambda r: (r[1], r[0]))

        # PILで再度画像を開いて切り出し
        img_pil = Image.open(input_image_path)
        
        for i, box in enumerate(bounding_boxes):
            center_x = box[0] + box[2] // 2
            center_y = box[1] + box[3] // 2
            x1 = center_x - avg_w // 2
            y1 = center_y - avg_h // 2
            x2 = center_x + avg_w // 2
            y2 = center_y + avg_h // 2
            
            cropped_img = img_pil.crop((x1, y1, x2, y2))
            output_filename = os.path.join(output_dir, f"uniform_card_{i}.png")
            cropped_img.save(output_filename)
        
        print(f"完了: {os.path.basename(input_image_path)} を6枚に分割しました。")

    except Exception as e:
        print(f"エラーが発生しました ({os.path.basename(input_image_path)}): {e}")

if __name__ == '__main__':
    # --- 設定項目 ---
    
    # 1. 処理したい画像が入っているフォルダのパスを指定
    input_dir = 'split_image/pic_8bit'
    
    # 2. 分割した画像の保存先となるベースフォルダを指定
    base_output_dir = 'split_image/split_uniform_cards'
    
    # --- 処理の実行 ---

    # 入力フォルダが存在するかチェック
    if not os.path.isdir(input_dir):
        print(f"エラー: 入力フォルダが見つかりません - {input_dir}")
    else:
        # 対応する画像形式（png, jpg, jpeg）のリストを取得
        image_extensions = ('*.png', '*.jpg', '*.jpeg')
        image_files = []
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(input_dir, ext)))

        print(f"{len(image_files)}個の画像ファイルを検出しました。処理を開始します...")

        # 各画像ファイルに対してループ処理
        for image_path in image_files:
            # 出力先のサブフォルダ名を作成（元のファイル名から拡張子を除いたもの）
            filename_without_ext = os.path.splitext(os.path.basename(image_path))[0]
            output_subdir = os.path.join(base_output_dir, filename_without_ext)
            
            # 分割処理関数を呼び出し
            split_cards_by_layout(image_path, output_subdir)
        
        print("\n全ての処理が完了しました。")