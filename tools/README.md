# tools/ —— 构建脚本

## 为什么用脚本而不是手绘导出？

手工维护 16 个元件 × 2 套语言 × 3 类产物（库文件 / 示例图 / 预览图）很容易漏改。
脚本生成的好处：

| 好处 | 说明 |
| --- | --- |
| 可复现 | 改配色、改线型、改标签文案，一条命令重出全部产物 |
| 中英同步 | 一次生成中文库 + 英文库，图形保证完全一致 |
| 易评审 | PR 里能看出元件是"怎么画出来的"，不是一张不知道来源的二进制 |
| 无依赖 | 只用 Python 标准库，不需要 `pip install` 任何东西 |

## 用法

```bash
# 在仓库根目录执行
python tools/build_library.py
```

Python 3.9+ 即可（用到 f-string 之外都是常规语法）。

## 会生成什么

```
library/hvac-excalidraw-library-zh-v1.0.0.excalidrawlib     ← 中文库
library/hvac-excalidraw-library-en-v1.0.0.excalidrawlib     ← 英文库
examples/01-chilled-water-system.excalidraw                 ← 示例图纸
examples/02-ahu-duct-layout.excalidraw
examples/03-ice-storage-system.excalidraw
docs/assets/preview-components.svg / .png                   ← 元件总览预览（中/英两版）
docs/assets/preview-components-en.svg / .png
docs/assets/preview-example-system.svg                      ← 三张示例图预览
docs/assets/preview-example-duct.svg
docs/assets/preview-example-ice.svg
submission/hon668/                            ← 投稿官方库的文件包
```

> PNG 预览图是靠调用本机已安装的 Chrome / Edge 无头模式把 SVG 截图得到的（官方库 PR 必须要 PNG）。
> 本机没装这两个浏览器时会打印 `[SKIP]`，SVG 仍然正常生成，你可以自己打开 SVG 另存为 PNG。

## 另一个脚本：setup_repo.py（上传 GitHub 前跑一次）

仓库里凡是需要填你自己信息的地方都用了统一占位符。这个脚本负责一次性替换掉，
并顺手把 `submission/hon668/` 目录改名（否则投稿时路径对不上）：

```bash
# 先预演，看看会改哪些文件
python tools/setup_repo.py --username <你的GitHub用户名> --name "<你的名字>" --dry-run

# 确认无误后执行（带 --email 会顺便配好 git 提交身份）
python tools/setup_repo.py --username hon668 --name "hon668" --email 329574003+hon668@users.noreply.github.com

# 替换完必须重跑构建，库文件里的 source 链接才会同步
python tools/build_library.py
```

## 第三个脚本：publish_release.py（发版时跑）

把「发 Release + 传附件 + 填仓库信息 + 开 Pages」这四件事压成一条命令，
走 GitHub REST API，不用在网页上点十几下。

```bash
python tools/publish_release.py
```

**它做四件事**：

| 步骤 | 调用的接口 | 说明 |
| --- | --- | --- |
| 1. 创建 Release | `POST /repos/{o}/{r}/releases` | 正文自动从 `CHANGELOG.md` 抽对应 tag 的段落，前面拼上下载说明 |
| 2. 上传附件 | `POST /uploads.github.com/.../assets` | 自动挂上 `library/` 里的中英两个 `.excalidrawlib` |
| 3. 仓库信息 | `PATCH /repos/{o}/{r}` + `PUT .../topics` | 描述、主页、Topics 一次配好 |
| 4. 开启 Pages | `POST /repos/{o}/{r}/pages` | 等价于 Settings → Pages 选 `main` + `/docs` |

**凭据从哪来？** 脚本用 `git credential fill` 读本机 **Git Credential Manager**
已存的 GitHub 凭据——所以**必须先成功 push 过一次**（GCM 那时才会记下凭据）。
脚本不会打印 token 内容。

> ⚠️ 两点注意：
> - 在**空仓库首次 push 之前**跑它没用，因为 GCM 里还没有凭据
> - 脚本里的 `OWNER` / `REPO` / `TAG` 是常量，**发下一个版本前记得改 `TAG`**，
>   并同步改 `RELEASE_TITLE` 和正文里的版本号

**不想用脚本 / GCM 没凭据？** 就按 `docs/setup-github-repo.md` 里的
步骤 3~6 在网页上手点一遍，效果完全一样。

## 第四个脚本：submit_to_official.py（投稿官方库）

把「fork 官方仓库 → 同步上游 main → 建分支 → 提交 3 个文件 → 开 PR」压成一条命令。
完整背景和踩坑说明见 [`docs/pr-to-official-library.md`](../docs/pr-to-official-library.md)。

```bash
# 先空跑：只读探查，打印 diff 统计，不改任何东西
python tools/submit_to_official.py --dry-run

# 确认 diff 干净（例如 `新增 16 行 / 删除 0 行`）后再真跑
python tools/submit_to_official.py
```

