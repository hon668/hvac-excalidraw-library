# library/ —— 素材库文件（核心资产）

这个目录就是本项目**真正值钱的部分**。

## 文件说明

| 文件 | 用途 | 谁用 |
| --- | --- | --- |
| `hvac-excalidraw-library-zh-v1.0.0.excalidrawlib` | **中文标签**版本（元件自带的文字标签是中文） | 自己画图、国内项目沟通 |
| `hvac-excalidraw-library-en-v1.0.0.excalidrawlib` | **英文标签**版本 | 投稿 Excalidraw 官方库；涉外项目、英文汇报 |

两个文件的图形完全一致，只有元件内的文字标签和元件名不同。

## 怎么用

**网页版 Excalidraw**：打开 <https://excalidraw.com> → 库面板（快捷键 <kbd>9</kbd>）→ Browse libraries → Open → 选文件

**Obsidian Excalidraw 插件**：把文件放进 Vault → 打开 Excalidraw 图 → 库面板 → Load library → 选文件

完整步骤见根目录 [README.md](../README.md) 第五节。

## 关于版本号

文件名里的 `v1.0.0` 必须和 `tools/build_library.py` 顶部的 `VERSION` 常量一致。
升级版本时：改常量 → 重跑脚本 → 删除旧版文件（历史版本由 Git 保存）。
规则见 [VERSIONING.md](../VERSIONING.md)。

## 文件格式速查

```jsonc
{
  "type": "excalidrawlib",
  "version": 2,                    // 库格式版本（2 = 支持元件命名）
  "source": "https://github.com/...",
  "libraryItems": [
    {
      "id": "…",                   // 元件唯一 ID
      "status": "published",
      "name": "冷水机组",            // 库面板里显示的名字
      "created": 1757923200000,    // 时间戳
      "elements": [ /* 原生 Excalidraw 元素数组，同组元素共享 groupIds */ ]
    }
  ]
}
```

> ⚠️ 不要手工编辑这个大文件（一个库有 16 个元件、185 个元素、几千行）。
> 要改元件请改 `tools/build_library.py`，或者用 Excalidraw 导入后改完再导出覆盖。

## 元件清单（16 个）

| 分组 | 元件 |
| --- | --- |
| 冷热源主机 | 冷水机组（双筒式）、冷却塔、空气处理机组 AHU、风机盘管 FCU |
| 水力与蓄能 | 循环水泵、板式换热器、蓄冰槽、蓄冷罐 |
| 阀件与仪表 | 蝶阀、截止阀、过滤器、压力表、温度传感器 |
| 风系统 | 风管风口、消声器、软接头 |

> 配色约定：描边 `#1e1e1e` · 冷却水/热水橙 `#e8590c` · 冷冻水/冷媒蓝 `#1971c2` · 风管绿 `#2f9e44` · 辅助线灰 `#868e96`。
> 实线 = 一次侧 / 供水，虚线 = 二次侧 / 回水。
