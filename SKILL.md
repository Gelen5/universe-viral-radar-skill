---
name: universe-viral-radar
version: 0.1.0
description: Evidence-first viral video and benchmark creator analysis. Reads real video evidence through claude-video, optionally researches Xiaohongshu with redbook, extracts reusable mechanisms, maps monetization paths, and generates personalized short-video topics, scripts and pre-publish reviews.
argument-hint: <video-url-or-path | creator-profile | evidence-files> [goal]
allowed-tools: Bash, Read, Write, Glob, Grep, AskUserQuestion
homepage: https://github.com/Gelen5/universe-viral-radar-skill
repository: https://github.com/Gelen5/universe-viral-radar-skill
license: MIT
user-invocable: true
---

# 宇宙第一爆款雷达 Skill

不是凭空猜爆款，也不是照抄对标文案。

本 Skill 从真实视频、主页、公开数据和评论证据出发，完成六个任务：

1. 单条爆款视频深度拆解；
2. 对标博主分析；
3. 博主变现路径分析；
4. 爆款结构提取；
5. 个性化选题和脚本生成；
6. 发布前检查。

## 核心原则

先读 `references/evidence-rules.md`。所有输出都必须区分观察事实、证据推断和未知。禁止承诺必爆，禁止复制原作者完整内容。

## 运行入口

先解析用户意图，只进入最少必要流程：

- 给视频链接或本地视频：进入 **视频拆解**。
- 给博主主页、主页截图或账号数据：进入 **博主分析 + 变现分析**。
- 给多条爆款材料：进入 **结构提取**。
- 给拆解结果并要求自己的内容：进入 **个性化选题脚本**。
- 给待发布脚本：进入 **发布前检查**。
- 用户要求完整研究：按“证据采集 → 分析 → 结构 → 个性化 → 检查”依次执行。

## Step 0：环境检查

从当前 Skill 根目录运行：

```bash
python scripts/viral_radar.py doctor
```

### 视频能力

真实视频读取依赖单独安装的 `bradautomates/claude-video`：

```bash
npx skills add bradautomates/claude-video -g
```

本 Skill 不复制上游代码，而是自动寻找 `/watch` Skill 的 `scripts/watch.py`。支持环境变量：

```bash
CLAUDE_VIDEO_SKILL_DIR=/absolute/path/to/skills/watch
```

### 小红书可选连接器

```bash
npm install -g @lucasygu/redbook
redbook whoami
```

`redbook` 不是必需项。没有连接器时，要求用户提供主页截图、公开数据、字幕、评论和产品入口。不得因为连接器缺失而停止分析。

平台读取必须顺序执行，默认每次读取间隔约 20 秒，不并发、不绕过验证码或平台限制。

## Step 1：建立用户档案

若用户要生成个人化内容，先检查是否已有档案：

```bash
python scripts/viral_radar.py init-profile creator-profile.json
```

读取并补全 `creator-profile.json`。重点确认：身份、受众、内容主线、真实证据、表达习惯、产品、可用时间、拍摄方式和当前目标。

## Step 2：真实视频读取

```bash
python scripts/viral_radar.py video "<url-or-local-path>" --out workspaces/video-001 --detail balanced
```

针对前三秒或指定区间，使用：

```bash
python scripts/viral_radar.py video "<source>" --out workspaces/video-001-hook --start 0 --end 8 --max-frames 30 --resolution 1024
```

运行后必须：

1. 读取 `video-evidence.json`；
2. 读取 `claude-video-output.txt`；
3. 使用 `Read` 打开所有关键帧；
4. 将画面与时间戳字幕对应；
5. 再读取 `references/video-breakdown.md` 和 `references/viral-structure.md` 完成分析。

若链接下载失败，优先要求用户上传本地视频、字幕或关键截图，不要假装已看过视频。

## Step 3：小红书可选研究

搜索选题：

```bash
python scripts/viral_radar.py redbook search "<关键词>" --out workspaces/xhs-search
```

