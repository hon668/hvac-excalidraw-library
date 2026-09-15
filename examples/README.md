# examples/ —— 示例图纸

用本库元件拼出来的完整示例，**目的不是给你抄，而是示范"这批元件怎么组合成一张像样的图"**。

## 文件清单

| 文件 | 内容 | 涉及元件 |
| --- | --- | --- |
| `01-chilled-water-system.excalidraw` | 冷冻水系统原理图。回路：冷水机组 → 蝶阀 → 过滤器 → 循环水泵 → 供水立管 → 末端（AHU + FCU），回水虚线回到冷机，并带压力表与两处温度测点 | 冷水机组、循环水泵、AHU、FCU、蝶阀、过滤器、压力表、温度传感器、软接头 |
| `02-ahu-duct-layout.excalidraw` | 空调箱风路接管示意。新风/回风 → AHU（过滤 → 表冷 → 风机）→ 软接头 → 消声器 → 送风干管 → 支管 → 两个风口 | AHU、软接头、消声器、风管风口 |
| `03-ice-storage-system.excalidraw` | 冰蓄冷系统原理图。**三个环路同图**：冷却水（橙实线，冷却塔→水泵→冷凝器→蝶阀→回塔）、乙二醇（蓝实线，蒸发器→泵→蓄冰槽盘管→板换一次侧→回冷机）、冷冻水（蓝虚线，板换二次侧⇄蓄冷罐） | 冷却塔、冷水机组、循环水泵 ×2、蝶阀、压力表、蓄冰槽、板式换热器、蓄冷罐、温度传感器、软接头 |

预览图：`docs/assets/preview-example-system.svg`、`docs/assets/preview-example-duct.svg`、`docs/assets/preview-example-ice.svg`

> 示例图的坐标是**逐个标定过的**：每条管线的端点都精确落在元件接管端头上，注释里记了端头坐标。
> 改布局时记得同步改 `tools/build_library.py` 里对应的坐标，**改完必须重新渲染预览确认管线接得上、没有压字**。
>
> 三张图各自的主轴：`01` 供水干管 `y=168` / 末端支管 `y=430` / 回水干管 `y=600`；`02` 风管轴 `y=180`；`03` 冷却水轴 `y=481`、乙二醇进 `y=527`、乙二醇回 `y=760`、冷冻水 `y=593/661`。

## 怎么打开

| 环境 | 操作 |
| --- | --- |
| 网页版 Excalidraw | 打开 <https://excalidraw.com>，把 `.excalidraw` 文件**直接拖进画布** |
| Obsidian Excalidraw 插件 | 把 `.excalidraw` 文件放进 Vault，双击打开 |

## 文件格式

`.excalidraw` 是 Excalidraw 的单张图纸格式（和 `.excalidrawlib` 素材库不同）：

```jsonc
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://github.com/…",
  "elements": [ /* 这张图上的所有元素 */ ],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": null },
  "files": {}
}
```

## 说明

- 示例图纸也是由 `tools/build_library.py` 生成的，改脚本可重出，保证与元件库版本同步
- 图里**每个设备实例都是独立分组**（点一下就能整体拖动），管线是单根线条，方便单独改走向
- 图纸只做**画法示范**，不追求工程深度；实际项目请按设计图纸和规范调整
- 欢迎把你用本库画的作品提 PR 放进这个目录（请先删掉项目名称、公司名等敏感信息）
