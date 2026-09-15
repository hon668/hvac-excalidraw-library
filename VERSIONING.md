# 版本管理说明 VERSIONING

本文件说明两件事：**版本号怎么定**、**Release 怎么发**。

---

## 一、版本号规则（语义化版本）

格式：`v主版本号.次版本号.修订号`，例如 `v1.0.0`。

| 位置 | 名称 | 什么时候 +1 | 举例 |
| --- | --- | --- | --- |
| 第一位 | 主版本 MAJOR | **破坏性变更**：删除元件、重命名元件、改变数据结构导致旧文件/旧引用失效 | `v1.3.0 → v2.0.0` |
| 第二位 | 次版本 MINOR | **新增元件**，向后兼容 | `v1.0.0 → v1.1.0` |
| 第三位 | 修订 PATCH | **图形修正、微调描边、改文案**，不新增元件 | `v1.1.0 → v1.1.1` |

### 判断口诀

> **加东西 → 中间位；改错字/改线 → 末位；删东西/改名 → 首位。**

### 补充约定

- 版本号必须**同步出现在 4 个地方**（发布前逐项检查）：

| 位置 | 内容 |
| --- | --- |
| `tools/build_library.py` | 顶部 `VERSION = "1.1.0"` |
| `library/` 文件名 | `hvac-excalidraw-library-zh-v1.1.0.excalidrawlib`（旧版文件删除，历史版本由 Git 保存） |
| `CHANGELOG.md` | 新增一节 `## [v1.1.0] - 2026-XX-XX` |
| `README.md` | 徽章版本号 + 元件数量 |

- 尚未发布的功能在 CHANGELOG 里写作 `## [Unreleased]`。
- **不要**在 `library/` 里堆历史版本文件，Git tag 本身就是历史归档。

---

## 二、CHANGELOG 维护

采用 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 的分类方式：

```
## [v1.1.0] - 2026-10-01
### 新增 Added
- 新增「冷却塔 Cooling Tower」元件
### 变更 Changed
- 调整压力表刻度线数量，更接近真实表盘
### 修复 Fixed
- 修正循环水泵出口方向
```

每次 PR 合入时，把变更写进 `CHANGELOG.md` 的 `[Unreleased]` 段；发版时把它改名为具体版本号 + 日期。

---

## 三、Release 发布操作步骤

### 3.1 发布前检查清单

- [ ] `python tools/build_library.py` 跑通，无报错
- [ ] `docs/assets/preview-components.png` 已更新，肉眼确认元件都正常
- [ ] `library/` 下只保留最新版文件，文件名版本号正确
- [ ] `README.md`（元件清单表、徽章）、`CHANGELOG.md` 已更新
- [ ] 本地 `git status` 干净，改动已全部提交并推到 `main`

### 3.2 方式一：网页操作（推荐新手，可视化）

1. 打开仓库主页 → 右侧 **Releases** → **Draft a new release**
2. **Choose a tag** → 输入 `v1.1.0` → 点 **Create new tag: v1.1.0 on publish**
   （分支选 `main`）
3. **Release title** 填 `v1.1.0`（或 `HVAC 手绘素材库 v1.1.0`）
4. **Describe this release** 粘贴 CHANGELOG 里对应版本的段落
5. 把 `library/hvac-excalidraw-library-zh-v1.1.0.excalidrawlib` **拖到附件区上传**（这是给普通用户直接下载用的）
6. 需要的话勾选 **Set as the latest release**
7. 点 **Publish release**

### 3.3 方式二：命令行（推荐熟练后）

```bash
# 1) 确保 main 是最新
git checkout main
git pull origin main

# 2) 打附注标签（不要用轻量标签，附注标签会记录打标签的人和说明）
git tag -a v1.1.0 -m "HVAC 手绘素材库 v1.1.0：新增冷却塔元件"

# 3) 推送标签（这一步才真正把 tag 推到 GitHub）
git push origin v1.1.0

# 4) 在 GitHub 网页上基于该 tag 创建 Release，并把 .excalidrawlib 作为附件上传
```

> 如果打错了标签要重来：
> ```bash
> git tag -d v1.1.0                # 删本地
> git push origin :refs/tags/v1.1.0  # 删远端
> ```

### 3.4 附件命名建议

Release 附件统一用**带版本号**的名字，用户下载后不会混淆：

```
hvac-excalidraw-library-zh-v1.1.0.excalidrawlib
hvac-excalidraw-library-en-v1.1.0.excalidrawlib
```

---

## 四、常见问题

**Q：我改了元件但觉得不算"新功能"，该发版本吗？**
A：改了图形就发修订号（`v1.1.1`）。**每个 Release 都应该对应一次 tag**，别攒着不发，用户看不到更新会以为项目死了。

**Q：`.excalidrawlib` 里需要写版本号吗？**
A：文件本身只有 Excalidraw 的格式版本（`"version": 2`），**库自身的版本号靠文件名 + Git tag 体现**。

**Q：Obsidian 用户怎么知道有新版？**
A：两种方式——① 关注仓库的 Release（点 Watch → Custom → Releases）；② 在 CHANGELOG 里看。这也是为什么每次发版必须写 CHANGELOG。
