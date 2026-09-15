# 从零把项目发布到 GitHub（分步执行清单）

> 这份文档是**操作手册**，按顺序做完，项目就上线了：
> 有仓库、有 Release、有 GitHub Pages、能被别人搜到。
> 全程只需要 `git` 命令 + GitHub 网页，不需要本地装任何构建环境。

---

## 步骤 0：替换占位符（**最容易忘，先做**）

仓库里所有待你填的地方都用了统一占位符，全局搜一遍改掉：

| 占位符 | 替换成 | 出现位置 |
| --- | --- | --- |
| `hon668` | 你的 GitHub 用户名 | README / docs / CONTRIBUTING / tools / submission 目录名 |
| `hon668` | 你的名字或昵称 | `LICENSE`、`docs/pr-to-official-library.md` |
| `hon668` | 你的 GitHub 用户名 | `tools/build_library.py` 的 `source` 字段 |

**推荐做法**：用现成的脚本一把替换（会自动跳过 `.git` 和 `.workbuddy`）：

```bash
# ① 预演：只列出会改哪些文件，不写盘
python tools/setup_repo.py --username <你的GitHub用户名> --name "<你的名字>" --dry-run

# ② 确认无误后执行；带 --email 会顺便配好 git 提交身份
python tools/setup_repo.py --username hon --name "Hon" --email hon@example.com
```

脚本会连 `submission/hon668/` 这个**目录名**一起改掉（投稿官方库时路径必须和你的用户名一致）。

⚠️ 改完**必须重跑一次构建脚本**，库文件和示例图里的 `source` 链接才会同步更新：

```bash
python tools/build_library.py
```

> 不想用脚本也行：VS Code 打开项目 → <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>H</kbd> 全局替换，但别忘了目录改名。

---

## 步骤 1：新建 GitHub 仓库

1. 登录 GitHub → 右上角 **+** → **New repository**
2. 填写：

| 字段 | 填什么 |
| --- | --- |
| Repository name | `hvac-excalidraw-library` |
| Description | 手绘风格中央空调/HVAC 暖通 Excalidraw 素材库｜Hand-drawn HVAC components for Excalidraw |
| 可见性 | **Public**（做作品集、要开 Pages，必须公开） |
| Add a README file | ❌ **不要勾**（我们本地已经有 README 了，勾了会冲突） |
| .gitignore / license | ❌ 都不要选（本地已备好） |

3. 点 **Create repository**，页面会显示一个空仓库和一堆命令 —— 别管它，按步骤 2 走

---

## 步骤 2：本地初始化并首次推送

在项目文件夹里打开终端：

```bash
cd /d/workfiles/PRODUCT/小工具/hvac-excalidraw-library   # 换成你的实际路径

# 确认仓库状态：本项目工作目录已经执行过 git init -b main，跳过下面这行即可
# git init -b main          # 只有在别处新拷了一份、没有 .git 目录时才需要

# 先看一眼将要提交的文件，确认没有多余的临时文件
git status --short

git add .
git commit -m "chore: initial release v1.0.0

- 16 个手绘风格 HVAC 元件（冷机/冷却塔/AHU/FCU/水泵/板换/蓄冰槽/蓄冷罐/阀门/仪表等）
- 中文库 + 英文库双版本 .excalidrawlib
- 三张示例图纸与 SVG/PNG 预览图
- 构建脚本 tools/build_library.py
- 完整文档：README / CONTRIBUTING / VERSIONING / CHANGELOG / MIT LICENSE"

# 关联远程仓库（把 hon668 换成你的用户名）
git remote add origin https://github.com/hon668/hvac-excalidraw-library.git

git push -u origin main
```

> 刷新 GitHub 页面，文件应该都在了。
> `git add .` 不会把 `.workbuddy/`（本地会话笔记）推上去，`.gitignore` 里已经排除。

### 关于 Git 身份（如果 `git commit` 报错要求配置）

```bash
git config --global user.name  "你的名字"
git config --global user.email "你的邮箱@example.com"
```

> 或者跑步骤 0 的脚本时带上 `--email`，它会顺手配好。

### 关于 push 时要求输入密码

