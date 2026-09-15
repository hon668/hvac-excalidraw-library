#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
投稿到 Excalidraw 官方素材库（excalidraw/excalidraw-libraries）的自动化脚本。

用 GitHub REST + Git Data API 一气呵成：
  1) fork excalidraw/excalidraw-libraries 到 hon668
  2) 把 fork 的 main 同步到上游最新（merge-upstream）
  3) 建分支 add-hvac-handdrawn-library，一次 commit 提交 3 个变更：
       - libraries/hon668/hvac-handdrawn-components.excalidrawlib   （新增）
       - libraries/hon668/hvac-handdrawn-components.png             （新增）
       - libraries.json                                             （末尾追加一条）
  4) 向上游仓库开 Pull Request

凭据来源：本机 Git Credential Manager（git credential fill），不落盘。
用法：
    python tools/submit_to_official.py --dry-run     # 只探查，不改任何东西
    python tools/submit_to_official.py               # 真正执行
作者：hon668
"""
import base64
import json
import pathlib
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent

UPSTREAM_OWNER = "excalidraw"
UPSTREAM_REPO = "excalidraw-libraries"
FORK_OWNER = "hon668"
BRANCH = "add-hvac-handdrawn-library"

LIB_FILE = "hvac-handdrawn-components.excalidrawlib"
PNG_FILE = "hvac-handdrawn-components.png"
SRC_DIR = ROOT / "submission" / FORK_OWNER

API = "https://api.github.com"
UPSTREAM = "%s/repos/%s/%s" % (API, UPSTREAM_OWNER, UPSTREAM_REPO)
FORK = "%s/repos/%s/%s" % (API, FORK_OWNER, UPSTREAM_REPO)

TMP = pathlib.Path(tempfile.mkdtemp(prefix="gh_submit_"))
DRY = "--dry-run" in sys.argv

ENTRY = {
    "name": "HVAC Hand-drawn Components",
    "description": (
        "Hand-drawn HVAC / central air-conditioning components: chiller, cooling tower, "
        "air handling unit, fan coil unit, circulation pump, plate heat exchanger, ice "
        "storage tank, chilled water tank, butterfly valve, globe valve, strainer, "
        "pressure gauge, temperature sensor, duct outlet, duct silencer, flexible connector."
    ),
    "authors": [
        {"name": FORK_OWNER,
         "url": "https://github.com/%s" % FORK_OWNER,
         "github": "https://github.com/%s" % FORK_OWNER}
    ],
    "source": "%s/%s" % (FORK_OWNER, LIB_FILE),
    "preview": "%s/%s" % (FORK_OWNER, PNG_FILE),
    "created": "2026-09-15",
    "updated": "2026-09-15",
    "version": 2,
}

PR_TITLE = "Add HVAC hand-drawn components library"

PR_BODY = """## Library submission

**Library name:** HVAC Hand-drawn Components
**Items:** 16
**Category:** HVAC / central air-conditioning schematics (mechanical engineering)

### What's in it

A set of hand-drawn (`roughness = 1`) components for drawing HVAC water/air system schematics:

| # | Item | What it contains |
|---|------|------------------|
| 1 | Chiller | shell, top-mounted compressor, upper condenser and lower evaporator shells, four pipe connections |
| 2 | Cooling Tower | tapered casing, top fan, side air-inlet louvers, collection basin |
| 3 | Air Handling Unit (AHU) | mixing / filter / cooling coil / fan / supply sections |
| 4 | Fan Coil Unit (FCU) | coil, centrifugal fan, 3-speed indication |
| 5 | Circulation Pump | motor, coupling, volute, impeller, suction & discharge, base |
| 6 | Plate Heat Exchanger | plate pack, two connections per side |
| 7 | Ice Storage Tank | tank shell with serpentine ethylene-glycol coil and ice symbols |
| 8 | Chilled Water Tank | vertical tank with thermocline and 7 degC / 12 degC stratification marks |
| 9 | Butterfly Valve | valve body, stem, lever handle |
| 10 | Globe Valve | valve body, stem, handwheel |
| 11 | Strainer / Filter | mesh frame with hatch pattern |
| 12 | Pressure Gauge | dial, needle, ticks, connection |
| 13 | Temperature Sensor | well, bulb, lead wire, "T" mark |
| 14 | Duct Outlet / Diffuser | duct, louvers, airflow arrows |
| 15 | Duct Silencer | casing with alternating baffles |
| 16 | Flexible Connector | flanges with corrugated flexible section |

