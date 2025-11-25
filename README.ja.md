log2mermaid
=================

ログをMermaidのシーケンス図に変換するツールです。

クイックスタート

1. pythonをインストールする
2. 以下のコマンドで実行する
``` sh
python3 log2mermaid.py [--note] LOG_FILE MATCH_CSV > diagram.mmd
```

サンプル

- exampleにサンプルが格納されています。

![サンプル結果](example/result.png)

CSVフォーマット

- 必須カラム: `title`, `match`, `src`, `dst`
- 任意カラム: `kind`
  - `kind` が `note` の場合、その行は「ノート行」として扱われます。
  - ノート行は状態変化などのさまざまなイベントを表し、`src -> dst` のメッセージは出力されず、MermaidのNoteとしてライフライン上に表示されます。
  - `kind` が指定されていない場合や `note` 以外の値の場合は、通常のメッセージ行（矢印）として扱われます。
- `match` は正規表現（Pythonの `re.search` で各ログ行に適用）
- 例（`example/match.csv` の抜粋）:
  | title          | match                        | src     | dst     | kind    |
  | ----           | ----                         | ----    | ----    | ----    |
  | requestMessage | Sample1 .* requestMessage    | Sample1 | Sample2 | message |
  | notifyMessage  | Sample2 .* notifyMessage     | Sample2 | Sample1 | message |
  | State:Executing| Sample2 State:.* -> 1        | Sample2 |         | note    |

注意事項

- デフォルトでは元ログはMermaidのNoteとして出力されません（メッセージ行のみ出力されます）。
- `--note` オプションを付けると、MermaidのNoteとして元ログも出力されます。機密情報が含まれる場合はご注意ください。
