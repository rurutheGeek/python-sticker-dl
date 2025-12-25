# -*- coding: utf-8 -*-
import os
import re
import shutil
import argparse
import requests
import zipfile
from bs4 import BeautifulSoup

# --- URLテンプレート ---
DOWNLOAD_URLS = {
    "sticker_normal": "http://dl.stickershop.line.naver.jp/products/0/0/1/{id}/iphone/stickers@2x.zip",
    "sticker_message": "https://stickershop.line-scdn.net/stickershop/v1/product/{id}/iphone/sticker_name_base@2x.zip",
    "sticker_moving": "http://dl.stickershop.line.naver.jp/products/0/0/1/{id}/iphone/stickerpack@2x.zip",
    "emoji_normal": "http://dl.stickershop.line.naver.jp/sticonshop/v1/{id}/sticon/iphone/package.zip?v=1",
    "emoji_moving": "https://stickershop.line-scdn.net/sticonshop/v1/{id}/sticon/iphone/package_animation.zip"
}

# --- ファイルパスのパターン ---
CONTENT_PATTERNS = {
    "sticker_normal": r"^\d+@2x\.png$",
    "sticker_message": r"^\d+@2x\.png$",
    "sticker_moving_animation": r"^\d+@2x\.png$",
    "sticker_moving_effect_main": r"^\d+@2x\.png$",
    "sticker_moving_effect_popup": r"^\d+\.png$",
    "emoji_normal": r"^\d+\.png$",
    "emoji_moving": r"^\d+_animation\.png$"
}

# --- コンテンツが含まれるディレクトリ ---
CONTENT_DIRS = {
    "sticker_moving_animation": "animation@2x",
    "sticker_moving_effect_popup": "popup",
}


