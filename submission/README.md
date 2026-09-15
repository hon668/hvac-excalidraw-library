# submission/ —— 投稿 Excalidraw 官方素材库的文件包

这个目录**不是给普通用户用的**，它是为了给 [excalidraw/excalidraw-libraries](https://github.com/excalidraw/excalidraw-libraries)
提 PR 而准备的文件，已经按官方仓库要求的格式放好了。

## 目录内容

```
submission/
└── hon668/                       ← 把目录名改成你自己的 GitHub 用户名
    ├── hvac-handdrawn-components.excalidrawlib  ← 英文库（官方只接受英文）
    └── hvac-handdrawn-components.png            ← 预览图（与库文件同名）
```

## 为什么单独准备一份

官方库有 4 条硬规则，我们这个目录是按规则裁剪过的版本：

| 官方规则 | 这里的做法 |
| --- | --- |
| 只接受英文标签 | 用的是 `-en-` 英文库，不是中文库 |
| 文件必须放在 `libraries/<用户名>/` 下 | 目录名改一下就能直接拷 |
| 必须提供 PNG/JPG 预览图 | `hvac-handdrawn-components.png` 已生成 |
| `libraries.json` 里的路径是相对 `libraries/` 的 | 提交时按手册写 |

## 操作

**完整操作手册 + 可直接复制的 PR 文案** → 见 [`docs/pr-to-official-library.md`](../docs/pr-to-official-library.md)

一句话版：

1. Fork `excalidraw/excalidraw-libraries`
2. 把本目录改名为你的 GitHub 用户名，整个拷进对方的 `libraries/` 下
3. 在 `libraries.json` 末尾追加一条元数据（手册里有现成的 JSON）
4. 提 PR，标题 `Add HVAC hand-drawn components library`

## 注意

- 本目录内容是**由 `tools/build_library.py` 自动生成的**，不要手工改这里的文件；改元件请改脚本后重跑。
- 官方库是"快照式"的：我们这边发新版后，需要重新提一次 PR 覆盖这两个文件。
