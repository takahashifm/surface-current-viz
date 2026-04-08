#!/usr/bin/env python3
"""
GRIB2 Parser v2 - pygrib を使用した実装

複数の GRIB2 ファイル（FD01～FD10）を読み込み、
1つの JSON ファイルに統合する
"""

import os
import json
import glob
import pygrib
import numpy as np
from datetime import datetime

DATA_DIR = "data"
PROCESSED_DIR = "processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

LAT_MIN = 41.0  # 北緯 41° 以上
LAT_MAX = 44.0  # 北緯 44° 以下
LON_MIN = 143.0  # 東経 143° 以上
LON_MAX = 147.0  # 東経 147° 以下
STEP = 2  # グリッド間隔（2ポイントおき、約1km）

def parse_grib2_file(filepath):
    """
    GRIB2 ファイルを解析して u/v データを抽出

    Returns:
        { "time": "...", "data": [ { "lat": ..., "lon": ..., "u": ..., "v": ... } ] }
    """
    print(f"📖 解析中: {os.path.basename(filepath)}")

    try:
        grbs = pygrib.open(filepath)

        # 最初のメッセージペア（最浅層）から情報を取得
        msg_u = grbs.message(1)
        msg_v = grbs.message(2)

        ref_time = msg_u.validDate
        print(f"  参照時刻: {ref_time}")

        # 緯度・経度グリッドを取得
        lats, lons = msg_u.latlons()
        u_vals = msg_u.values
        v_vals = msg_v.values

        # データポイントに変換
        entries = []

        # グリッドを疎にサンプリング
        for i in range(0, lats.shape[0], STEP):
            for j in range(0, lats.shape[1], STEP):
                lat = float(lats[i, j])
                lon = float(lons[i, j])

                # 北緯 41° 以上、44° 以下
                if lat < LAT_MIN or lat > LAT_MAX:
                    continue

                # 東経 143° 以上、147° 以下
                if lon < LON_MIN or lon > LON_MAX:
                    continue

                u = float(u_vals[i, j])
                v = float(v_vals[i, j])

                # NaN チェック
                if np.isnan(u) or np.isnan(v):
                    continue

                entries.append({
                    "lat": lat,
                    "lon": lon,
                    "u": u,
                    "v": v
                })

        grbs.close()

        print(f"  ✓ {len(entries)} ポイント抽出")
        return {
            "time": ref_time.isoformat(),
            "data": entries
        }

    except Exception as e:
        print(f"  ❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return None

def process_all_grib2():
    """複数の GRIB2 ファイルをパースして JSON に統合"""
    print("=" * 60)
    print("GRIB2 Parser v2 (複数ファイル統合)")
    print("=" * 60)

    grib2_files = sorted(glob.glob(os.path.join(DATA_DIR, "*.bin")))

    if not grib2_files:
        print(f"⚠️  GRIB2 ファイルが見つかりません: {DATA_DIR}")
        return

    all_entries = []

    for filepath in grib2_files:
        filename = os.path.basename(filepath)
        result = parse_grib2_file(filepath)

        if result and result['data']:
            all_entries.append(result)

    # 統合 JSON ファイルに保存
    output_filename = "ocean_current_data.json"
    output_path = os.path.join(PROCESSED_DIR, output_filename)

    output_data = {
        "entries": all_entries,
        "count": len(all_entries),
        "generated": datetime.now().isoformat()
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n💾 統合 JSON 保存: {output_filename}")
    print(f"  時刻エントリ数: {len(all_entries)}")

    total_points = sum(len(entry['data']) for entry in all_entries)
    print(f"  総ポイント数: {total_points:,}")
    print(f"  ファイルサイズ: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")

    print("=" * 60)
    print("✅ パース完了")
    print("=" * 60)

if __name__ == "__main__":
    process_all_grib2()