**本机已经配好了 Git Credential Manager（GCM 2.9.0），正常情况下不需要手工造 Token：**

首次 `git push` 时 GCM 会自动弹出浏览器窗口让你授权 GitHub → 点 **Authorize** 即可，
凭据随后缓存进 Windows 凭据管理器，之后推送不再需要输入任何东西。

> 若弹窗没出现（例如 `git push` 直接报 403 / `Authentication failed`），先确认配置还在：
> ```bash
> git config --global --list | grep credential
> # 应输出 credential.helper=manager
> ```
> 不在就补一条：`git config --global credential.helper manager`

**备选方案：Personal Access Token**（GCM 不可用时）

GitHub 从 2021 年起**不再接受账号密码**，必须用 Token 当密码：

1. GitHub 网页 → 右上角头像 → **Settings** → 左下 **Developer settings**
2. **Personal access tokens** → **Tokens (classic)** → **Generate new token (classic)**
3. Note 随便填（如 `hvac-library`），Expiration 建议 90 天，勾选 **`repo`** 权限
4. 生成后**立刻复制**那串 `ghp_xxxx`（离开页面就再也看不到了）
5. `git push` 时：Username 填你的 GitHub 用户名，**Password 粘贴那串 token**

**再备选：SSH**（一劳永逸，但配置步骤多）

```bash
ssh-keygen -t ed25519 -C "你的邮箱"        # 一路回车，密码可留空
cat ~/.ssh/id_ed25519.pub                  # 复制输出内容
```
把内容粘到 GitHub → **Settings → SSH and GPG keys → New SSH key**，之后远程地址改用
`git@github.com:用户名/hvac-excalidraw-library.git`。

> 查看 GCM 已存的账号：`git-credential-manager github list`

### 关于连不上 GitHub（中国大陆网络，必看）

**典型症状**，`git ls-remote` 或 `git push` 报：

```
fatal: unable to access 'https://github.com/...': Recv failure: Connection was reset
fatal: unable to access 'https://github.com/...': schannel: server closed abruptly (missing close_notify)
```

**原因**：git **不使用系统/浏览器的代理**。所以"浏览器能打开 github.com"不代表 git 能连上，
必须单独给 git 指定代理端口。

**三步排查**：

```bash
# ① 环境变量里有没有现成的代理
env | grep -i proxy

# ② 找本机正在监听的代理端口（常见 7890 / 7891 / 10828 / 10809 / 7897 ...）
netstat -ano | grep LISTENING | grep "127.0.0.1:"

# ③ 逐个探测哪个端口真能连上 GitHub —— 返回 200 的那个就是
curl -s -o /dev/null -w "%{http_code}\n" -x http://127.0.0.1:10828 https://github.com/
```

**配置**（把端口换成你探测到的那个）：

```bash
git config --global http.proxy  http://127.0.0.1:10828
git config --global https.proxy http://127.0.0.1:10828

# 验证：应当无报错（空仓库就是无输出）
git ls-remote --heads origin
```

**想取消代理**：

```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

> ⚠️ 配了代理之后，**代理软件必须开着**，否则 git 会报 `Failed to connect to 127.0.0.1 port 10828`。
> 如果你换用 SSH 方式（`git@github.com:...`），走的是 22 端口，代理配置对它无效，需要另外给 SSH 配 ProxyCommand。

---

## 步骤 3：打 tag（版本标记）

```bash
git tag -a v1.0.0 -m "HVAC 手绘素材库 v1.0.0：首发，16 个元件"
git push origin v1.0.0
```

> 用 `-a`（附注标签），会记录打标签的人和时间，比轻量标签更规范。

---

## 步骤 4：发布 Release（让别人能一键下载）

1. 仓库主页右侧 → **Releases** → **Draft a new release**
2. **Choose a tag** 下拉 → 选中刚推上去的 `v1.0.0`（如果没出现，点 `Create new tag on publish` 手动填 `v1.0.0`，目标分支选 `main`）
3. **Release title**：`v1.0.0`
4. **Describe this release**：把 `CHANGELOG.md` 里 `## [v1.0.0]` 那一整段复制进去
5. **Attach binaries**：把这两个文件拖进附件区
   ```
   library/hvac-excalidraw-library-zh-v1.0.0.excalidrawlib
   library/hvac-excalidraw-library-en-v1.0.0.excalidrawlib
   ```
