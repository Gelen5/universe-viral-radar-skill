# 宇宙第一爆款雷达 Skill

> 从真实爆款和真实博主中，找到适合你迁移的内容结构与变现路径，并生成你能直接拍的选题和脚本。

## 第一版功能

- 单条爆款视频深度拆解
- 对标博主分析
- 博主变现路径分析
- 爆款结构提取
- 个性化选题和脚本生成
- 发布前检查

这不是“输入行业，随机生成 100 个标题”的提示词。它坚持先采集证据，再分析机制，最后结合创作者自己的身份、案例、产品和表达方式生成内容。

## 架构

```text
真实视频 / 主页 / 数据 / 评论
              ↓
claude-video 读取画面与字幕
redbook（可选）读取小红书公开数据
              ↓
证据标准化
              ↓
视频拆解 + 博主内容地图 + 商业证据链
              ↓
爆款结构抽象
              ↓
创作者个人档案匹配
              ↓
选题、脚本、拍摄方案、平台化发布检查
```

## 快速开始

### 1. 安装本仓库

```bash
git clone https://github.com/Gelen5/universe-viral-radar-skill.git
cd universe-viral-radar-skill
python -m pip install -e .
```

也可以不安装，直接使用：

```bash
python scripts/viral_radar.py doctor
```

### 2. 安装视频读取能力

```bash
npx skills add bradautomates/claude-video -g
```

`claude-video` 使用 `yt-dlp`、`ffmpeg`、原生字幕和可选 Whisper，把真实画面与带时间戳字幕交给 AI。平台链接支持情况取决于上游工具和平台当前规则；本地视频始终是更稳定的输入方式。

### 3. 可选安装小红书连接器

```bash
npm install -g @lucasygu/redbook
redbook whoami
```

请遵守平台规则。不要并发读取，不要高频抓取，不要绕过验证码。连接器不可用时，Skill 仍支持用户提供截图、字幕和公开数据完成分析。

### 4. 建立创作者档案

```bash
viral-radar init-profile creator-profile.json
```

填入身份、受众、内容支柱、真实案例、表达风格、产品和拍摄限制。

### 5. 读取一条视频

```bash
viral-radar video "https://example.com/video" \
  --out workspaces/video-001 \
  --detail balanced
```

重点分析前 8 秒：

```bash
viral-radar video "./video.mp4" \
  --out workspaces/video-hook \
  --start 0 --end 8 \
  --max-frames 30 \
  --resolution 1024
```

### 6. 小红书研究示例

```bash
viral-radar redbook search "AI变现" --out workspaces/search
viral-radar redbook creator "<profile-url>" --out workspaces/creator
viral-radar redbook note "<fresh-note-url>" --out workspaces/note
```

### 7. 发布前检查

发布前检查默认分三层：

```text
通用短视频规则
→ 平台专项规则
→ 综合评分与修改稿
```

当前内置平台：

- 小红书；
- 抖音；
- 视频号。

规则文件位于：

- `references/platforms/`
- `references/prepublish/`

### 8. 构建完整分析上下文

```bash
viral-radar build-context \
  --mode full \
  --profile creator-profile.json \
  --evidence workspaces/video-001/video-evidence.json \
  --evidence workspaces/creator/redbook-creator.json \
  --out workspaces/context.md
```

## Agent Skill 使用

支持 Agent Skills 的宿主可以读取根目录 `SKILL.md`。典型请求：

- “拆解这条视频为什么爆，重点看前三秒、完播和评论机制。”
- “分析这个博主的内容主线和变现路径，告诉我具体学什么。”
- “基于这 5 条爆款提取共同结构，不要仿写。”
- “结合我的创作者档案，生成 10 个选题和 3 条可直接拍的脚本。”
- “检查这条脚本是否值得发布，直接给我修改稿。”

## 目录

```text
SKILL.md                         Agent 工作流
references/                     六大功能的分析规则与平台发布规则
profiles/                       创作者档案模板
schemas/                        数据结构
src/universe_viral_radar/       Python 适配器与 CLI
scripts/viral_radar.py          无需安装的本地入口
examples/                       示例输入
THIRD_PARTY_NOTICES.md          开源项目说明
```

## 设计边界

- 不保证爆款、涨粉或成交。
- 不复制对标博主的完整脚本和独有案例。
- 商业模式分析必须标注观察事实、推断与未知。
- 不绕过平台限制。
- 仅使用用户授权材料或公开数据。

## 开源参考

见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。本仓库未直接打包第三方代码，第三方工具需要单独安装并遵守各自许可证与规则。

## License

MIT