def get_pack_info(url):
    """
    URLからスタンプ・絵文字の情報を取得する
    """
    print(f"▼ パック情報を取得中: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # タイトルタグを複数の可能性から探す
        title_tag = soup.find('p', class_='mdCMN38Item01Ttl')  # 新しいレイアウト
        if not title_tag:
            title_tag = soup.find('p', class_='mdCMN08Ttl')  # 古いレイアウト
        
        if not title_tag:
            print("エラー: タイトルが見つかりませんでした。")
            return None, None, None
        
        title = title_tag.text.strip()
        # ファイルシステムで使えない文字を削除
        title = re.sub(r'[\\/*?:"><|]', "", title)
        
        pack_id = None
        pack_type = None

        if "stickershop" in url:
            match = re.search(r'/product/(\d+)', url)
            if match:
                pack_id = match.group(1)
                pack_type = "sticker"
        elif "emojishop" in url:
            match = re.search(r'/product/([a-fA-F0-9]+)', url)
            if match:
                pack_id = match.group(1)
                pack_type = "emoji"
        
        if pack_id and title and pack_type:
            print(f"  ID: {pack_id}, タイトル: {title}, 種類: {pack_type}")
            return pack_id, title, pack_type
        else:
            print("エラー: URLからIDと種類を特定できませんでした。")
            return None, None, None

    except requests.exceptions.RequestException as e:
        print(f"エラー: ページ情報の取得に失敗しました: {e}")
        return None, None, None


def download_zip(url, path):
    """
    ファイルをダウンロードする
    """
    print(f"▼ ダウンロード開始: {url}")
    try:
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"  ダウンロード完了: {path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"  ダウンロードエラー: {e}")
        return False


def organize_files(source_dir, output_dir, title, pattern, is_popup=False):
    """
    指定されたパターンのファイルを整理・リネームする
    """
    for filename in os.listdir(source_dir):
        if re.match(pattern, filename):
            original_path = os.path.join(source_dir, filename)
            
            # ポップアップスタンプの場合、ファイル名に "popup" を追加
            prefix = f"{title}_popup_" if is_popup else f"{title}_"
            new_filename = f"{prefix}{filename}"
            
            new_path = os.path.join(output_dir, new_filename)
            shutil.move(original_path, new_path)


def process_pack(pack_id, title, pack_subtype):
    """
    ダウンロードから整理までの全工程を管理する
    """
    zip_path = f"{pack_id}_temp.zip"
    temp_extract_dir = "temp_extract_dir"
    output_base_dir = "output"  # メインの出力ディレクトリ
    
    # --- ダウンロード ---
    download_url = DOWNLOAD_URLS[pack_subtype].format(id=pack_id)
    if not download_zip(download_url, zip_path):
        return

    # --- 解凍 ---
    print(f"▼ ZIPファイルを解凍中: {zip_path}")
    if os.path.exists(temp_extract_dir):
        shutil.rmtree(temp_extract_dir)
    os.makedirs(temp_extract_dir)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_dir)
        print("  解凍完了")
    except (zipfile.BadZipFile, OSError) as e:
        print(f"エラー: 解凍に失敗しました: {e}")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        return

    # --- 整理とリネーム ---
    # 出力先を 'output/スタンプ名' に設定
    output_dir = os.path.join(output_base_dir, title)
    os.makedirs(output_dir, exist_ok=True)
    print(f"▼ ファイルを整理・リネーム中 -> '{output_dir}'")
    
    if pack_subtype == "sticker_moving":
        # 動くスタンプの場合、エフェクトかアニメーションかを判別
        popup_dir = os.path.join(temp_extract_dir, CONTENT_DIRS["sticker_moving_effect_popup"])
        if os.path.isdir(popup_dir):
            print("  種類: エフェクトスタンプ")
            # メイン画像
            organize_files(temp_extract_dir, output_dir, title, CONTENT_PATTERNS["sticker_moving_effect_main"])
            # ポップアップ画像
            organize_files(popup_dir, output_dir, title, CONTENT_PATTERNS["sticker_moving_effect_popup"], is_popup=True)
        else:
            print("  種類: アニメーションスタンプ")
            animation_dir = os.path.join(temp_extract_dir, CONTENT_DIRS["sticker_moving_animation"])
            organize_files(animation_dir, output_dir, title, CONTENT_PATTERNS["sticker_moving_animation"])
    elif pack_subtype == "emoji_moving":
        organize_files(temp_extract_dir, output_dir, title, CONTENT_PATTERNS["emoji_moving"])
    elif pack_subtype == "emoji_normal":
        organize_files(temp_extract_dir, output_dir, title, CONTENT_PATTERNS["emoji_normal"])
    else: # Normal and Message stickers
        organize_files(temp_extract_dir, output_dir, title, CONTENT_PATTERNS[pack_subtype])
    
    print("  整理完了")

    # --- クリーンアップ ---
    print("▼ 一時ファイルをクリーンアップ中...")
    if os.path.exists(temp_extract_dir):
        shutil.rmtree(temp_extract_dir)
    if os.path.exists(zip_path):
        os.remove(zip_path)
    print("  クリーンアップ完了")
    print("\nすべての処理が完了しました。")


def main():
    """
    メイン処理
    """
    parser = argparse.ArgumentParser(description="LINEスタンプや絵文字をダウンロードし、整理するスクリプト。")
    # URL引数をオプションにする (nargs='?', default=None)
    parser.add_argument("url", nargs='?', default=None, help="（任意）LINEストアのスタンプまたは絵文字の製品URL。")
    args = parser.parse_args()

    url = args.url
    # URLが引数で渡されなかった場合、ユーザーに入力を促す
    if url is None:
        url = input("LINEストアのURLを入力してください: ")

    pack_id, title, pack_type = get_pack_info(url)
    if not all([pack_id, title, pack_type]):
        return

    pack_subtype = ""
    if pack_type == "sticker":
        while True:
            choice = input("\nスタンプの種類を選択してください (1: 普通, 2: メッセージ, 3: 動く): ")
            if choice == "1":
                pack_subtype = "sticker_normal"
                break
            elif choice == "2":
                pack_subtype = "sticker_message"
                break
            elif choice == "3":
                pack_subtype = "sticker_moving"
                break
            else:
                print("無効な選択です。1, 2, 3のいずれかを入力してください。")
    elif pack_type == "emoji":
        while True:
            choice = input("\n絵文字の種類を選択してください (1: 普通, 2: 動く/音あり): ")
            if choice == "1":
                pack_subtype = "emoji_normal"
                break
            elif choice == "2":
                pack_subtype = "emoji_moving"
                break
            else:
                print("無効な選択です。1, 2のいずれかを入力してください。")

    if pack_subtype:
        process_pack(pack_id, title, pack_subtype)

if __name__ == "__main__":
    main()
