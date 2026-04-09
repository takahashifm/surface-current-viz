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
    GRIB2 ファイルを解析して grib2json フォーマットで出力

    Returns:
        grib2json 形式のデータ
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

        # グリッド情報を取得
        nlat, nlon = lats.shape
        lat_min, lat_max = float(np.nanmin(lats)), float(np.nanmax(lats))
        lon_min, lon_max = float(np.nanmin(lons)), float(np.nanmax(lons))

        # グリッドデータを構築（Leaflet-Velocity 互換）
        grid_data = []

        for i in range(0, nlat, STEP):
            for j in range(0, nlon, STEP):
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

                grid_data.append([lat, lon, u, v])

        grbs.close()

        print(f"  ✓ {len(grid_data)} ポイント抽出")

        # grib2json フォーマットで返す
        return {
            "header": {
                "parameterNumber": 2,
                "parameterNumberName": "u-component of ocean current",
                "parameterUnit": "m/s",
                "refTime": ref_time.isoformat(),
                "nlon": nlon // STEP,
                "nlat": nlat // STEP,
                "la1": float(np.nanmax(lats)),
                "la2": float(np.nanmin(lats)),
                "lo1": float(np.nanmin(lons)),
                "lo2": float(np.nanmax(lons)),
                "dx": 0.02,  # 約2km
                "dy": 0.02
            },
            "data": grid_data
        }

    except Exception as e:
        print(f"  ❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return None

def process_all_grib2():
    """複数の GRIB2 ファイルをパースして grib2json 形式で統合"""
    print("=" * 60)
    print("GRIB2 Parser v2 (grib2json 形式出力)")
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

    # grib2json リスト形式で保存
    output_filename = "ocean_current_data.json"
    output_path = os.path.join(PROCESSED_DIR, output_filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)

    print(f"\n💾 grib2json 形式で保存: {output_filename}")
    print(f"  時刻エントリ数: {len(all_entries)}")

    total_points = sum(len(entry['data']) for entry in all_entries)
    print(f"  総ポイント数: {total_points:,}")
    print(f"  ファイルサイズ: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")

    print("=" * 60)
    print("✅ パース完了")
    print("=" * 60)

if __name__ == "__main__":
    process_all_grib2()
