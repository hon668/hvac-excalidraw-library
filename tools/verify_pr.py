#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
投稿后自检：把官方仓库的 CI 校验脚本拉下来，对**已推送到 fork 的实际提交内容**跑一遍。

  1) 从 fork 的 PR 分支拉 libraries.json / .excalidrawlib / .png，确认 blob 正确落地
  2) 用官方 scripts/validate-libraries.js 实跑校验（等价于官方 CI 的 yarn validate:libraries）
  3) 模拟官方 scripts/gen-item-names.mjs 对本次条目的抽取，打印 itemNames

用法：python tools/verify_pr.py
作者：hon668
"""
import base64
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORK_OWNER = "hon668"
BRANCH = "add-hvac-handdrawn-library"
UPSTREAM_OWNER = "excalidraw"
UPSTREAM_REPO = "excalidraw-libraries"
FORK = "https://api.github.com/repos/%s/%s" % (FORK_OWNER, UPSTREAM_REPO)
UPSTREAM = "https://api.github.com/repos/%s/%s" % (UPSTREAM_OWNER, UPSTREAM_REPO)

NODE = r"C:\Users\Hon\.workbuddy\binaries\node\versions\22.22.2-2\node.exe"
WORK = ROOT / ".workbuddy" / "tmp" / "verify"
LIB_REL = "libraries/%s/hvac-handdrawn-components.excalidrawlib" % FORK_OWNER
PNG_REL = "libraries/%s/hvac-handdrawn-components.png" % FORK_OWNER


def get_token():
    p = subprocess.run(["git", "credential", "fill"], cwd=str(ROOT),
                       input="protocol=https\nhost=github.com\n\n",
                       capture_output=True, text=True)
    for line in p.stdout.splitlines():
        if line.startswith("password="):
            return line[len("password="):]
    sys.exit("[FATAL] 无法取得 token")


TOKEN = get_token()


def api(method, url):
    r = subprocess.run(
        ["curl", "-sS", "-X", method,
         "-H", "Authorization: Bearer " + TOKEN,
         "-H", "Accept: application/vnd.github+json",
         "-H", "X-GitHub-Api-Version: 2022-11-28", url],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "").strip()
    try:
        return json.loads(out) if out else {}
    except Exception:
        return {"_raw": out[:500]}


def fetch_file(repo, path, ref=None):
    """取远端文件原始字节。"""
    url = "%s/contents/%s" % (repo, path)
    if ref:
        url += "?ref=" + ref
    d = api("GET", url)
    if isinstance(d, list) or not d.get("content"):
        sys.exit("  [FATAL] 取不到 %s: %s" % (path, str(d)[:200]))
    return base64.b64decode(d["content"]), d.get("sha", "")


print("=" * 70)
print("投稿自检 —— fork=%s 分支=%s" % (FORK_OWNER, BRANCH))
print("=" * 70)

WORK.mkdir(parents=True, exist_ok=True)
(WORK / "scripts").mkdir(exist_ok=True)
(WORK / "libraries" / FORK_OWNER).mkdir(parents=True, exist_ok=True)

# ---- 1) 拉 PR 分支上的实际内容 ----
print("\n[1] 从 fork 分支拉取已提交内容")
raw_json, sha_json = fetch_file(FORK, "libraries.json", BRANCH)
raw_lib, sha_lib = fetch_file(FORK, LIB_REL, BRANCH)
raw_png, sha_png = fetch_file(FORK, PNG_REL, BRANCH)
print("  [ OK ] libraries.json                       %8.1f KB  sha=%s" % (len(raw_json) / 1024, sha_json[:10]))
print("  [ OK ] hvac-handdrawn-components.excalidrawlib %8.1f KB  sha=%s" % (len(raw_lib) / 1024, sha_lib[:10]))
print("  [ OK ] hvac-handdrawn-components.png        %8.1f KB  sha=%s" % (len(raw_png) / 1024, sha_png[:10]))

# 与本地源文件比对（确认上传没有损坏）
local_lib = (ROOT / "submission" / FORK_OWNER / "hvac-handdrawn-components.excalidrawlib").read_bytes()
local_png = (ROOT / "submission" / FORK_OWNER / "hvac-handdrawn-components.png").read_bytes()
print("  与本地源文件一致: lib=%s  png=%s"
      % (raw_lib == local_lib, raw_png == local_png))

# 落地，供 node 脚本使用
(WORK / "libraries.json").write_bytes(raw_json)
(WORK / LIB_REL).write_bytes(raw_lib)
(WORK / PNG_REL).write_bytes(raw_png)

# ---- 2) 拉官方校验脚本 ----
print("\n[2] 拉取官方 CI 校验脚本")
vjs, _ = fetch_file(UPSTREAM, "scripts/validate-libraries.js")
(WORK / "scripts" / "validate-libraries.js").write_bytes(vjs)
print("  [ OK ] scripts/validate-libraries.js (%d bytes)" % len(vjs))

# ---- 3) 实跑官方校验 ----
print("\n[3] 实跑官方校验（等价 CI 的 yarn validate:libraries）")
print("  cwd = %s" % WORK)
p = subprocess.run([NODE, "./scripts/validate-libraries.js"], cwd=str(WORK),
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
if p.returncode == 0:
    print("  [ OK ] 校验通过，无输出（与官方 CI 预期一致）")
else:
    print("  [FAIL] rc=%d" % p.returncode)
    print(p.stdout[-1500:])
    print(p.stderr[-1500:])
    sys.exit(1)

# ---- 4) 模拟 gen-item-names 抽取 ----
print("\n[4] 模拟官方 gen-item-names.mjs 对本次条目的抽取")
libs = json.loads(raw_json.decode("utf-8"))
mine = [l for l in libs if l.get("source", "").startswith(FORK_OWNER + "/")]
print("  我方条目数: %d" % len(mine))
if not mine:
    sys.exit("  [FATAL] libraries.json 里找不到 hon668 的条目")
entry = mine[0]
print("  name      : %s" % entry.get("name"))
print("  source    : %s" % entry.get("source"))
print("  preview   : %s" % entry.get("preview"))
print("  version   : %s" % entry.get("version"))
print("  authors   : %s" % json.dumps(entry.get("authors"), ensure_ascii=False))

libr = json.loads(raw_lib.decode("utf-8"))
print("  库文件 type      : %s" % libr.get("type"))
print("  库文件 libraryItems 数量: %d" % len(libr.get("libraryItems", [])))

names = [it.get("name") for it in libr.get("libraryItems", []) if it.get("name")]
print("  可提取的 itemNames: %d / %d" % (len(names), len(libr.get("libraryItems", []))))
for i, n in enumerate(names, 1):
    print("    %2d. %s" % (i, n))

missing = [i for i, it in enumerate(libr.get("libraryItems", [])) if not it.get("name")]
if missing:
    print("  [WARN] 以下元件没有 name（itemNames 会缺项）: %s" % missing)

# 官方库只接受英文：粗筛非 ASCII
non_ascii = [n for n in names if any(ord(ch) > 127 for ch in n)]
if non_ascii:
    print("  [WARN] 疑似非英文元件名: %s" % non_ascii)
else:
    print("  [ OK ] 全部元件名为纯 ASCII（英文）")

# ---- 5) 预览图完整性 ----
print("\n[5] 预览图检查")
sig = raw_png[:8]
print("  文件头: %s" % sig)
print("  [%s] PNG 魔数" % ("OK" if sig == b"\x89PNG\r\n\x1a\n" else "FAIL"))

print("\n" + "=" * 70)
print("自检完成：官方校验脚本通过，itemNames 可正常生成。")
print("=" * 70)
