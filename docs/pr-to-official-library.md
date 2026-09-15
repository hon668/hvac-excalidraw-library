# 投稿到 Excalidraw 官方素材库（libraries.excalidraw.com）操作手册

本文件是**投稿到官方素材库**的完整操作手册 + 可直接复制的 PR 文案。
（投稿官方库和本仓库维护是两件事：本仓库是"自己家的库"，官方库是"上架到 excalidraw.com 的公共图库"。）

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
