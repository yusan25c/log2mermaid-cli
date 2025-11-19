log2mermaid
=================

A tool that converts logs into Mermaid sequence diagrams.

Quick start

1. Install Python 3
2. Run the command below
```sh
python3 log2mermaid.py [--note] LOG_FILE MATCH_CSV > diagram.mmd
```

Sample

- Samples are in the `example` directory.

![Example Result](example/result.png)

CSV format

- Required columns: `title`, `match`, `src`, `dst`
- `match` is a regular expression (Python `re.search`) applied to each log line.
- Example (same as example/match.csv):

  | title     | match                      | src        | dst         |
  | ----      | ----                       | ----       | ----        |
  | hogeFunc1 | Component1 func:           | API Server | Client      |
  | hogeFunc2 | Component2 func:.* str=abc | Client     | API Server  |

Notes

- By default, original log lines are not emitted as Mermaid Notes (only the message lines are output).
- If you add the `--note` option, original log lines are emitted as Mermaid Notes. Be careful with sensitive information.

Japanese guide

- See `README.ja.md`.
