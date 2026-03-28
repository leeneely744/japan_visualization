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

## トラブルシューティング

### TypeScript: `Cannot find module './style.css' or its corresponding type declarations`

**現象**  
`src/main.ts` で `import './style.css'` や画像・SVG の import に対し、エディタ上で上記のように型解決エラーが出る一方、Docker で起動した Vite の画面は問題なく表示できる。

**原因**  
`docker-compose.yaml` ではプロジェクトを `/app` にマウントしたうえで、`/app/node_modules` だけ匿名ボリュームに切り出している。`npm install` はコンテナ内のそのボリュームに依存関係を入れるため、**ホスト側の `node_modules` は空のまま**になりやすい。Vite はコンテナ内で正しく動くが、**エディタの TypeScript はホストの `node_modules` を参照する**ため、`vite` が提供する `vite/client` 型（`*.css` などの宣言）が読み込めずエラーになる。

**対処**  
リポジトリ直下でホスト上も依存関係を入れる。

```bash
npm install
```

インストール後、`node_modules/vite` が存在すればエディタのエラーは解消される。コンテナは引き続き独自の `node_modules` ボリュームを使う点に注意（ロックファイルで揃えておくと差分は抑えやすい）。

**別案**  
匿名ボリューム `- /app/node_modules` をやめてホストと `node_modules` を共有する、または Dev Containers でコンテナ内のツリーをエディタから参照する、など。

## 今後の予定

- [ ] 実データ（CSV/GeoJSON）の読み込み対応
- [ ] メッシュポリゴン（GeoJsonLayer）の追加
- [ ] 都道府県境界の表示
- [ ] データ絞り込みUI
- [ ] GitHub Pages でのホスティング