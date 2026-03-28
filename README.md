# Japan Data Viz

日本の地理データをインタラクティブに可視化するWebアプリケーション。

## 技術スタック

| 種別 | ライブラリ / サービス | バージョン |
|---|---|---|
| 地図レンダリング | MapLibre GL JS | 3.x |
| データ可視化 | deck.gl | latest |
| ベースマップ | CARTO Dark Matter | — |
| フォント | Google Fonts (Syne, DM Mono) | — |

## 構成ファイル
```
index.html   # すべてのコードが1ファイルに収まっている（CDN使用）
```

## データソース（予定）

- [e-Stat（政府統計）](https://www.e-stat.go.jp/gis)
- [国土数値情報](https://nlftp.mlit.go.jp/ksj/)
- [国土地理院](https://maps.gsi.go.jp/)

## 使い方

1. `index.html` をブラウザで開く（ローカルでも動作する）
2. サイドパネルでレイヤーの表示・非表示を切り替える
3. 不透明度・高さ倍率をスライダーで調整する
4. データ点にホバーすると詳細情報がツールチップで表示される

## 今後の予定

- [ ] 実データ（CSV/GeoJSON）の読み込み対応
- [ ] メッシュポリゴン（GeoJsonLayer）の追加
- [ ] 都道府県境界の表示
- [ ] データ絞り込みUI
- [ ] GitHub Pages でのホスティング