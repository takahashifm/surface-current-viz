#!/usr/bin/env python3
"""
ocean_current_data.json を HTML に埋め込むスクリプト

使用方法:
    python3 embed_data.py
"""

import json
import os

def embed_data_in_html():
    """ocean_current_data.json を HTML に埋め込む"""

    # JSON ファイルを読み込む
    json_path = "processed/ocean_current_data.json"
    html_path = "index.html"

    if not os.path.exists(json_path):
        print(f"❌ エラー: {json_path} が見つかりません")
        return

    print(f"📖 {json_path} を読み込み中...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # JavaScript コードを生成
    js_code = f"""        const embeddedOceanCurrentData = {json.dumps(data, ensure_ascii=False)};
"""

    print(f"✓ JavaScript コードを生成（サイズ: {len(js_code):,} bytes）")

    # HTML ファイルを読み込む
    print(f"📖 {html_path} を読み込み中...")
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # プレースホルダーを置き換える
    old_placeholder = "        const embeddedOceanCurrentData = null;  // プレースホルダー"

    if old_placeholder in html_content:
        html_content = html_content.replace(old_placeholder, js_code.rstrip())
        print(f"✓ HTML を更新（プレースホルダーを置き換え）")
    else:
        print("⚠️  プレースホルダーが見つかりません")
        return

    # HTML ファイルを上書き
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    html_size = os.path.getsize(html_path) / 1024 / 1024
    print(f"💾 {html_path} を保存（サイズ: {html_size:.1f} MB）")
    print("=" * 60)
    print("✅ データを HTML に埋め込みました")
    print("=" * 60)

if __name__ == "__main__":
    embed_data_in_html()
