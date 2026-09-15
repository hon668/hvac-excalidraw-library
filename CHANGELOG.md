# 更新日志 CHANGELOG

本文件记录本项目所有值得注意的变更。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [Unreleased]

### 新增 Added
- `tools/submit_to_official.py` —— 一键投稿 Excalidraw 官方素材库（fork → 同步上游 → 单 commit 提交 3 个文件 → 开 PR），走 Git Data API，支持 `--dry-run` 只看 diff
- `tools/verify_pr.py` —— 投稿自检脚本：拉官方 `validate-libraries.js` 本地实跑、模拟 `gen-item-names` 抽取 itemNames、逐字节比对已上传文件
- `docs/pr-to-official-library.md` 补充：官方 CI 两个 workflow 的实测行为、校验规则全文逻辑、itemNames 生成机制、首次贡献者 checks 为空的说明

### 已投稿 Submitted
- 向 [excalidraw/excalidraw-libraries](https://github.com/excalidraw/excalidraw-libraries) 提交 PR [#2873](https://github.com/excalidraw/excalidraw-libraries/pull/2873)（英文库 16 元件），等待维护者评审

### 计划中 Planned
- 膨胀水箱 Expansion Tank
- 分水器 / 集水器 Header
- 电动调节阀 Motorized Control Valve
- 温控器 / 温控面板 Thermostat
- VAV 末端 / 散流板
- 多联机室外机 VRF Outdoor Unit

---

## [v1.0.0] - 2026-09-15

### 新增 Added
- 首个正式版本，包含 16 个手绘风格暖通元件：
  1. 冷水机组 Chiller（双筒式：上冷凝器 + 下蒸发器 + 顶置压缩机 + 四路接管）
  2. 冷却塔 Cooling Tower（收口塔体 + 顶部风机 + 两侧进风格栅 + 集水盘）
  3. 空气处理机组 AHU（五段式：混风 / 过滤 / 表冷 / 风机 / 送风）
  4. 风机盘管 FCU（含三档调速标识）
  5. 循环水泵 Circulation Pump（电机 + 联轴器 + 泵壳 + 叶轮 + 底座）
  6. 板式换热器 Plate Heat Exchanger（板片束 + 两侧四路接管）
  7. 蓄冰槽 Ice Storage Tank（槽体 + 乙二醇蛇形盘管 + 冰晶）
  8. 蓄冷罐 Chilled Water Tank（立式罐体 + 斜温层 + 7℃/12℃ 分层）
  9. 蝶阀 Butterfly Valve
  10. 截止阀 Globe Valve
  11. 过滤器 Strainer / Filter
  12. 压力表 Pressure Gauge
  13. 温度传感器 Temperature Sensor
  14. 风管风口 Duct Outlet / Diffuser
  15. 消声器 Duct Silencer
  16. 软接头 Flexible Connector
- 中文库 `hvac-excalidraw-library-zh-v1.0.0.excalidrawlib`
- 英文库 `hvac-excalidraw-library-en-v1.0.0.excalidrawlib`（用于投稿 Excalidraw 官方素材库）
- 示例图纸三张：
  - `01-chilled-water-system.excalidraw` 冷冻水系统原理图
  - `02-ahu-duct-layout.excalidraw` 空调箱风路接管示意
  - `03-ice-storage-system.excalidraw` 冰蓄冷系统原理图（冷却水 / 乙二醇 / 冷冻水三环路）
- 构建脚本 `tools/build_library.py`，一条命令可重新生成全部库文件、示例图纸与预览图
- 辅助脚本 `tools/setup_repo.py`，一条命令替换仓库里的用户名/作者名占位符并重命名投稿目录
- 完整文档：README、贡献指南、版本管理说明、Issue/PR 模板
- GitHub Pages 预览站点（`docs/`）

### 说明 Notes
- 全部元件均为 Excalidraw 原生矢量元素（rectangle / ellipse / line / text），无位图
- 统一 `roughness = 1` 手绘风格；配色约定：描边 `#1e1e1e`、冷却水/热水橙 `#e8590c`、冷冻水/冷媒蓝 `#1971c2`、风管绿 `#2f9e44`、辅助线灰 `#868e96`
- 环路区分线型：实线 = 一次侧 / 供水，虚线 = 二次侧 / 回水
- 每个元件内部元素已分组，插入画布后可整体拖动，亦可解组二次编辑
- 中文库为日常使用主库；**英文库用于向官方库投稿**（官方库只接受英文标签）
- 投稿材料已备好（`submission/` 文件包 + `docs/pr-to-official-library.md` PR 文案），待向 [excalidraw/excalidraw-libraries](https://github.com/excalidraw/excalidraw-libraries) 官方素材库提交 PR