6. 勾选 **Set as the latest release**
7. 点 **Publish release**

> ✅ 检查：仓库主页右侧出现 `Releases v1.0.0`，点进去能直接下载 `.excalidrawlib`。

---

## 步骤 5：开启 GitHub Pages（在线预览站点）

1. 仓库 → **Settings** → 左侧 **Pages**
2. **Source** 选 **Deploy from a branch**
3. **Branch** 选 `main`，文件夹选 **`/docs`**，点 **Save**
4. 等 1~2 分钟，刷新页面，顶部会出现绿色提示：*Your site is live at …*
5. 访问地址（把用户名换掉）：
   ```
   https://hon668.github.io/hvac-excalidraw-library/
   ```

> 如果页面显示 404：① 确认选的是 `/docs` 不是 `/root`；② 等几分钟（首次构建较慢）；
> ③ 检查 Actions 标签页有没有报错（`theme: jekyll-theme-cayman` 是 GitHub 内置主题，正常不会报错）。

---

## 步骤 6：仓库信息美化（5 分钟，作品集必备）

**Settings → General** 页面往下：

1. **Description** 填一句话简介（就是步骤 1 那句）
2. **Website** 填步骤 5 的 Pages 地址 —— 仓库主页右侧会显示链接
3. **Topics** 加上这些标签（提升被搜到的概率）：
   ```
   excalidraw  hvac  hand-drawn  diagram  architecture  engineering
   obsidian  excalidraw-library  mechanical-engineering  air-conditioning
   ```
4. 在 README 顶部徽章区确认链接里的用户名已替换

---

## 步骤 7：验证上线结果（自检清单）

- [ ] 仓库主页 README 能正常显示，预览图**没裂图**
- [ ] Release 页有 `v1.0.0`，附件能下载
- [ ] Pages 站点能打开，元件总览图显示正常
- [ ] Clone 下来 `python tools/build_library.py` 能跑通
- [ ] `.excalidrawlib` 拖进 <https://excalidraw.com> 能正常导入 16 个元件（**最关键的一步，务必亲自拖一次**）
- [ ] Obsidian 里 Load library 也能导入
- [ ] Topics 标签已设置

---

## 步骤 8（可选）：后续每个版本的固定动作

发新版本时按这个顺序走，不会乱：

```bash
# 1) 改元件 / 改文档
vim tools/build_library.py        # 改 VERSION = "1.1.0"

# 2) 重新生成全部产物
python tools/build_library.py

# 3) 删掉旧版库文件（历史版本由 Git 保存）
git rm library/hvac-excalidraw-library-*-v1.0.0.excalidrawlib

# 4) 更新 CHANGELOG.md、README 元件清单 / 徽章
# 5) 提交、推、打标签
git add .
git commit -m "feat(lib): add cooling tower, bump to v1.1.0"
git push origin main
git tag -a v1.1.0 -m "v1.1.0：新增冷却塔元件"
git push origin v1.1.0
# 6) 到 GitHub 网页发 Release + 上传新库文件
```

完整版本规则见 [VERSIONING.md](../VERSIONING.md)。

---

## 附：常见问题

| 问题 | 原因 / 解决 |
| --- | --- |
| `git push` 提示 `rejected / fetch first` | 远程有初始 commit（建仓库时勾了 README）。执行 `git pull origin main --allow-unrelated-histories` 合并后再推 |
| 推上去发现预览图裂了 | 图片路径大小写不对，或没 `git add` 成功。GitHub 区分大小写，本地 Windows 不区分 |
| 每次提交 JSON 都显示整个文件变了 | 已提供 `.gitattributes` 统一为 LF；若仍异常，检查编辑器是否自动改了换行符 |
| 想让别人一起维护 | Settings → Collaborators 邀请；或用 Issue 让大家提需求、提 PR |
| 想加英文说明方便外国人 | 复制一份 `README.en.md`，在 README 顶部互相加一行语言切换链接（可选，不急） |
