# nexus-webscraper-mcp

Crawl4AI を搭載し、高度なノイズ除去機能を備えたスクレイピング MCP サーバーです。

## 特徴
- **高精度スクレイピング**: Crawl4AI の `fit_markdown=True` を用いて、ウェブページの主要コンテンツのみを優先的に抽出。
- **後処理トリミング**: `関連記事` や `ランキング`、`Copyright` 等の不要な要素を検知して自動的に削除する後処理ロジックを搭載。ITmedia のようなサイトでも本文のみを綺麗に抽出します。
- **MCP 対応**: `FastMCP` ベースで構築されており、標準入出力を通じて各種 AI アシスタントから直接呼び出すことが可能です。

## セットアップ方法

本プロジェクトは `uv` をパッケージマネージャーとして使用しています。

```bash
uv sync
```

## 実行方法

以下のコマンドを実行することで、MCP サーバーが起動します。

```bash
uv run server.py
```

## ライセンス

本プロジェクトは [Apache License 2.0](LICENSE) に基づいてライセンスされています。詳細はリポジトリ内の [LICENSE](LICENSE) ファイルをご確認ください。

## 帰属表示 (Attribution)

ウェブデータ抽出エンジンとして Crawl4AI を使用しています。
本プロジェクトではウェブデータ抽出にCrawl4AIを使用しています（[https://github.com/unclecode/crawl4ai](https://github.com/unclecode/crawl4ai)）。

<a href="https://github.com/unclecode/crawl4ai">
  <img src="https://img.shields.io/badge/Powered%20by-Crawl4AI-blue?style=flat-square" alt="Powered by Crawl4AI"/>
</a>
