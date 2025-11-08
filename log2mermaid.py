#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import csv
import re
import os

DEFAULT_LOG2M_NOTE_MAX = 160


def _escape(text: str) -> str:
    # Minimal escaping to keep Mermaid stable
    return (
        text.replace('"', "'")
            .replace('`', "'")
            .replace('<', '&lt;')
            .replace('>', '&gt;')
    )


def _needs_alias(name: str) -> bool:
    return re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', name) is None


def main() -> None:
    if len(sys.argv) != 3:
        print('Usage: log2mermaid.py LOG_FILE MATCH_CSV', file=sys.stderr)
        sys.exit(1)

    log_file = sys.argv[1]
    conv_file = sys.argv[2]

    # マッピングの読み込み（match は正規表現として扱う）
    try:
        with open(conv_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            headers = set(reader.fieldnames or [])
            required = {'title', 'match', 'src', 'dst'}
            if not headers or not required.issubset(headers):
                print('Error: CSV header must include title, match, src, dst', file=sys.stderr)
                sys.exit(2)

            conv_list = []
            for r in reader:
                title = (r.get('title') or '').strip()
                word = (r.get('match') or '').strip()
                src = (r.get('src') or '').strip()
                dst = (r.get('dst') or '').strip()
                if title and word and src and dst:
                    try:
                        pat = re.compile(word)
                    except re.error as e:
                        print(f"Error: invalid regex in match: {word} ({e})", file=sys.stderr)
                        sys.exit(2)
                    conv_list.append({'title': title, 'pattern': pat, 'src': src, 'dst': dst})
    except FileNotFoundError:
        print(f'Error: CSV not found: {conv_file}', file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f'Error: failed to read CSV: {e}', file=sys.stderr)
        sys.exit(2)

    # ログを逐次走査してマッチを収集
    matches = []
    participants = []
    seen = set()
    try:
        with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                for c in conv_list:
                    if c['pattern'].search(line):
                        src = c['src']
                        dst = c['dst']
                        if src not in seen:
                            participants.append(src)
                            seen.add(src)
                        if dst not in seen:
                            participants.append(dst)
                            seen.add(dst)
                        matches.append((src, dst, c['title'], line.rstrip('\n')))
    except FileNotFoundError:
        print(f'Error: log file not found: {log_file}', file=sys.stderr)
        sys.exit(2)

    # 参加者の簡易エイリアス（識別子に不向きな名前のみ）
    alias = {}
    counter = 1
    for p in participants:
        if _needs_alias(p):
            alias[p] = f'P{counter}'
            counter += 1
        else:
            alias[p] = p

    # Mermaid出力
    print('sequenceDiagram')
    for p in participants:
        a = alias[p]
        if a == p:
            print(f'    participant {a}')
        else:
            print(f'    participant {a} as "{_escape(p)}"')
    # Noteの最大文字数（0で無制限）。環境変数 LOG2M_NOTE_MAX で上書き可。
    try:
        note_max = int(os.getenv('LOG2M_NOTE_MAX', str(DEFAULT_LOG2M_NOTE_MAX)))
    except ValueError:
        note_max = DEFAULT_LOG2M_NOTE_MAX

    for src, dst, title, line in matches:
        s = alias[src]
        d = alias[dst]
        print(f'    {s} ->> {d}: {_escape(title)}')
        note = _escape(line)
        if note_max > 0 and len(note) > note_max:
            note = note[: max(0, note_max - 1)] + '…'
        print(f'    Note over {s},{d}: {note}')


if __name__ == '__main__':
    main()
