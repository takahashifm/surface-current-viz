#!/usr/bin/env python3
"""
GRIB2 Parser for Surface Current Data

GRIB2 形式の海流データをパース、JSON形式に変換
"""

import os
import json
import glob
import xarray as xr
import numpy as np
from pathlib import Path

DATA_DIR = "data"
PROCESSED_DIR = "processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

def parse_grib2_file(filepath):
    """
    GRIB2 ファイルをパース

    Args:
        filepath: GRIB2 ファイルパス

    Returns:
        dict: {lat, lon, u, v, depth, timestamp} のリスト
    """
    try:
        print(f"📖 パース中: {os.path.basename(filepath)}")

        # xarray で GRIB2 を読み込み
        ds = xr.open_dataset(filepath, engine='cfgrib')

        print(f"  変数: {list(ds.data_vars)}")
        print(f"  次元: {dict(ds.dims)}")

        # u, v 成分を抽出
        # 変数名は GRIB2 エンコーディングに依存 (例: u, v または UGRD, VGRD)
        u_var = None
        v_var = None

        for var in ds.data_vars:
            if 'u' in var.lower():
                u_var = var
            elif 'v' in var.lower():
                v_var = var

        if u_var is None or v_var is None:
            print(f"❌ u/v 成分が見つかりません: {list(ds.data_vars)}")
            return None

        u_data = ds[u_var]
        v_data = ds[v_var]

        print(f"  U変数: {u_var}, V変数: {v_var}")

        # 座標を取得
        lat = ds.coords['latitude'].values if 'latitude' in ds.coords else ds.coords.get('lat').values
        lon = ds.coords['longitude'].values if 'longitude' in ds.coords else ds.coords.get('lon').values

        # 深度情報を取得（存在する場合）
        depth = None
        if 'isobaricInhPa' in ds.coords:
            depth = ds.coords['isobaricInhPa'].values
        elif 'depthBelowLand' in ds.coords:
            depth = ds.coords['depthBelowLand'].values

        # タイムスタンプ
        timestamp = str(ds.coords['time'].values[0]) if 'time' in ds.coords else None

        # データをグリッドからポイントクラウドに変換
        entries = []

        # シンプルな実装: グリッド全体をポイントに変換
        u_array = u_data.values[0] if u_data.values.ndim > 2 else u_data.values
        v_array = v_data.values[0] if v_data.values.ndim > 2 else v_data.values

        for i, lat_val in enumerate(lat):
            for j, lon_val in enumerate(lon):
                if i < len(u_array) and j < len(u_array[i]):
                    u = float(u_array[i, j])
                    v = float(v_array[i, j])

                    # NaN チェック
                    if np.isnan(u) or np.isnan(v):
                        continue

                    entries.append({
                        "lat": float(lat_val),
                        "lon": float(lon_val),
                        "u": u,
                        "v": v,
                        "depth": float(depth[0]) if depth is not None else None
                    })

        print(f"  ✓ {len(entries)} ポイント抽出")
        return {
            "timestamp": timestamp,
            "data": entries
        }

    except Exception as e:
        print(f"❌ パースエラー: {e}")
        return None

def process_all_grib2():
    """すべての GRIB2 ファイルをパース"""
    print("=" * 60)
    print("GRIB2 Parser")
    print("=" * 60)

    grib2_files = glob.glob(os.path.join(DATA_DIR, "*.bin"))

    if not grib2_files:
        print(f"⚠️  GRIB2 ファイルが見つかりません: {DATA_DIR}")
        return

    for filepath in sorted(grib2_files):
        filename = os.path.basename(filepath)
        result = parse_grib2_file(filepath)

        if result:
            # JSON に保存
            output_filename = filename.replace('.bin', '.json').replace('grib2', '')
            output_path = os.path.join(PROCESSED_DIR, output_filename)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"  💾 保存: {output_filename}\n")

    print("=" * 60)
    print("✅ パース完了")
    print("=" * 60)

if __name__ == "__main__":
    process_all_grib2()
