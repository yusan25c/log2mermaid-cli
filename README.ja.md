log2mermaid
=================

ログをMermaidのシーケンス図に変換するツールです。

クイックスタート

1. pythonをインストールする
2. 以下のコマンドで実行する
``` sh
python3 log2mermaid.py LOG_FILE MATCH_CSV > diagram.mmd
```

サンプル

- exampleにサンプルが格納されています。

![サンプル結果](example/result.png)

CSVフォーマット

- 必須カラム: `title`, `match`, `src`, `dst`
- 例:
  | title | match | src | dst |
  | ---- | ---- | ---- | ---- |
  | hogeFunc1 | Component1: hoge function exec | Comp1 | Comp2 |
  | hogeFunc2 | Component2: hoge function exec | Comp2 | Comp1 |
- 詳しくはexample内にあるmatch.csvを参照してください。


注意事項

- ログの内容がそのまま出力に含まれます。機密情報が含まれる場合はご注意ください。

