# Surface Current Visualizer

海面流表層の流れを可視化するツール

## 概要

GLINNOVATION の GRIB2 フォーマット海流データを取得・解析し、
ブラウザ上でインタラクティブに可視化します。

## データソース

- **URL**: https://metingest01.glinnovation.jp/dataput/jmbsc/OCN_GPV_Rnwpa/
- **ファイル形式**: GRIB2 (.bin)
- **対象**: 日本周辺海域
- **グリッド解像度**: 2km
- **深度範囲**: 1100～6150m
- **予報期間**: FD01～FD10（1日先～10日先）

## ファイル構成

```
surface-current-viz/
├── fetch_grib2.py          # GRIB2 データ取得スクリプト
├── parse_grib2.py          # GRIB2 パーサー
├── index.html              # 可視化画面
├── data/                   # ダウンロードしたGRIB2ファイル
├── processed/              # パース済みデータ (JSON)
└── README.md
```

## セットアップ

### 1. Python 環境

```bash
pip install cfgrib xarray netcdf4 requests
```

### 2. データ取得

```bash
python3 fetch_grib2.py
```

### 3. 可視化

ブラウザで `index.html` を開く

## 使用方法

1. `fetch_grib2.py` で最新の GRIB2 ファイルを取得
2. `parse_grib2.py` で GRIB2 を JSON に変換
3. `index.html` で可視化

## 技術スタック

- **データ処理**: Python (cfgrib, xarray)
- **可視化**: Leaflet.js + Canvas
- **フォーマット**: GRIB2 → JSON
