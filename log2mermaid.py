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

def _adjust_title(title: str, line: int) -> str:
    return f"{_escape(title)}<br/>L:{line}"

def main() -> None:
    args = sys.argv[1:]

    show_note = False
    if '--note' in args:
        show_note = True
        args = [a for a in args if a != '--note']

    if len(args) != 2:
        print('Usage: log2mermaid.py [--note] LOG_FILE MATCH_CSV', file=sys.stderr)
        sys.exit(1)

    log_file = args[0]
    conv_file = args[1]

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
                # kind: message | note（任意カラム。未指定やそれ以外は message 扱い）
                kind_raw = (r.get('kind') or 'message').strip().lower()
                if kind_raw == 'note':
                    kind = 'note'
                else:
                    kind = 'message'

                # title / match / src は必須
                if not (title and word and src):
                    continue
                # message 行では dst も必須。note 行では dst は任意（src のみでも可）
                if kind == 'message':
                    if not dst:
                        continue

                try:
                    pat = re.compile(word)
                except re.error as e:
                    print(f"Error: invalid regex in match: {word} ({e})", file=sys.stderr)
                    sys.exit(2)
                conv_list.append(
                    {
                        'title': title,
                        'pattern': pat,
                        'src': src,
                        'dst': dst,
                        'kind': kind,
                    }
                )
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
            i = 0
            for line in f:
                i += 1
                for c in conv_list:
                    if c['pattern'].search(line):
                        src = c['src']
                        dst = c['dst']
                        if src and src not in seen:
                            participants.append(src)
                            seen.add(src)
                        if dst and dst not in seen:
                            participants.append(dst)
                            seen.add(dst)
                        matches.append(
                            (
                                i,
                                src,
                                dst,
                                c['title'],
                                line.rstrip('\n'),
                                c.get('kind', 'message'),
                            )
                        )
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
    print('    autonumber')
    for p in participants:
        a = alias[p]
        if a == p:
            print(f'    participant {a}')
        else:
            print(f'    participant {a} as "{_escape(p)}"')
    note_max = None
    if show_note:
        # Noteの最大文字数（0で無制限）。環境変数 LOG2M_NOTE_MAX で上書き可。
        try:
            note_max = int(os.getenv('LOG2M_NOTE_MAX', str(DEFAULT_LOG2M_NOTE_MAX)))
        except ValueError:
            note_max = DEFAULT_LOG2M_NOTE_MAX

    for i, src, dst, title, line, kind in matches:
        s = alias[src]
        d = alias.get(dst) if dst else None

        has_dst = d is not None

        # kind=note の行は、メッセージ矢印を出さず、ライフライン上のNoteで表現する
        if kind == 'note':
            if has_dst:
                print(f'    Note over {s},{d}: {_adjust_title(title, i)}')
            else:
                print(f'    Note over {s}: {_adjust_title(title, i)}')
        else:
            # メッセージ行で dst が欠けている場合は自身宛てとして扱う（念のためのフォールバック）
            if not has_dst:
                d = s
            print(f'    {s} ->> {d}: {_adjust_title(title, i)}')

        # --note オプション指定時は、元ログ行をNoteとして出力（note 行／メッセージ行どちらも対象）
        if show_note:
            note = _escape(line)
            if note_max is not None and note_max > 0 and len(note) > note_max:
                note = note[: max(0, note_max - 1)] + '…'
            if has_dst:
                print(f'    Note over {s},{d}: {note} L:{i}')
            else:
                print(f'    Note over {s}: {note} L{i}')


if __name__ == '__main__':
    main()
