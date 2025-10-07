import os
from PIL import Image

def split_image_grid(input_image_path, output_dir, rows, cols):
    """
    グリッド状の画像を個別の画像に分割して保存する関数

    :param input_image_path: 分割したい元の画像のパス
    :param output_dir: 分割した画像の保存先ディレクトリ
    :param rows: グリッドの行数
    :param cols: グリッドの列数
    """
    # 出力先ディレクトリがなければ作成する
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # 画像を開く
        with Image.open(input_image_path) as img:
            # 画像の全体の幅と高さを取得
            width, height = img.size
            
            # 1枚あたりの画像の幅と高さを計算
            single_width = width // cols
            single_height = height // rows
            
            count = 0
            # 行と列の数だけループして画像を切り出す
            for i in range(rows):
                for j in range(cols):
                    # 切り出す範囲を計算 (left, top, right, bottom)
                    left = j * single_width
                    top = i * single_height
                    right = left + single_width
                    bottom = top + single_height
                    
                    # 指定した範囲で画像を切り出す
                    cropped_img = img.crop((left, top, right, bottom))
                    
                    # 保存するファイル名を設定
                    output_filename = os.path.join(output_dir, f"icon_{count}.png")
                    
                    # 画像を保存
                    cropped_img.save(output_filename)
                    print(f"保存しました: {output_filename}")
                    
                    count += 1
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません - {input_image_path}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == '__main__':
    # --- 設定項目 ---
    
    # 1. 元の画像ファイルのパスを指定
    # 例: 'generated_image.png'
    input_image = 'split_image/pic_8bit/Gemini_Generated_Image_7javto7javto7jav.png' 
    
    # 2. 分割した画像の保存先フォルダ名を指定
    output_folder = 'split_image/split_icons'
    
    # 3. グリッドの分割数を指定 (今回は縦3枚, 横2枚なので 3行, 2列)
    grid_rows = 3
    grid_cols = 2

    # --- 処理の実行 ---
    split_image_grid(input_image, output_folder, grid_rows, grid_cols)