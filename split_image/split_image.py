import os
import cv2
import numpy as np
from PIL import Image

def split_image_by_content(input_image_path, output_dir, padding=10):
    """
    画像の内容（オブジェクト）を検出して、個別の画像に分割する関数

    :param input_image_path: 分割したい元の画像のパス
    :param output_dir: 分割した画像の保存先ディレクトリ
    :param padding: 切り出す領域の周囲に追加する余白のピクセル数
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

        # 白い背景の画像を想定し、閾値処理でオブジェクトを強調 (背景を白、オブジェクトを黒にする)
        # 背景が完全に白でない可能性を考慮し、閾値は240など少し低めに設定
        _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        
        # オブジェクトが小さい場合や、線が細い場合に備えて膨張処理 (オプション)
        # kernel = np.ones((3,3),np.uint8)
        # thresh = cv2.dilate(thresh,kernel,iterations = 1)

        # 輪郭を検出
        # cv2.findContoursはPython 3では(contours, hierarchy)を返す
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 検出された輪郭からバウンディングボックスを取得し、結合処理を行う
        rects = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            # 小さすぎるノイズを除去 (例: 幅または高さが小さすぎる場合)
            if w > 20 and h > 20: # 閾値は画像によって調整してください
                rects.append((x, y, x + w, y + h)) # (x1, y1, x2, y2)形式で保存

        # 重複する、または近接するバウンディングボックスを結合する
        # この処理は、1つのアイコンが複数の小さな輪郭に分かれている場合などに有効
        # ここでは簡単な重複チェックを行うが、より高度な結合にはNMS (Non-Maximum Suppression) などが必要な場合もある
        merged_rects = []
        if rects:
            rects.sort(key=lambda r: (r[1], r[0])) # Y座標、X座標でソート
            
            current_rect = list(rects[0]) # (x1, y1, x2, y2)
            for i in range(1, len(rects)):
                next_rect = rects[i]
                
                # 少し重なっている、または近接しているかを判定 (閾値は調整可能)
                # min_overlap_x = max(0, min(current_rect[2], next_rect[2]) - max(current_rect[0], next_rect[0]))
                # min_overlap_y = max(0, min(current_rect[3], next_rect[3]) - max(current_rect[1], next_rect[1]))

                # ここでは単純に次の矩形が現在の矩形に完全に含まれている、
                # あるいは非常に近い場合に結合を試みる
                # より堅牢な結合ロジックが必要な場合は、IoU (Intersection over Union) などを利用
                
                # 次の矩形が現在の矩形とY座標が近い、またはX座標で重なっている場合
                # 結合ロジックをよりシンプルにするため、ここではY座標が近いもの同士をグループ化し、
                # その中でX座標が近いものを結合することを想定
                
                # 簡単な結合ロジック:
                # current_rectとnext_rectが水平方向または垂直方向に隣接しているかをチェック
                # 具体的な数値ではなく、アイコンの間隔を見て調整する
                
                # 結合のしきい値 (例: 20ピクセル以内にあれば結合)
                overlap_threshold = 20
                
                # X軸方向の結合条件 (重なりがあるか、または非常に近いか)
                x_overlap = max(0, min(current_rect[2], next_rect[2]) - max(current_rect[0], next_rect[0]))
                
                # Y軸方向の結合条件 (重なりがあるか、または非常に近いか)
                y_overlap = max(0, min(current_rect[3], next_rect[3]) - max(current_rect[1], next_rect[1]))

                # どちらかの軸で重なりがあり、もう一方の軸で非常に近い、または重なりがある場合
                if (x_overlap > -overlap_threshold and # X軸で重なりまたは非常に近い
                    y_overlap > -overlap_threshold):   # Y軸で重なりまたは非常に近い
                    
                    # 結合して新しいバウンディングボックスを更新
                    current_rect[0] = min(current_rect[0], next_rect[0])
                    current_rect[1] = min(current_rect[1], next_rect[1])
                    current_rect[2] = max(current_rect[2], next_rect[2])
                    current_rect[3] = max(current_rect[3], next_rect[3])
                else:
                    merged_rects.append(tuple(current_rect))
                    current_rect = list(next_rect)
            merged_rects.append(tuple(current_rect)) # 最後の矩形を追加

        # 最終的な矩形をフィルタリング (重複を完全に除去するため、NMSのようなアルゴリズムが必要になる場合がある)
        # ここでは単純に、検出された領域を並べ替えて、大きな重複を避けることを試みる
        # より堅牢な実装には、グループ化やNMSが適している
        
        # 簡易的な重複除去とソート
        final_rects = []
        for r_new in merged_rects:
            is_new = True
            for r_existing in final_rects:
                # 既存の矩形が新しい矩形を包含しているか、またはその逆かをチェック
                if (r_new[0] >= r_existing[0] and r_new[1] >= r_existing[1] and
                    r_new[2] <= r_existing[2] and r_new[3] <= r_existing[3]):
                    is_new = False # 新しい矩形は既存の矩形に含まれる
                    break
                elif (r_existing[0] >= r_new[0] and r_existing[1] >= r_new[1] and
                      r_existing[2] <= r_new[2] and r_existing[3] <= r_new[3]):
                    # 既存の矩形が新しい矩形に含まれる場合は、既存のものを置き換える
                    final_rects.remove(r_existing)
                    final_rects.append(r_new)
                    is_new = False
                    break
            if is_new:
                final_rects.append(r_new)
        
        # Y座標とX座標でソートして、アイコンの並び順を保つ
        final_rects.sort(key=lambda r: (r[1], r[0]))

        # PIL形式に変換して切り出す
        img_pil = Image.open(input_image_path)
        img_width, img_height = img_pil.size
        
        count = 0
        for x1, y1, x2, y2 in final_rects:
            # パディングを追加
            x1_padded = max(0, x1 - padding)
            y1_padded = max(0, y1 - padding)
            x2_padded = min(img_width, x2 + padding)
            y2_padded = min(img_height, y2 + padding)

            # 画像を切り出す
            cropped_img_pil = img_pil.crop((x1_padded, y1_padded, x2_padded, y2_padded))
            
            # 保存するファイル名を設定
            output_filename = os.path.join(output_dir, f"icon_{count}.png")
            
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
    
    # 3. 切り出す領域の周囲に追加する余白のピクセル数 (調整可能)
    # 値を大きくすると、切り出されるアイコンの周囲の余白が大きくなります
    crop_padding = 10 

    # --- 処理の実行 ---
    split_image_by_content(input_image, output_folder, crop_padding)