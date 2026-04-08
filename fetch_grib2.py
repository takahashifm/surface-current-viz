#!/usr/bin/env python3
"""
Surface Current GRIB2 Data Fetcher

GLINNOVATION から GRIB2 フォーマットの海流データを取得
https://metingest01.glinnovation.jp/dataput/jmbsc/OCN_GPV_Rnwpa/
"""

import os
import sys
import requests
from datetime import datetime, timedelta
import ssl

# SSL証明書エラーを無視
ssl._create_default_https_context = ssl._create_unverified_context

BASE_URL = "https://metingest01.glinnovation.jp/dataput/jmbsc/OCN_GPV_Rnwpa/"
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_file_list():
    """ディレクトリから取得可能なファイル一覧を取得"""
    print("🔍 利用可能なファイル一覧を確認中...")

    try:
        response = requests.get(BASE_URL, verify=False, timeout=10)
        response.raise_for_status()
        print(f"✓ ディレクトリアクセス成功")
        return response.text
    except Exception as e:
        print(f"❌ ディレクトリ取得失敗: {e}")
        return None

def fetch_grib2(forecast_day=1):
    """
    特定の予報日の GRIB2 ファイルをダウンロード

    Args:
        forecast_day: 予報日 (1-10)
    """
    if forecast_day < 1 or forecast_day > 10:
        print(f"❌ 予報日は 1-10 の範囲です: {forecast_day}")
        return False

    # ファイル名パターン: Z__C_RJTD_<タイムスタンプ>_OCN_GPV_Rjp_Gll2km_Lsurf_Pssh_FD<NN>_grib2.bin
    # タイムスタンプは初期時刻（例：20260402000000）
    # 実装では、最新のデータを探すため、複数の日付をトライ

    now = datetime.utcnow()
    # 過去3日分をトライ（最新データを探す）
    dates_to_try = [
        (now - timedelta(days=0)).strftime("%Y%m%d000000"),
        (now - timedelta(days=1)).strftime("%Y%m%d000000"),
        (now - timedelta(days=2)).strftime("%Y%m%d000000"),
    ]

    fd_str = f"FD{forecast_day:02d}"

    for ts in dates_to_try:
        filename = f"Z__C_RJTD_{ts}_OCN_GPV_Rjp_Gll2km_Lz1-1000_Pcur_{fd_str}_grib2.bin"
        url = BASE_URL + filename

        print(f"📥 ダウンロード試行: {filename}")

        try:
            response = requests.get(url, verify=False, timeout=30)
            if response.status_code == 200:
                filepath = os.path.join(DATA_DIR, filename)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"✓ ダウンロード成功: {filename} ({len(response.content)} bytes)")
                return True
            else:
                print(f"  ステータス: {response.status_code}")
        except Exception as e:
            print(f"  エラー: {e}")

    return False

def fetch_all_forecasts(start_day=1, end_day=10):
    """全予報日のデータをダウンロード"""
    print("=" * 60)
    print("Surface Current GRIB2 Data Fetcher")
    print("=" * 60)

    success_count = 0
    for day in range(start_day, end_day + 1):
        if fetch_grib2(day):
            success_count += 1
        print()

    print("=" * 60)
    print(f"✅ 完了: {success_count}/{end_day - start_day + 1} 日分取得")
    print("=" * 60)

if __name__ == "__main__":
    # コマンドライン引数で予報日を指定可能
    if len(sys.argv) > 1:
        try:
            day = int(sys.argv[1])
            fetch_grib2(day)
        except ValueError:
            print(f"❌ 無効な引数: {sys.argv[1]}")
            sys.exit(1)
    else:
        # デフォルト: FD01 のみ取得
        fetch_grib2(1)
