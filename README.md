log2mermaid
=================

A tool that converts logs into Mermaid sequence diagrams.

Quick start

1. Install Python 3
2. Run the command below
```sh
python3 log2mermaid.py LOG_FILE MATCH_CSV > diagram.mmd
```

Sample

- Samples are in the `example` directory.

![Example Result](example/result.png)

CSV format

- Required columns: `title`, `match`, `src`, `dst`
- Example:
  | title | match | src | dst |
  | ---- | ---- | ---- | ---- |
  | hogeFunc1 | Component1: hoge function exec | Comp1 | Comp2 |
  | hogeFunc2 | Component2: hoge function exec | Comp2 | Comp1 |
- For details, see `example/match.csv`.

Notes

- The original log content is included in the output. Be careful with sensitive information.

Japanese guide

- See `README.ja.md`.

