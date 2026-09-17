# 投稿到 Excalidraw 官方素材库（libraries.excalidraw.com）操作手册

本文件是**投稿到官方素材库**的完整操作手册 + 可直接复制的 PR 文案。
（投稿官方库和本仓库维护是两件事：本仓库是"自己家的库"，官方库是"上架到 excalidraw.com 的公共图库"。）

---

## 〇、当前投稿状态

| 项目 | 值 |
| --- | --- |
| PR | [#2873 — Add HVAC hand-drawn components library](https://github.com/excalidraw/excalidraw-libraries/pull/2873) |
| 提交时间 | 2026-09-15 |
| 来源分支 | `hon668:add-hvac-handdrawn-library` → `excalidraw:main` |
| 改动 | 3 个文件，`+8103 / -0`（`libraries.json` 仅末尾追加 16 行） |
| 状态 | `open` / `mergeable: true`，等待维护者评审 |
| 自检 | 官方 `validate-libraries.js` 已本地实跑通过；`gen-item-names` 可提取 16/16 元件名 |

**2026-09-17 复查**：仍为 `open`、`mergeable: true`、`commits: 1`（机器人尚未回填 `itemNames`），
无维护者评论、无 CI 运行记录 —— 属正常等待状态。

**已 fork 的仓库**：<https://github.com/hon668/excalidraw-libraries>（分支 `add-hvac-handdrawn-library`）

> 提完 PR 后本仓库再发新版，需要重新走一次流程覆盖官方仓库里的快照文件，
> 这时直接重跑 `tools/submit_to_official.py` 即可（脚本会复用已有 fork，并强制更新分支）。

---

## 一、投稿前必须知道的 4 条硬规则

官方库 [excalidraw/excalidraw-libraries](https://github.com/excalidraw/excalidraw-libraries) 的审核指南里明确写了：

| # | 规则 | 我们的应对 |
| --- | --- | --- |
| 1 | ⚠️ **只接受英文**：所有元件内的文字、库名称、描述都必须是英文 | 所以本仓库额外维护了**英文库** `hvac-excalidraw-library-en-v1.0.0.excalidrawlib`，投稿用它，**不要用中文库** |
| 2 | 至少 3 个元件，且同属一个类别 | 我们 16 个元件，同属 HVAC / 中央空调一类 ✅ |
| 3 | 一个元件由多个元素组成时**必须成组** | 构建脚本已对每个元件统一设置 `groupIds` ✅ |
| 4 | 不接受"只对自己有用"或"随手就能画"的图形（单个箭头、单个方块等） | 我们每个元件都是多元素设备级图形 ✅ |

另外还有两条软性要求：

- 预览图要是 **PNG / JPG**（我们的 `submission/` 目录已生成）
- 引用/搬运别人库里的元件必须做实质性改动（我们的元件全部是自绘代码生成的，无版权问题 ✅）

---

## 二、需要提交的 3 个东西

官方仓库的结构是：

```
excalidraw-libraries/
├── libraries.json                                  ← 要改：加一条库的元数据
└── libraries/
    └── <你的GitHub用户名>/                          ← 要加：新建这个目录
        ├── hvac-handdrawn-components.excalidrawlib  ← 英文库文件
        └── hvac-handdrawn-components.png            ← 预览图（PNG，与库文件同名）
```

> 注意：`libraries.json` 里的 `source` / `preview` 字段**是相对于 `libraries/` 目录的路径**，
> 不要写成 `libraries/xxx/...`，否则自动化工序读不到文件。

---

## 三、操作步骤

两条路选一条。**方式 A 是本次实际走的路**；方式 B 留着理解原理或手动补提时用。

### 方式 A：脚本一键搞定（推荐）

本仓库自带 `tools/submit_to_official.py`，用 GitHub REST + Git Data API 一气呵成
（凭据直接复用本机 Git Credential Manager，不落盘）：

```bash
# 1) 先空跑：只读探查，确认官方 libraries.json 格式、条目数、有没有重名条目
python tools/submit_to_official.py --dry-run

# 2) 真跑：fork → 同步上游 main → 建分支 → 一次 commit 提交 3 个变更 → 开 PR
python tools/submit_to_official.py

# 3) 自检：拉官方 CI 校验脚本本地实跑，并模拟 gen-item-names 抽取
python tools/verify_pr.py
```

`--dry-run` 会打印 diff 统计（例如 `新增 16 行 / 删除 0 行`），确认改动只落在文件末尾，
不会因为格式化差异产生整文件重排的大 diff。

脚本做对的几件事，手动做很容易踩：

| 坑 | 脚本的处理 |
| --- | --- |
| `libraries.json` 缩进是 2 空格、文件末尾带换行 | 序列化后与原文件逐行比对，`+16/-0` |
| `source` / `preview` 是**相对 `libraries/` 的路径** | 写成 `hon668/hvac-...`，不带 `libraries/` 前缀 |
| fork 刚建时 main 可能落后上游 | 先调 `merge-upstream` 同步，再基于最新 commit 建分支 |
| 逐个文件调 Contents API 会产生 3 个 commit | 走 Git Data API（blob → tree → commit → ref），**只有一个 commit** |
| 分支名已存在时新建会失败 | 检测到已有 ref 就 `PATCH` 强制更新 |

### 方式 B：手动操作

1. **Fork** [excalidraw/excalidraw-libraries](https://github.com/excalidraw/excalidraw-libraries)
2. Clone 到本地：
   ```bash
   git clone https://github.com/hon668/excalidraw-libraries.git
   cd excalidraw-libraries
   git checkout -b add-hvac-handdrawn-library
   ```
3. 新建目录并放入文件（直接把本仓库 `submission/hon668/` 里的两个文件拷过去，目录名改成你自己的 GitHub 用户名）：
   ```bash
   mkdir -p libraries/hon668
   cp <本仓库>/submission/hon668/* libraries/hon668/
   ```
4. 编辑 `libraries.json`，**在数组末尾追加**下面这条（记得把占位符换掉）：

```json
{
  "name": "HVAC Hand-drawn Components",
  "description": "Hand-drawn HVAC / central air-conditioning components: chiller, cooling tower, air handling unit, fan coil unit, circulation pump, plate heat exchanger, ice storage tank, chilled water tank, butterfly valve, globe valve, strainer, pressure gauge, temperature sensor, duct outlet, duct silencer, flexible connector.",
  "authors": [
    {
      "name": "hon668",
      "url": "https://github.com/hon668",
      "github": "https://github.com/hon668"
    }
  ],
  "source": "hon668/hvac-handdrawn-components.excalidrawlib",
  "preview": "hon668/hvac-handdrawn-components.png",
  "created": "2026-09-15",
  "updated": "2026-09-15",
  "version": 2
}
```

> `version: 2` 表示库内每个元件都有名字（我们的每个元件都有英文名）。
> `itemNames` 字段不用自己写，官方仓库的 GitHub Action 会跑 `scripts/gen-item-names.mjs` 自动提取并回填到你的 PR 分支上。

5. 提交并推送：
   ```bash
   git add .
   git commit -m "Add HVAC hand-drawn components library"
   git push origin add-hvac-handdrawn-library
   ```
6. 在 GitHub 上打开 PR，标题和正文用下一节的文案
7. 等自动化工序（机器人会在你的 PR 上补一个 commit 填 `itemNames`）
8. 维护者评审 → 通过后合并 → 你的库就会出现在 <https://libraries.excalidraw.com> 里

---

## 四、PR 文案（可直接复制）

### PR 标题

```
Add HVAC hand-drawn components library
```

### PR 正文（英文，官方仓库是英文项目）

```markdown
## Library submission

**Library name:** HVAC Hand-drawn Components
**Items:** 16
**Category:** HVAC / central air-conditioning schematics (mechanical engineering)

### What's in it

A set of hand-drawn (roughness = 1) components for drawing HVAC water/air system schematics:

| # | Item | What it contains |
|---|------|------------------|
| 1 | Chiller | shell, top-mounted compressor, upper condenser and lower evaporator shells, four pipe connections |
| 2 | Cooling Tower | tapered casing, top fan, side air-inlet louvers, collection basin |
| 3 | Air Handling Unit (AHU) | mixing / filter / cooling coil / fan / supply sections |
| 4 | Fan Coil Unit (FCU) | coil, centrifugal fan, 3-speed indication |
| 5 | Circulation Pump | motor, coupling, volute, impeller, suction & discharge, base |
| 6 | Plate Heat Exchanger | plate pack, two connections per side |
| 7 | Ice Storage Tank | tank shell with serpentine ethylene-glycol coil and ice symbols |
| 8 | Chilled Water Tank | vertical tank with thermocline and 7°C / 12°C stratification marks |
| 9 | Butterfly Valve | valve body, stem, lever handle |
| 10 | Globe Valve | valve body, stem, handwheel |
| 11 | Strainer / Filter | mesh frame with hatch pattern |
| 12 | Pressure Gauge | dial, needle, ticks, connection |
| 13 | Temperature Sensor | well, bulb, lead wire, "T" mark |
| 14 | Duct Outlet / Diffuser | duct, louvers, airflow arrows |
| 15 | Duct Silencer | casing with alternating baffles |
| 16 | Flexible Connector | flanges with corrugated flexible section |

### Files added

- `libraries/hon668/hvac-handdrawn-components.excalidrawlib`
- `libraries/hon668/hvac-handdrawn-components.png`
- one new entry appended to `libraries.json`

### Checklist

- [x] All texts and labels are in **English**
- [x] Each item is a **single group**, so it can be moved as one unit
- [x] More than 3 items, all within the **same category**
- [x] Items are generic and reusable far beyond my own use case
- [x] Every item is a **native vector element** (rectangle / ellipse / line / text) — no images
- [x] PNG preview provided, same base name as the library file
- [x] Nothing copied from other libraries
- [x] I agree to publish this under the repository's MIT license

### Notes

The components are generated programmatically from a small drawing script, so the geometry
and styling are consistent across the whole set (stroke `#1e1e1e`, cooling water / hot water
`#e8590c`, chilled water / refrigerant `#1971c2`, ducts `#2f9e44`, helper lines `#868e96`).
Solid lines are used for primary/supply and dashed lines for secondary/return branches.
Source: https://github.com/hon668/hvac-excalidraw-library

Happy to adjust naming, colors or item granularity based on your review.
```

---

## 五、投稿后可能被要求改什么（提前有个准备）

| 评审意见 | 我们的处理方式 |
| --- | --- |
| "元件太细/太复杂，缩小后看不清" | 减少内部构造线（如冷机换热管排），提高线条粗度 |
| "个别元件不需要自带标签文字" | 删掉元件内 `label()` 文本，只保留图形 |
| "希望按功能拆分，例如把阀门分成多个细类" | 新增元件，主版本号升到 v2.0.0 |
| "颜色建议统一为纯黑描边" | 把 `BLUE / GREEN / ORANGE` 常量改成 `#1e1e1e` 重新构建 |
| "预览图需要更高分辨率" | `tools/build_library.py` 里用 `--force-device-scale-factor=2` 重出 PNG |

所有改动都是改脚本 + 重跑一条命令的事，所以评审要求基本都能快速响应。

---

## 六、后续维护

- **官方库里的文件更新**：官方仓库是"快照式"的，我们这边发新版后，需要再到官方仓库提一次 PR 覆盖那两个文件（并更新 `libraries.json` 里的 `updated` 日期）。
- **别频繁提**：建议攒够一批改动（比如新增 3~5 个元件）再更新一次官方库，避免给维护者添麻烦。
- 提 PR 前先 `git pull upstream main` 同步，避免 `libraries.json` 冲突。

---

## 七、官方仓库的自动化工序（实测记录）

官方仓库 `.github/workflows/` 下有两个 workflow，都会在 PR 上触发：

| 文件 | 触发 | 干什么 |
| --- | --- | --- |
| `validate-libraries.yml` | `on: pull_request` | 跑 `yarn validate:libraries` → `node scripts/validate-libraries.js` |
| `process-libraries.yml` | `on: pull_request` | 跑 `node scripts/gen-item-names.mjs`，有 diff 就自动 `git push` 一个 `regenerate itemNames` commit 到你的分支 |

### 校验规则（`validate-libraries.js` 全文逻辑）

对我们这条条目而言，等价于：

1. `name` / `description` / `version` / `source` / `preview` / `created` / `updated` / `authors` **八个字段都非空**
2. 若填了 `id`，则**不能与其它条目重复**（我们没填 `id`，跳过）
3. `itemNames` 字段官方目前**注释掉了校验**（`// TODO re-enable once we add missing item names for old libs`），不需要自己写

### itemNames 是怎么来的

`gen-item-names.mjs` 的逻辑很短：

```js
for (const lib of libraries) {
  if (lib.version === 1) continue;
  const libraryData = JSON.parse(await readFile(`libraries/` + lib.source, "utf8"));
  lib.itemNames = libraryData.libraryItems.reduce((acc, item) => {
    if (item.name) acc.push(item.name);
    return acc;
  }, []);
}
await writeFile(PATH_LIBRARIES, JSON.stringify(libraries, null, 2));
```

三个直接推论：

- 它读的是 **`libraries/` + `lib.source`**，所以 `source` 字段**绝不能带 `libraries/` 前缀**，否则 CI 会读不到文件
- 它把 `version === 1` 的库跳过 —— 我们写 `version: 2`，所以会走这条分支，每个元件**必须有 `name`**
- 它用 `JSON.stringify(libraries, null, 2)` 写回，**不带末尾换行** —— 这解释了官方 `libraries.json` 的格式来源

对应地，本仓库的库文件必须保证 16 个 `libraryItems` 每个都有 `name`（英文），
`tools/verify_pr.py` 的 `[4]` 段就是专门模拟这一步的，会打印 `可提取的 itemNames: 16 / 16`。

### ⚠️ 首次贡献者：checks 一开始是空的，这是正常的

PR #2873 刚开出来时 `check-runs` 返回 0 条，`actions/runs` 也是 0。
这不是出错，而是 GitHub 对**首次向该仓库贡献的人**的默认安全策略 ——
workflow 需要维护者点一次 "Approve and run" 才会执行。

所以不要因为看不到 CI 结果就反复改提交。判断自己能不能过，
用 `python tools/verify_pr.py` **把官方校验脚本拉下来本地实跑**，这是同一份代码，结论等价。

### 评审节奏（观察值）

- 官方库当前约 232 个库，open issues 1800+（含 PR）
- 抽样看合并记录：从提交到合并可能是**数周量级**，也有被直接关闭的（部分是"与已有 PR 重复"）
- 结论：PR 提完就放着，别催。要继续推进就先做本仓库自己的事（补元件、发 v1.1.0）

---

## 八、本次投稿的完整命令回放

```bash
# 空跑，确认没有把 libraries.json 改乱
python tools/submit_to_official.py --dry-run

# 真跑
python tools/submit_to_official.py
#   [2] fork -> hon668/excalidraw-libraries (3s 就绪)
#   [3] merge-upstream -> none（已是最新）
#   [4] main commit=297a349eaf
#   [5] blob lib=ff1ab9e6c9  png=11f161b449  json=8bdb51d518
#   [6] tree=dce7be0c77
#   [7] commit=8377cf584c
#   [8] ref=refs/heads/add-hvac-handdrawn-library
#   [9] PR #2873 -> https://github.com/excalidraw/excalidraw-libraries/pull/2873

# 自检
python tools/verify_pr.py
#   [3] 官方 validate-libraries.js 实跑通过
#   [4] itemNames 16/16，全 ASCII
#   [5] PNG 魔数正确
```

---

## 九、合并前后：别人到底怎么用上你的库

这是投稿最容易误解的一点 —— **PR 合并之前，官方素材库网站上搜不到你的库，而且没有任何"提交审核入口"能让你提前上架**。

### 网站的数据从哪来（实测）

```bash
curl -s https://libraries.excalidraw.com/libraries.json | jq 'length'
# 232  ← 与官方仓库 main 分支 libraries.json 的条目数完全一致
```

网站就是读官方仓库 `main` 分支那份 `libraries.json` 渲染出来的。
所以判断"我的库上架了没"，不用刷网站，直接看 PR 状态就够了：

```bash
curl -s https://api.github.com/repos/excalidraw/excalidraw-libraries/pulls/2873 \
  | jq '{state, merged, mergeable}'
```

`merged: true` 之后网站就会出现在列表里（可按 `HVAC` 或作者 `hon668` 搜到），
此时官方页面会给出 **Add to Excalidraw** 按钮，点一下就是真正的一键安装。

### ⚠️ 关键坑：`#addLibrary` 直链有硬编码域名白名单

很多人（包括我）会想到"自己拼一个一键安装直链发给别人"，格式是：

```
https://excalidraw.com/#addLibrary=<库文件的公网URL>
```

**但这条路对自建仓库是走不通的。** Excalidraw 源码
`packages/excalidraw/data/library.ts` 里写着：

```js
/**
 * format: hostname or hostname/pathname
 *
 * Both hostname and pathname are matched partially,
 * hostname from the end, pathname from the start, with subdomain/path boundaries
 **/
const ALLOWED_LIBRARY_URLS = [
  "excalidraw.com",
  // when installing from github PRs
  "raw.githubusercontent.com/excalidraw/excalidraw-libraries",
];
```

匹配规则是 **hostname 从末尾部分匹配、pathname 从开头部分匹配**。于是：

| 你拼的直链 | 结果 |
| --- | --- |
| `raw.githubusercontent.com/excalidraw/excalidraw-libraries/...` | ✅ 放行（官方仓库，用于从 PR 安装） |
| `raw.githubusercontent.com/<你的用户名>/<你的仓库>/...` | ❌ 弹窗 `Invalid or disallowed library URL` |
| `https://<你的用户名>.github.io/...`（GitHub Pages） | ❌ 同上，不在白名单 |

**实测截图印证**：用无头浏览器打开自建库的 `#addLibrary` 直链，Excalidraw 会弹
「错误 — Invalid or disallowed library URL: `https://raw.githubusercontent.com/hon668/...`」。

> 这个白名单是客户端硬编码的，托管方式再怎么换都绕不过去。
> **在被官方库收录之前，唯一可靠的分享方式是"给下载链接，对方自己导入"。**

### 收录前后的分享策略

| 阶段 | 推荐分享方式 |
| --- | --- |
| **合并前**（现在） | 发 Release 下载直链：<br>`https://github.com/hon668/hvac-excalidraw-library/releases/latest/download/hvac-excalidraw-library-zh-v1.0.0.excalidrawlib`<br>对方下载 `.excalidrawlib` → Excalidraw 库面板 `Open` 导入 |
| **合并后** | 直接发 <https://libraries.excalidraw.com> 上的库页面链接，对方点 **Add to Excalidraw** 一键装 |

### 所以，想"方便让人用"，真正该做的事

1. **耐心等评审**（数周量级）—— 这是上架的唯一路径
2. 等待期间用 **下载直链 + 示例图预览** 让别人先看到效果、先能用起来
3. 想加快「被看见」，靠的不是催 PR，而是**把库本身做实用**：
   元件覆盖面、示例图纸质量、README 的搜索关键词


