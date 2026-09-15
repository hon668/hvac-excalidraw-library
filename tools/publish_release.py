#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一次性发布脚本：调 GitHub REST API 完成
  1) 创建 Release v1.0.0（正文取自 CHANGELOG）
  2) 上传两个 .excalidrawlib 作为 Release 附件
  3) 填写仓库描述 / 主页 / Topics
  4) 开启 GitHub Pages（main 分支 /docs 目录）

凭据来源：本机 Git Credential Manager（git credential fill）。
作者：hon668  仅用于 hon668/hvac-excalidraw-library。
"""
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
OWNER = "hon668"
REPO = "hvac-excalidraw-library"
TAG = "v1.0.0"
RELEASE_TITLE = "v1.0.0 — 首发：16 个手绘 HVAC 元件"
PAGES_URL = "https://%s.github.io/%s/" % (OWNER, REPO)
DESCRIPTION = ("Hand-drawn Excalidraw component library for HVAC / central "
               "air-conditioning schematics — 16 native vector components, "
               "works with excalidraw.com and the Obsidian Excalidraw plugin.")
TOPICS = ["excalidraw", "hvac", "hand-drawn", "diagram", "obsidian",
          "excalidraw-library", "hvac-engineering", "mechanical-engineering",
          "engineering-diagram", "roughjs"]

TMP = pathlib.Path(tempfile.mkdtemp(prefix="gh_rel_"))


# ----------------------------------------------------------------------
def get_token():
    """从本机凭据管理器取 GitHub token（不打印内容）。"""
    p = subprocess.run(
        ["git", "credential", "fill"], cwd=str(ROOT),
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True, text=True)
    for line in p.stdout.splitlines():
        if line.startswith("password="):
            return line[len("password="):]
    sys.exit("[FATAL] 无法从凭据管理器取得 token")


TOKEN = get_token()


def api(method, url, payload=None, upload=None):
    """调 REST API。payload=dict 走 JSON；upload=文件路径 走二进制流。"""
    cmd = ["curl", "-sS", "-X", method,
           "-H", "Authorization: Bearer " + TOKEN,
           "-H", "Accept: application/vnd.github+json",
           "-H", "X-GitHub-Api-Version: 2022-11-28"]
    if upload:
        cmd += ["-H", "Content-Type: application/octet-stream",
                "--data-binary", "@" + upload]
    elif payload is not None:
        f = TMP / "req.json"
        f.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        cmd += ["-H", "Content-Type: application/json; charset=utf-8",
                "--data-binary", "@" + str(f)]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    out = (r.stdout or "").strip()
    try:
        return json.loads(out) if out else {}
    except Exception:
        return {"_raw": out[:600]}


def show(tag, res, keys):
    if res.get("message"):
        print("  [FAIL] %s -> %s" % (tag, res["message"]))
        return False
    info = " | ".join("%s=%s" % (k, res.get(k)) for k in keys if k in res)
    print("  [ OK ] %s -> %s" % (tag, info))
    return True


# ----------------------------------------------------------------------
print("=" * 66)
print("发布 %s/%s  release=%s" % (OWNER, REPO, TAG))
print("=" * 66)

# ---- 1) Release body：从 CHANGELOG 抽 v1.0.0 段落 ----
changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
lines = changelog.splitlines()
start = next(i for i, l in enumerate(lines) if l.startswith("## [%s]" % TAG))
section = "\n".join(lines[start + 1:]).strip()
body = """**首个正式版本** — 16 个手绘风格 HVAC 元件，全部为 Excalidraw 原生矢量元素
（rectangle / ellipse / line / text），兼容网页版 Excalidraw 与 Obsidian Excalidraw 插件。

### 📦 下载哪个？

| 文件 | 说明 |
| --- | --- |
| `hvac-excalidraw-library-zh-v1.0.0.excalidrawlib` | **中文标签**，日常画图用这个 |
| `hvac-excalidraw-library-en-v1.0.0.excalidrawlib` | 英文标签，投稿 Excalidraw 官方素材库用 |

### 导入方法

打开 <https://excalidraw.com> → 左下角**素材库**面板 → 点 **打开** → 选择下载的 `.excalidrawlib` 文件。
Obsidian 用户：把文件拖进 Excalidraw 插件，或放进 vault 后在插件设置里指定。

> 每个元件内部已分组，插入画布后可整体拖动，也可解组二次编辑。

---

%s
""" % section

print("\n[1/4] 创建 Release")
rel = api("POST", "https://api.github.com/repos/%s/%s/releases" % (OWNER, REPO),
          payload={"tag_name": TAG, "name": RELEASE_TITLE, "body": body,
                   "draft": False, "prerelease": False})
if not show("create release", rel, ["id", "tag_name", "html_url"]):
    sys.exit(1)
release_id = rel["id"]

# ---- 2) 上传两个 .excalidrawlib 附件 ----
print("\n[2/4] 上传 Release 附件")
assets = [
    ROOT / "library" / ("%s-zh-%s.excalidrawlib" % (REPO, TAG)),
    ROOT / "library" / ("%s-en-%s.excalidrawlib" % (REPO, TAG)),
]
for a in assets:
    if not a.exists():
        print("  [SKIP] 文件不存在:", a.name)
        continue
    up = api("POST",
             "https://uploads.github.com/repos/%s/%s/releases/%d/assets?name=%s"
             % (OWNER, REPO, release_id, a.name),
             upload=str(a))
    n = a.stat().st_size
    show("%s (%.0f KB)" % (a.name, n / 1024), up, ["id", "size", "state"])

# ---- 3) 仓库描述 / 主页 / Topics ----
print("\n[3/4] 填写仓库信息")
r1 = api("PATCH", "https://api.github.com/repos/%s/%s" % (OWNER, REPO),
         payload={"description": DESCRIPTION, "homepage": PAGES_URL})
show("description + homepage", r1, ["description", "homepage"])

r2 = api("PUT", "https://api.github.com/repos/%s/%s/topics" % (OWNER, REPO),
         payload={"names": TOPICS})
show("topics", r2, ["names"])

# ---- 4) 开启 GitHub Pages ----
print("\n[4/4] 开启 GitHub Pages")
pg = api("POST", "https://api.github.com/repos/%s/%s/pages" % (OWNER, REPO),
         payload={"source": {"branch": "main", "path": "/docs"}})
if pg.get("message") and "already" in str(pg["message"]).lower():
    print("  [INFO] Pages 之前已开启")
    pg = api("GET", "https://api.github.com/repos/%s/%s/pages" % (OWNER, REPO))
show("enable pages", pg, ["html_url", "status", "url"])

print("\n完成。Release: %s" % rel.get("html_url", "(未知)"))
print("Pages  ：%s" % PAGES_URL)
