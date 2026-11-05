#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ruminator.py: 反刍随身记与闪念捕获服务核心实现 (MCP intuition-ruminator 配套)
理论依据：贝弗里奇《科学研究的艺术》第六章「直觉」之加压-泄压与随身纸笔置于脑后
"""

import os
import sys
import datetime
from pathlib import Path
from typing import Optional

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent

for p in [CURRENT_DIR, PROJECT_ROOT / "scripts"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

def record_spark(
    spark_text: str,
    category: str = "闪念",
    tags: str = "",
    root_dir: Optional[Path] = None
) -> str:
    """
    闪念秒记与瞬间卸载（Unload）：将灵感存入 反刍/YYYY-MM-DD.md 并清空工作记忆缓存
    """
    root = root_dir or PROJECT_ROOT
    ruminate_dir = root / "反刍"
    ruminate_dir.mkdir(parents=True, exist_ok=True)
    
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    file_path = ruminate_dir / f"{date_str}.md"
    
    # 构造条目
    tag_suffix = f" #{tags.strip()}" if tags.strip() else ""
    header_needed = not file_path.exists()
    
    entry_lines = []
    if header_needed:
        entry_lines.append(f"# 研创反刍与闪念捕获日志：{date_str}\n")
        entry_lines.append("> 理论依据：贝弗里奇《科学研究的艺术》第六章「直觉」\n")
        entry_lines.append("> 核心准则：随身闪念秒记即落盘，大脑缓存即刻清空置于脑后（Unload），静待潜意识拼图。\n\n---\n")
    
    entry_lines.append(f"\n### [{time_str}] 【{category}】{tag_suffix}")
    entry_lines.append(f"\n{spark_text.strip()}\n")
    
    with open(file_path, "a", encoding="utf-8") as f:
        f.writelines(entry_lines)
        
    return (
        f"[✓] 闪念已成功归档并从工作记忆中卸载（Unload）！\n"
        f"时间：{date_str} {time_str}\n"
        f"归档文件：{file_path.relative_to(root)}\n"
        f"内容：{spark_text.strip()[:80]}...\n\n"
        f"【医嘱建议】：内容已安全落盘，请立即将其抛置脑后，安心投入当前工作或放松休息，让潜意识在后台自由拼图。"
    )

def read_daily_rumination(date_str: str = "", root_dir: Optional[Path] = None) -> str:
    """
    读取指定日期的反刍日志（默认读取今日）
    """
    root = root_dir or PROJECT_ROOT
    if not date_str:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    file_path = root / "反刍" / f"{date_str}.md"
    if not file_path.exists():
        return f"日期 {date_str} 暂无反刍闪念记录（路径: {file_path}）"
    return file_path.read_text(encoding="utf-8")
