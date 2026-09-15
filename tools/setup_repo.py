#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把仓库里的占位符一次性替换成你自己的信息。

仓库里所有需要填的地方都用了统一占位符，这个脚本负责全局替换 + 重命名投稿目录，
免得你手动搜 11 个文件。

用法：
    # 只看会改什么，不真改（推荐先跑这个）
    python tools/setup_repo.py --username <你的GitHub用户名> --name "<你的名字>" --dry-run

    # 真正执行
    python tools/setup_repo.py --username <你的GitHub用户名> --name "<你的名字>"

    # 顺便配好 git 提交身份（不传 --email 就只替换、不动 git）
    python tools/setup_repo.py --username hon --name "Hon" --email hon@example.com

替换内容：
    YOUR-GITHUB-USERNAME  →  你的 GitHub 用户名
    YOUR NAME             →  你的名字 / 昵称（出现在 LICENSE 版权行）
    <你的用户名>          →  你的 GitHub 用户名（在 tools/build_library.py 的 source 字段）

替换完还要重跑一次构建脚本，库文件里的 source 链接才会更新：

    python tools/build_library.py
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 不扫描的目录
SKIP_DIRS = {".git", ".workbuddy", "__pycache__", "node_modules", ".venv", "venv"}

# 占位符（拆开拼是为了脚本自己不被替换掉）
U_PH = "YOUR-GITHUB-" + "USERNAME"
N_PH = "YOUR " + "NAME"
C_PH = "<" + "你的用户名" + ">"

# 投稿目录（会被重命名）
SUBMISSION_DIR = ROOT / "submission"


def iter_text_files():
    """遍历仓库里的文本文件（跳过 .git/.workbuddy 等目录，以及本脚本自身）。"""
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.resolve() == Path(__file__).resolve():
            continue  # 本脚本的注释里就写着占位符，跳过
        yield path


def main():
    ap = argparse.ArgumentParser(description="替换 hvac-excalidraw-library 里的占位符")
    ap.add_argument("--username", required=True, help="你的 GitHub 用户名（用于仓库链接）")
    ap.add_argument("--name", help="你的名字/昵称（用于 LICENSE 版权行），默认同用户名")
    ap.add_argument("--email", help="git 提交邮箱，传了才帮你配 git config --global")
    ap.add_argument("--dry-run", action="store_true", help="只预览改动，不写文件")
    args = ap.parse_args()

    username = args.username.strip()
    name = (args.name or username).strip()

    if username.startswith("YOUR") or name.startswith("YOUR"):
        sys.exit("[x] --username / --name 不能还是占位符本身")

    replacements = [(C_PH, username), (U_PH, username), (N_PH, name)]

    print("=" * 66)
    print("占位符替换 %s" % ("（预演，不写盘）" if args.dry_run else ""))
    print("  用户名 -> %s" % username)
    print("  作者名 -> %s" % name)
    print("=" * 66)

    changed_files, total_hits = 0, 0
    for path in iter_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # 二进制文件跳过

        new_text, hits = text, 0
        for old, new in replacements:
            hits += new_text.count(old)
            new_text = new_text.replace(old, new)

        if hits == 0:
            continue

        rel = path.relative_to(ROOT).as_posix()
        changed_files += 1
        total_hits += hits
        print("  [%2d 处] %s" % (hits, rel))
        if not args.dry_run:
            path.write_text(new_text, encoding="utf-8")

    # 重命名投稿目录：submission/YOUR-GITHUB-USERNAME -> submission/<用户名>
    old_dir = SUBMISSION_DIR / U_PH
    new_dir = SUBMISSION_DIR / username
    if old_dir.is_dir() and old_dir != new_dir:
        print("\n  [目录改名] submission/%s  ->  submission/%s" % (U_PH, username))
        if not args.dry_run:
            if new_dir.exists():
                print("     ⚠ 目标目录已存在，跳过（请手工确认）")
            else:
                old_dir.rename(new_dir)

    print("-" * 66)
    if changed_files == 0:
        print("没有发现占位符 —— 可能已经替换过了。")
    else:
        print("共 %d 个文件、%d 处替换%s。" % (changed_files, total_hits,
                                              "（未写盘）" if args.dry_run else ""))

    # 顺便配 git 身份
    if args.email and not args.dry_run:
        import subprocess
        subprocess.run(["git", "config", "--global", "user.name", name], check=False)
        subprocess.run(["git", "config", "--global", "user.email", args.email], check=False)
        print("git 全局身份已设为：%s <%s>" % (name, args.email))

    if not args.dry_run and changed_files:
        print("\n下一步：重跑构建脚本，让库文件里的 source 链接同步更新")
        print("    python tools/build_library.py")


if __name__ == "__main__":
    main()
