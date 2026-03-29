# Japan Data Viz — Makefile
#
# 【重要】開発用アプリの起動は Docker 経由のみを前提としています（Node/pnpm の
# バージョンを揃え、Windows / macOS などで同じ手順にするため）。
#   起動: make up  →  http://localhost:5173
#
# make setup / make install は任意です。ホスト上に node_modules を置き、エディタの
# 型解決・補完を効かせるための用途を想定しています（アプリ本体はコンテナ内で動作）。

PNPM ?= pnpm
DOCKER_COMPOSE ?= docker compose

.PHONY: help setup install image up down logs prod-build prod-preview clean

.DEFAULT_GOAL := help

help:
	@echo "【開発サーバーは Docker で起動してください】環境を揃えるための前提です。"
	@echo ""
	@echo "Setup（任意 — IDE 用にホストへ依存を入れる場合）"
	@echo "  make setup / make install   pnpm install（ホスト上）"
	@echo ""
	@echo "開発サーバー（Docker — こちらが通常の起動方法）"
	@echo "  make image                    開発用コンテナイメージをビルド"
	@echo "  make up                       コンテナ内で Vite を起動（前景・:5173）"
	@echo "  make down                     コンテナを停止"
	@echo "  make logs                     ログを追従（バックグラウンド起動時など）"
	@echo ""
	@echo "Production（プレフィックスで誤実行を防ぐ）"
	@echo "  make prod-build               型チェック + vite build → dist/"
	@echo "  make prod-preview             dist/ をプレビュー（先に prod-build）"
	@echo ""
	@echo "Maintenance"
	@echo "  make clean                    dist/ のみ削除（node_modules は触れない）"

setup install:
	$(PNPM) install

# 開発用アプリは必ず Docker で起動する（ローカルで pnpm dev するターゲットは置かない）
image:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

prod-build:
	$(PNPM) run build

prod-preview:
	$(PNPM) run preview

clean:
	rm -rf dist