分析单条笔记：

```bash
python scripts/viral_radar.py redbook note "<fresh-web-url>" --out workspaces/xhs-note
```

读取博主：

```bash
python scripts/viral_radar.py redbook creator "<profile-url>" --out workspaces/xhs-creator --cooldown 20
```

提取 1—3 条共同结构：

```bash
python scripts/viral_radar.py redbook template "<url1>" "<url2>" --out workspaces/xhs-template
```

遵循上游规则：需要读取笔记时先搜索获取新鲜 URL；令牌可能过期；触发风控后停止并告知用户。

## Step 4：对标博主与变现分析

读取：

- `references/creator-analysis.md`
- `references/monetization-path.md`

先判断账号是否值得对标，再做内容地图和商业证据链。必须明确：

- 这个账号适合学什么；
- 哪些资源普通人学不了；
- 爆款是稳定机制还是单条异常；
- 已观察到的产品和入口；
- 推断的商业模式及置信度；
- 用户当前最值得执行的 1—3 个动作。

可使用评分脚本：

```bash
python scripts/viral_radar.py score-benchmark examples/benchmark-score-input.json
```

## Step 5：结构迁移与个性化生成

读取：

- `references/viral-structure.md`
- `references/personalized-script.md`
- 用户档案
- 视频和博主分析结果

结构迁移必须经过：

```text
原始内容 → 用户心理机制 → 抽象结构 → 删除原作者独有资产 → 匹配用户真实资产 → 生成原创版本
```

默认输出四类选题：流量、涨粉、信任、成交。重点选题给 15 秒、30 秒、60 秒脚本和完整发布包。

## Step 6：发布前检查

先读取 `references/prepublish-check.md` 作为总入口，再按以下顺序执行：

```text
用户选择平台
↓
通用短视频规则检查
↓
平台专项规则检查
↓
输出综合得分、严重问题、一般问题和修改稿
```

固定先读：

- `references/platforms/common-short-video-rules.md`
- `references/prepublish/common-checklist.md`

再按平台补读：

- 小红书：`references/platforms/xiaohongshu-rules.md` + `references/prepublish/xiaohongshu-checklist.md`
- 抖音：`references/platforms/douyin-rules.md` + `references/prepublish/douyin-checklist.md`
- 视频号：`references/platforms/wechat-channels-rules.md` + `references/prepublish/wechat-channels-checklist.md`

每条内容检查后必须输出：

- 平台；
- 综合得分；
- 发布结论；
- 严重问题；
- 一般问题；
- 建议修改；
- 新开头、完整优化脚本、封面短标题、发布配文、置顶评论。

发布结论只能使用四档：

1. **可以直接发布**
2. **小改后发布**
3. **建议重写**
4. **不建议发布**

严重的事实、合规、抄袭、信任崩塌或用户身份不匹配问题，必须降为“建议重写”或“不建议发布”。

## 构建完整上下文（可选）

需要把资料交给另一个 Agent 时：

```bash
python scripts/viral_radar.py build-context \
  --mode full \
  --profile creator-profile.json \
  --evidence workspaces/video-001/video-evidence.json \
  --evidence workspaces/xhs-creator/redbook-creator.json \
  --out workspaces/full-context.md
```

## 默认最终输出

```markdown
# 一句话结论

# 证据质量与缺口

# 单条视频拆解 / 对标博主分析

# 变现路径

# 爆款结构（可迁移 / 不可照搬）

# 个性化选题矩阵

# 重点脚本与拍摄方案

# 发布前检查

# 下一步最小验证动作
```

## 边界

- 不提供保证爆款、保证涨粉或保证成交的承诺。
- 不帮助绕过平台风控、登录保护、验证码或访问限制。
- 不复制完整受版权保护的视频脚本、文案或独有案例。
- 不把不可见的收入、价格和私域流程描述成事实。
- 只使用用户授权提供或公开可访问的数据。
