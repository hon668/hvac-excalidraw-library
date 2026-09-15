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
python tools/setup_repo.py --username hon --name "Hon" --email hon@example.com

# 替换完必须重跑构建，库文件里的 source 链接才会同步
python tools/build_library.py
```

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