**它做九件事**：

| 步骤 | 调用的接口 | 说明 |
| --- | --- | --- |
| 1~2. fork 并等待就绪 | `POST /repos/{upstream}/forks` | 轮询直到 fork 可用（实测 3 秒），已存在则复用 |
| 3. 同步上游 | `POST /repos/{fork}/merge-upstream` | 避免基于落后的 main 建分支 |
| 4. 取基线 | `GET .../git/ref/heads/main` + `/git/commits/{sha}` | 拿到 base commit 与 tree |
| 5. 建 blob | `POST .../git/blobs` | 3 个文件走 base64 上传 |
| 6. 建 tree | `POST .../git/trees` | 一次挂上 2 个新文件 + 改动的 `libraries.json` |
| 7. 建 commit | `POST .../git/commits` | 单个 commit，而不是三个 |
| 8. 建分支 | `POST/PATCH .../git/refs` | 分支已存在则强制更新，可反复重跑 |
| 9. 开 PR | `POST /repos/{upstream}/pulls` | 已存在同名 PR 时会提示而不是报错 |

> 用 Git Data API 而不是逐个文件调 Contents API，是为了让 PR 里只有**一个 commit**，
> 评审者点开就能看全，不会被三个碎提交干扰。

## 第五个脚本：verify_pr.py（投稿自检）

不等官方 CI（首次贡献者的 workflow 需要维护者批准才会跑），
把官方仓库的 `scripts/validate-libraries.js` 拉下来**本地实跑**，并模拟 `gen-item-names.mjs`：

```bash
python tools/verify_pr.py
```

它会：

1. 从 fork 的 PR 分支拉回实际提交的 3 个文件，并与本地源文件**逐字节比对**（确认上传没损坏）
2. 用官方 `validate-libraries.js` 实跑校验 —— 与官方 CI 是同一份代码，结论等价
3. 模拟 `gen-item-names` 抽取 `itemNames`，打印 `可提取的 itemNames: 16 / 16`，并粗筛非 ASCII（官方库只收英文）
4. 校验预览图 PNG 魔数

## 代码结构速查

| 位置 | 作用 |
| --- | --- |
| 顶部常量区 | `STROKE / BLUE / ORANGE / GREEN / GRAY / LIGHT` 配色，`VERSION` 版本号 |
| 元素工厂 | `rect()` `ellipse()` `polyline()` `arrow()` `text()` `label()` |
| `c_xxx(zh)` | 每个元件一个函数，`zh=True` 出中文标签，`False` 出英文标签 |
| `COMPONENTS` | 元件注册表 —— **新增元件只要写函数 + 在这里加一行** |
| `build_library()` | 打包成 `.excalidrawlib`（自动分组、自动归零坐标） |
| `example_system()` / `example_duct()` / `example_ice()` | 三张示例图纸的拼装 |
| `render_svg()` / `render_png()` | 预览图生成 |
| `setup_repo.py` | 上传 GitHub 前替换占位符 + 重命名投稿目录（独立脚本） |
| `publish_release.py` | 发版：建 Release + 传附件 + 填仓库信息 + 开 Pages（独立脚本，走 REST API） |
| `submit_to_official.py` | 投稿官方库：fork + 一次 commit 提交 3 个文件 + 开 PR（独立脚本，走 Git Data API） |
| `verify_pr.py` | 投稿自检：拉官方校验脚本本地实跑 + 模拟 itemNames 抽取（独立脚本） |

## 新增一个元件的完整示例

```python
def c_cooling_tower(zh):
    """冷却塔：塔体 + 顶部风机 + 进/出水管"""
    els = [
        rect(0, 0, 140, 110, bg=LIGHT, rnd=False),          # 塔体
        ellipse(45, -14, 50, 28),                            # 顶部风机
        ellipse(60, -4, 20, 10, stroke=GRAY, sw=1.5),        # 风机轮毂
        polyline([[0, 96], [-30, 96]], stroke=BLUE, sw=2),   # 进水管
        polyline([[140, 96], [170, 96]], stroke=BLUE, sw=2), # 出水管
    ]
    for i in range(5):                                        # 进风格栅
        els.append(polyline([[14 + i * 26, 20], [14 + i * 26, 92]], stroke=GRAY, sw=1))
    els.append(label(70, 118, "冷却塔 Cooling Tower" if zh else "Cooling Tower", 16))
    return els

# 然后注册进列表
COMPONENTS = [
    ...,
    ("冷却塔", "Cooling Tower", c_cooling_tower),
]
```

跑 `python tools/build_library.py` → 打开 `docs/assets/preview-components.png` 肉眼确认 →
更新 README 清单和 CHANGELOG → 提 PR。

详细规范（配色、尺寸、分组要求）见 [CONTRIBUTING.md](../CONTRIBUTING.md) 第二节。
