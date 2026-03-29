# Japan Data Viz

日本の地理データをインタラクティブに可視化する Web アプリケーション。

## 開発環境の前提（重要）

**開発用アプリは Docker 上で起動してください。** Node / pnpm のバージョン差をなくし、Windows / macOS などで同じ手順にするための前提です。ローカルに入れた Node で `pnpm dev` だけを実行する運用は想定していません。

### 必要なもの

- **Docker**（Docker Desktop など）— コンテナのビルドと起動
- **GNU Make** — `Makefile` 経由のコマンド
- （任意）**pnpm** — ホスト側で `make setup` し、エディタの型チェック・補完を効かせる場合

### アプリの起動（Docker）

```bash
make up
```

ブラウザで **http://localhost:5173** を開きます。

初回や `Dockerfile` を変更したあとは、先にイメージをビルドしても構いません。

```bash
make image
make up
```

停止するときは `make down`。

詳細なターゲット一覧は `make help` を参照してください。

---

## 技術スタック

| 種別 | ライブラリ / サービス | バージョン |
|---|---|---|
| ビルド | Vite, Vue 3, TypeScript | プロジェクト参照 |
| 地図レンダリング | MapLibre GL JS | 3.x |
| データ可視化 | deck.gl | latest |
| ベースマップ | CARTO Dark Matter | — |
| フォント | Google Fonts (Syne, DM Mono) | — |

## 構成（概要）

- `index.html` — エントリ HTML（CDN スクリプト・`#app`）
- `src/` — Vue / TypeScript ソース
- `Dockerfile` / `docker-compose.yaml` — 開発用コンテナ
- `Makefile` — セットアップ・Docker 起動・本番ビルドなど

## データソース（予定）

- [e-Stat（政府統計）](https://www.e-stat.go.jp/gis)
- [国土数値情報](https://www.nlftp.mlit.go.jp/ksj/)
- [国土地理院](https://maps.gsi.go.jp/)

## 使い方（アプリ）

1. 上記のとおり Docker で開発サーバーを起動する（`make up`）
2. ブラウザで表示を確認する
3. （実装に応じて）レイヤー表示・スライダー・ツールチップなどを操作する

## トラブルシューティング

### TypeScript: `Cannot find module './style.css'` など（エディタのみ）

**現象**  
エディタ上で型解決エラーが出る一方、Docker で起動した Vite の画面は問題ない。

**原因**  
`docker-compose.yaml` で `/app/node_modules` を匿名ボリュームにしていると、依存はコンテナ内に入り、**ホストの `node_modules` が空のまま**になりやすい。エディタはホストを参照するため。

**対処**  
ホストでも依存を入れる（任意）。

```bash
make setup
```

または `pnpm install`。`node_modules/vite` がホストにあればエディタのエラーは解消されやすいです。

**別案**  
匿名ボリュームをやめてホストと `node_modules` を共有する、Dev Containers でコンテナ内を開く、など。

## 今後の予定

- [ ] 実データ（CSV/GeoJSON）の読み込み対応
- [ ] メッシュポリゴン（GeoJsonLayer）の追加
- [ ] 都道府県境界の表示
- [ ] データ絞り込み UI
- [ ] GitHub Pages でのホスティング
