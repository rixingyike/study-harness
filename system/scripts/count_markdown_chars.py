#!/usr/bin/env python3
"""
Study-Harness 方案二: 独立命令行脚本工具
功能: 统计 Markdown 文件中的纯净正文非空白字符数量
过滤规则:
  1. 严格跳过开头的 YAML Frontmatter (--- 至 ---)
  2. 严格排除所有的引用块文本 (> ...)
  3. 严格排除所有的代码块 (``` 或 ~~~ 围合的全部代码与标记)
  4. 排除空白符（空格、全角空格、制表符、换行符）
"""
import os
import re
import sys
import json
import argparse
from pathlib import Path

def count_clean_markdown_chars(file_path: str) -> dict:
    path = Path(file_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    if not path.is_file():
        raise ValueError(f"指定路径不是普通文件: {file_path}")

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    in_frontmatter = False
    frontmatter_finished = False
    in_code_block = False
    code_fence_char = ""

    valid_lines_count = 0
    excluded_quote_lines = 0
    excluded_code_lines = 0
    clean_chars_list = []

    for i, line in enumerate(lines):
        # 1. 检测 YAML Frontmatter
        if i == 0 and line.strip() == "---":
            in_frontmatter = True
            continue

        if in_frontmatter:
            if line.strip() == "---":
                in_frontmatter = False
                frontmatter_finished = True
            continue

        # 2. 检测代码块开合 (``` 或 ~~~)
        stripped = line.strip()
        fence_match = re.match(r"^(```|~~~)", stripped)
        if fence_match:
            fence = fence_match.group(1)
            if not in_code_block:
                in_code_block = True
                code_fence_char = fence
                excluded_code_lines += 1
                continue
            elif in_code_block and stripped.startswith(code_fence_char):
                in_code_block = False
                code_fence_char = ""
                excluded_code_lines += 1
                continue

        if in_code_block:
            excluded_code_lines += 1
            continue

        # 3. 检测引用块 (> ...)
        if re.match(r"^\s*>", line):
            excluded_quote_lines += 1
            continue

        # 4. 统计正文非空白字符
        non_ws_chars = [ch for ch in line if not ch.isspace()]
        if non_ws_chars:
            valid_lines_count += 1
            clean_chars_list.extend(non_ws_chars)

    total_clean_chars = len(clean_chars_list)

    return {
        "file_path": str(path),
        "file_name": path.name,
        "total_lines": len(lines),
        "valid_text_lines": valid_lines_count,
        "excluded_quote_lines": excluded_quote_lines,
        "excluded_code_lines": excluded_code_lines,
        "non_whitespace_chars": total_clean_chars,
        "status": "success"
    }

def main():
    parser = argparse.ArgumentParser(
        description="统计 Markdown 文件中的纯净非空白字符数（排除 Frontmatter、引用和代码块）"
    )
    parser.add_argument("file_path", help="Markdown 文件的绝对路径或相对路径")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出统计结果")

    args = parser.parse_args()

    try:
        res = count_clean_markdown_chars(args.file_path)
    except Exception as e:
        if args.json:
            print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
        else:
            print(f"❌ 统计失败: {str(e)}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print("==================================================")
        print("📊 Markdown 纯净正文字符统计报告")
        print("==================================================")
        print(f"目标文件      : {res['file_path']}")
        print(f"原始总行数    : {res['total_lines']} 行")
        print(f"排除引用行    : {res['excluded_quote_lines']} 行 (已过滤 > 引用)")
        print(f"排除代码块行  : {res['excluded_code_lines']} 行 (已过滤 ```/~~~ 代码)")
        print(f"有效正文行数  : {res['valid_text_lines']} 行")
        print("--------------------------------------------------")
        print(f"非空白字符总数: {res['non_whitespace_chars']:,} 字")
        print("==================================================")

if __name__ == "__main__":
    main()