### Files added

- `libraries/%s/%s`
- `libraries/%s/%s`
- one new entry appended to `libraries.json`

### Checklist

- [x] All texts and labels are in **English**
- [x] Each item is a **single group**, so it can be moved as one unit
- [x] More than 3 items, all within the **same category**
- [x] Items are generic and reusable far beyond my own use case
- [x] Every item is a **native vector element** (rectangle / ellipse / line / text) - no images
- [x] PNG preview provided, same base name as the library file
- [x] Nothing copied from other libraries
- [x] I agree to publish this under the repository's MIT license

### Notes

The components are generated programmatically from a small drawing script, so the geometry
and styling are consistent across the whole set (stroke `#1e1e1e`, cooling water / hot water
`#e8590c`, chilled water / refrigerant `#1971c2`, ducts `#2f9e44`, helper lines `#868e96`).
Solid lines are used for primary/supply and dashed lines for secondary/return branches.

Source: https://github.com/%s/hvac-excalidraw-library

Happy to adjust naming, colors or item granularity based on your review.
""" % (FORK_OWNER, LIB_FILE, FORK_OWNER, PNG_FILE, FORK_OWNER)


# ----------------------------------------------------------------------
def get_token():
    p = subprocess.run(["git", "credential", "fill"], cwd=str(ROOT),
                       input="protocol=https\nhost=github.com\n\n",
                       capture_output=True, text=True)
    for line in p.stdout.splitlines():
        if line.startswith("password="):
            return line[len("password="):]
    sys.exit("[FATAL] 无法从凭据管理器取得 token")


TOKEN = get_token()


def api(method, url, payload=None, upload=None):
    cmd = ["curl", "-sS", "-X", method,
           "-H", "Authorization: Bearer " + TOKEN,
           "-H", "Accept: application/vnd.github+json",
           "-H", "X-GitHub-Api-Version: 2022-11-28"]
    if upload:
        cmd += ["-H", "Content-Type: application/octet-stream",
                "--data-binary", "@" + upload]
    elif payload is not None:
        f = TMP / ("req_%d.json" % (time.time_ns() % 10 ** 9))
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
        return {"_raw": out[:800]}


def ok(tag, res, keys):
    if isinstance(res, dict) and res.get("message") and not res.get("id") \
            and not res.get("sha") and not res.get("object"):
        print("  [FAIL] %s -> %s" % (tag, res["message"]))
        return False
    info = " | ".join("%s=%s" % (k, res.get(k)) for k in keys if k in res)
    print("  [ OK ] %s -> %s" % (tag, info))
    return True


def get_json(url):
    return api("GET", url)


# ----------------------------------------------------------------------
print("=" * 70)
print("投稿 Excalidraw 官方素材库  %s -> %s/%s" % (FORK_OWNER, UPSTREAM_OWNER, UPSTREAM_REPO))
print("模式：%s" % ("DRY-RUN（只探查）" if DRY else "执行"))
print("=" * 70)

# ---- 0) 本地投稿文件检查 ----
print("\n[0] 本地文件检查")
for f in (SRC_DIR / LIB_FILE, SRC_DIR / PNG_FILE):
    if not f.exists():
        sys.exit("  [FATAL] 缺少文件: %s" % f)
    print("  [ OK ] %s (%.0f KB)" % (f.name, f.stat().st_size / 1024))

# ---- 1) 取上游 libraries.json，确认格式与是否已收录 ----
print("\n[1] 读取上游 libraries.json")
res = get_json("%s/contents/libraries.json" % UPSTREAM)
if res.get("message"):
    sys.exit("  [FATAL] 读取失败: %s" % res["message"])
raw = base64.b64decode(res["content"]).decode("utf-8")
data = json.loads(raw)
base_sha = res["sha"]
print("  条目数: %d | 文件 %.0f KB | sha=%s" % (len(data), len(raw) / 1024, base_sha[:10]))

hdr = raw[:2]
tail = raw.rstrip()[-40:]
print("  缩进: %s | 末尾: %r" % ("2 空格" if hdr == "[\n" else repr(hdr), tail))

dupes = [d for d in data if FORK_OWNER in json.dumps(d.get("source", "") + d.get("preview", "")
         + d.get("name", ""), ensure_ascii=False)]
if dupes:
    print("  [WARN] 已存在疑似同作者条目: %s" % [d.get("name") for d in dupes])
else:
    print("  [ OK ] 尚无 %s 的条目，可以追加" % FORK_OWNER)

print("  最后一条示例:")
print("    " + json.dumps(data[-1], ensure_ascii=False)[:300])

# 生成新内容：保持 2 空格缩进 + 沿用原文件的末尾换行风格（官方文件不带末尾换行）
data.append(ENTRY)
new_raw = json.dumps(data, indent=2, ensure_ascii=False)
if raw.endswith("\n"):
    new_raw += "\n"
print("  追加后条目数: %d | 新版 %.0f KB" % (len(data), len(new_raw) / 1024))
print("  末尾换行: 原=%s 新=%s（应一致）"
      % (raw.endswith("\n"), new_raw.endswith("\n")))

if DRY:
    # 确认改动只落在文件末尾（避免整文件重排导致的巨大 diff）
    import difflib
    old_lines = raw.splitlines()
    new_lines = new_raw.splitlines()
    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm="", n=1))
    added = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
    removed = [l for l in diff if l.startswith("-") and not l.startswith("---")]
    print("\n  diff 检查: 新增 %d 行 / 删除 %d 行" % (len(added), len(removed)))
    print("  --- diff 摘要（前 6 行 / 后 3 行）---")
    for l in diff[:6]:
        print("    " + l[:120])
    if len(diff) > 9:
        print("    ...")
        for l in diff[-3:]:
            print("    " + l[:120])

    print("\nDRY-RUN 结束，未做任何改动。")
    print("计划提交：")
    print("  libraries/%s/%s" % (FORK_OWNER, LIB_FILE))
    print("  libraries/%s/%s" % (FORK_OWNER, PNG_FILE))
    print("  libraries.json  (+1 条)")
    sys.exit(0)

# ---- 2) fork ----
print("\n[2] Fork 上游仓库")
fr = get_json(FORK)
if fr.get("id"):
    print("  [ OK ] fork 已存在: %s" % fr.get("full_name"))
else:
    r = api("POST", "%s/forks" % UPSTREAM, payload={})
    if not ok("create fork", r, ["full_name", "id"]):
        sys.exit(1)
    print("  等待 GitHub 完成 fork ...")
    for i in range(40):
        time.sleep(3)
        fr = get_json(FORK)
        if fr.get("id"):
            print("  [ OK ] fork 就绪 (%ds): %s" % ((i + 1) * 3, fr.get("full_name")))
            break
    else:
        sys.exit("  [FATAL] fork 超时未就绪")

# ---- 3) 同步 fork 的 main 到上游最新 ----
print("\n[3] 同步 fork 的 main 到上游最新")
mu = api("POST", "%s/merge-upstream" % FORK, payload={"branch": "main"})
if mu.get("message") and "not" not in str(mu.get("message")).lower():
    print("  [INFO] merge-upstream: %s" % mu.get("message"))
else:
    print("  [ OK ] merge-upstream: %s" % mu.get("merge_type", mu.get("message", "done")))

# ---- 4) 取 main 的 commit / tree ----
print("\n[4] 取 fork main 的最新 commit")
ref = get_json("%s/git/ref/heads/main" % FORK)
if not ref.get("object"):
    sys.exit("  [FATAL] 取不到 main ref: %s" % ref)
head_commit = ref["object"]["sha"]
cm = get_json("%s/git/commits/%s" % (FORK, head_commit))
base_tree = cm["tree"]["sha"]
print("  [ OK ] commit=%s" % head_commit[:10])
print("  [ OK ] tree  =%s" % base_tree[:10])

# ---- 5) 建 blob ----
print("\n[5] 上传 3 个 blob")


def mk_blob(path, is_text=False):
    content = path.read_text(encoding="utf-8") if is_text else None
    if is_text:
        b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
    else:
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    r = api("POST", "%s/git/blobs" % FORK,
            payload={"content": b64, "encoding": "base64"})
    if not r.get("sha"):
        sys.exit("  [FATAL] blob 失败 %s: %s" % (path.name, r))
    print("  [ OK ] %-46s sha=%s" % (path.name, r["sha"][:10]))
    return r["sha"]


tmp_libjson = TMP / "libraries.json"
tmp_libjson.write_text(new_raw, encoding="utf-8", newline="\n")

blob_lib = mk_blob(SRC_DIR / LIB_FILE)
blob_png = mk_blob(SRC_DIR / PNG_FILE)
blob_json = mk_blob(tmp_libjson, is_text=True)

# ---- 6) 建 tree ----
print("\n[6] 建 tree")
tree = {
    "base_tree": base_tree,
    "tree": [
        {"path": "libraries/%s/%s" % (FORK_OWNER, LIB_FILE), "mode": "100644",
         "type": "blob", "sha": blob_lib},
        {"path": "libraries/%s/%s" % (FORK_OWNER, PNG_FILE), "mode": "100644",
         "type": "blob", "sha": blob_png},
        {"path": "libraries.json", "mode": "100644", "type": "blob", "sha": blob_json},
    ],
}
tr = api("POST", "%s/git/trees" % FORK, payload=tree)
if not tr.get("sha"):
    sys.exit("  [FATAL] tree 失败: %s" % tr)
print("  [ OK ] tree=%s" % tr["sha"][:10])

# ---- 7) 建 commit ----
print("\n[7] 建 commit")
commit_msg = """Add HVAC hand-drawn components library

