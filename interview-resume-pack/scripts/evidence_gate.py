#!/usr/bin/env python3
"""证据门：校验备战包产物中的 文件:行号 证据锚点是否真实存在。

用法: python3 evidence_gate.py <产物.md> <仓库根目录>
规则:
  - 提取 路径.ext:行号 形式锚点 → 文件必须存在、是普通文件、行号 >=1 且不超文件行数
  - 提取反引号内的裸路径 → 文件必须存在
  - 空产物 / 零锚点 → FAIL（产物必须有证据）
  - 任一悬空 → exit 1（打回重修）；全部通过 → exit 0
"""
import re
import sys
import pathlib

EXT = r'(?:py|java|go|js|ts|jsx|tsx|md|yaml|yml|json|toml|xml|sh|sql|html|css)'
ANCHOR = re.compile(rf'([\w\-./]+?\.{EXT}):(\d+)')
BARE = re.compile(rf'`([\w\-./]+?\.{EXT})`')


def fail(msg):
    print(f'证据门 FAIL: {msg}')
    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    doc, root = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    if not doc.exists():
        fail(f'产物不存在: {doc}')
    if not doc.is_file():          # 目录 → FAIL（原版 read_text 崩溃）
        fail(f'产物不是普通文件: {doc}')
    if not root.is_dir():
        fail(f'仓库根不存在: {root}')

    raw = doc.read_bytes()
    if not raw.strip():            # 空产物 → FAIL（原版静默 exit 0）
        fail('产物为空，无任何证据')
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:     # 二进制误入 → FAIL（原版崩溃/乱码）
        fail('产物不是 UTF-8 文本（可能误传二进制）')

    anchors = set(ANCHOR.findall(text))
    bad_anchors = {a for a in anchors if int(a[1]) < 1}   # 行号 0/负数 → 非法
    anchors = {a for a in anchors if int(a[1]) >= 1}
    anchor_paths = {p for p, _ in anchors}
    bares = {p for p in BARE.findall(text)} - anchor_paths

    for p, ln in sorted(bad_anchors):
        print(f'  FAIL 行号非法(须>=1): {p}:{ln}')

    oks, fails = 0, []
    for path, line in sorted(anchors):
        f = root / path
        if not f.is_file():
            fails.append(f'悬空文件: {path}:{line}')
            continue
        nlines = len(f.read_text(encoding='utf-8', errors='ignore').splitlines())
        if int(line) > max(nlines, 1):
            fails.append(f'行号越界: {path}:{line} (该文件共 {nlines} 行)')
        else:
            oks += 1
    for path in sorted(bares):
        if (root / path).is_file():
            oks += 1
        else:
            fails.append(f'悬空文件: {path}')

    if not anchors and not bares:  # 零锚点 → FAIL
        fails.append('产物中未发现任何 文件:行号 或 `路径` 证据锚点')

    total_fails = len(fails) + len(bad_anchors)
    print(f'证据门: {oks} 通过 / {total_fails} 悬空')
    for f in fails:
        print('  FAIL', f)
    sys.exit(1 if total_fails else 0)


if __name__ == '__main__':
    main()
