#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Study-Harness CLI Entrypoint.
"""

import sys
from study_harness import run_harness_loop

def main():
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = "请帮我在当前目录下创建一个名为'研创宣言.txt'的文件，内容为'鞍辔齐备，学者研创'，并确认写入是否成功。"

    run_harness_loop(task)

if __name__ == "__main__":
    main()