16 hand-drawn (roughness = 1) HVAC / central air-conditioning components,
all native vector elements (rectangle / ellipse / line / text):
chiller, cooling tower, AHU, FCU, pump, plate heat exchanger, ice storage
tank, chilled water tank, butterfly valve, globe valve, strainer, pressure
gauge, temperature sensor, duct outlet, duct silencer, flexible connector.

Source: https://github.com/%s/hvac-excalidraw-library""" % FORK_OWNER
c = api("POST", "%s/git/commits" % FORK,
        payload={"message": commit_msg, "tree": tr["sha"], "parents": [head_commit]})
if not c.get("sha"):
    sys.exit("  [FATAL] commit 失败: %s" % c)
print("  [ OK ] commit=%s" % c["sha"][:10])

# ---- 8) 建分支 ref ----
print("\n[8] 建分支 %s" % BRANCH)
ex = get_json("%s/git/ref/heads/%s" % (FORK, BRANCH))
if ex.get("object"):
    r = api("PATCH", "%s/git/refs/heads/%s" % (FORK, BRANCH),
            payload={"sha": c["sha"], "force": True})
    ok("update ref", r, ["ref"])
else:
    r = api("POST", "%s/git/refs" % FORK,
            payload={"ref": "refs/heads/%s" % BRANCH, "sha": c["sha"]})
    ok("create ref", r, ["ref"])

# ---- 9) 开 PR ----
print("\n[9] 开 Pull Request")
pr = api("POST", "%s/pulls" % UPSTREAM,
         payload={"title": PR_TITLE, "head": "%s:%s" % (FORK_OWNER, BRANCH),
                  "base": "main", "body": PR_BODY,
                  "maintainer_can_modify": True})
if pr.get("html_url"):
    print("  [ OK ] PR #%s -> %s" % (pr.get("number"), pr["html_url"]))
else:
    # 可能已存在
    lst = api("GET", "%s/pulls?state=all&head=%s:%s" % (UPSTREAM, FORK_OWNER, BRANCH))
    if isinstance(lst, list) and lst:
        print("  [INFO] PR 已存在: %s" % lst[0].get("html_url"))
    else:
        print("  [FAIL] 开 PR 失败: %s" % pr)

print("\n" + "=" * 70)
print("完成。后续：官方仓库 GitHub Action 会自动往 PR 分支补一个 commit 填 itemNames，")
print("然后等维护者评审合并。")
print("=" * 70)
