#!/usr/bin/env python3
"""证据门：校验备战包产物中的 文件:行号 证据锚点是否真实存在。

用法: python3 evidence_gate.py <产物.md> <仓库根目录>
规则:
  - 提取 路径.ext:行号 形式锚点 → 文件必须存在且行号不超文件行数
  - 提取反引号内的裸路径 → 文件必须存在
  - 任一悬空 → exit 1（打回 agy 重修对应段）
"""
import re
import sys
import pathlib

EXT = r'(?:py|java|go|js|ts|jsx|tsx|md|yaml|yml|json|toml|xml|sh|sql|html|css)'
ANCHOR = re.compile(rf'([\w\-./]+?\.{EXT}):(\d+)')
BARE = re.compile(rf'`([\w\-./]+?\.{EXT})`')


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    doc, root = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    if not doc.exists():
        sys.exit(f'产物不存在: {doc}')
    if not root.is_dir():
        sys.exit(f'仓库根不存在: {root}')

    text = doc.read_text(encoding='utf-8')
    anchors = set(ANCHOR.findall(text))
    anchor_paths = {p for p, _ in anchors}
    bares = {p for p in BARE.findall(text)} - anchor_paths

    oks, fails = 0, []
    for path, line in sorted(anchors):
        f = root / path
        if not f.exists():
            fails.append(f'悬空文件: {path}:{line}')
            continue
        nlines = len(f.read_text(encoding='utf-8', errors='ignore').splitlines())
        if int(line) > max(nlines, 1):
            fails.append(f'行号越界: {path}:{line} (该文件共 {nlines} 行)')
        else:
            oks += 1
    for path in sorted(bares):
        if (root / path).exists():
            oks += 1
        else:
            fails.append(f'悬空文件: {path}')

    print(f'证据门: {oks} 通过 / {len(fails)} 悬空')
    for f in fails:
        print('  FAIL', f)
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
