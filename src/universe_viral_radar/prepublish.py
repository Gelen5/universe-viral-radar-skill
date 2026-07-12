from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .utils import write_json

PLATFORMS = ("xiaohongshu", "douyin", "wechat-channels")
VERDICTS = (
    "可以直接发布",
    "小改后发布",
    "建议重写",
    "不建议发布",
)

COMPLIANCE_PATTERNS = (
    "保证",
    "包过",
    "稳赚",
    "躺赚",
    "100%",
    "绝对",
    "永久",
    "无风险",
    "立刻暴富",
)
HARD_SELL_PATTERNS = (
    "私信我",
    "马上下单",
    "立即购买",
    "点我主页",
    "加我微信",
    "扫码领取",
    "抓紧报名",
)
EVIDENCE_PATTERNS = (
    "案例",
    "截图",
    "数据",
    "复盘",
    "评论",
    "客户",
    "实验",
    "过程",
    "亲测",
)
AUDIENCE_PATTERNS = (
    "如果你",
    "你是不是",
    "适合",
    "给",
    "做",
    "上班族",
    "老板",
    "宝妈",
    "新人",
)
TRIGGER_PATTERNS = (
    "别再",
    "很多人",
    "为什么",
    "其实",
    "真相",
    "低估",
    "踩坑",
    "不是",
    "只要",
    "结果",
)


@dataclass
class ReviewInput:
    platform: str
    title: str
    script: str
    cover_title: str
    caption: str
    hashtags: list[str]
    source_path: str


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _normalize_tags(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    text = str(raw)
    return [tag.strip() for tag in re.split(r"[\s,，]+", text) if tag.strip()]


def load_review_input(path: str, platform: str | None = None) -> ReviewInput:
    target = Path(path).expanduser().resolve()
    if not target.exists():
        raise FileNotFoundError(target)

    if target.suffix.lower() == ".json":
        payload = json.loads(_read_text(target))
        guessed_platform = platform or payload.get("platform")
        script = str(
            payload.get("script")
            or payload.get("body")
            or payload.get("content")
            or payload.get("text")
            or ""
        ).strip()
        review_input = ReviewInput(
            platform=_normalize_platform(guessed_platform),
            title=str(payload.get("title") or "").strip(),
            script=script,
            cover_title=str(payload.get("cover_title") or payload.get("coverTitle") or "").strip(),
            caption=str(payload.get("caption") or payload.get("description") or "").strip(),
            hashtags=_normalize_tags(payload.get("hashtags") or payload.get("tags")),
            source_path=str(target),
        )
    else:
        raw = _read_text(target).strip()
        if not raw:
            raise ValueError("Input file is empty.")
        review_input = ReviewInput(
            platform=_normalize_platform(platform),
            title="",
            script=raw,
            cover_title="",
            caption="",
            hashtags=[],
            source_path=str(target),
        )

    if not review_input.script:
        raise ValueError("Input script/body is empty.")
    return review_input


def _normalize_platform(platform: str | None) -> str:
    if not platform:
        raise ValueError("Platform is required. Use --platform or provide it in the JSON input.")
    value = platform.strip().lower()
    aliases = {
        "xhs": "xiaohongshu",
        "xiaohongshu": "xiaohongshu",
        "redbook": "xiaohongshu",
        "douyin": "douyin",
        "dy": "douyin",
        "wechat": "wechat-channels",
        "wechat-channels": "wechat-channels",
        "video-channel": "wechat-channels",
        "视频号": "wechat-channels",
        "小红书": "xiaohongshu",
        "抖音": "douyin",
    }
    normalized = aliases.get(value, value)
    if normalized not in PLATFORMS:
        raise ValueError(f"Unsupported platform: {platform}")
    return normalized


def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(pattern.lower() in lowered for pattern in patterns)


def _sentence_start(text: str, limit: int) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    return compact[:limit]


def _topic_phrase(data: ReviewInput) -> str:
    for candidate in (data.title, data.cover_title, data.caption, data.script):
        compact = re.sub(r"\s+", " ", candidate).strip()
        if compact:
            compact = compact.split("。")[0].split("\n")[0].strip("：:，,。！？!? ")
            return compact[:24] or "这个主题"
    return "这个主题"


def _line_count(text: str) -> int:
    return len([line for line in text.splitlines() if line.strip()])


def _common_review(data: ReviewInput) -> tuple[int, list[str], list[str]]:
    script = data.script
    title = data.title
    first_chunk = _sentence_start(script, 80)
    score = 100
    severe: list[str] = []
    general: list[str] = []

    if not _contains_any(script + "\n" + title, AUDIENCE_PATTERNS):
        score -= 12
        severe.append("目标用户不够明确，开头看不出这条内容到底讲给谁。")

    if len(first_chunk) > 70 and not _contains_any(first_chunk, TRIGGER_PATTERNS):
        score -= 10
        severe.append("开头偏慢，前段没有明显冲突、结果差或好奇缺口。")

    if len(script) < 80:
        score -= 12
        severe.append("正文过短，信息量不足，难以支撑开头承诺。")
    elif len(script) < 150:
        score -= 6
        general.append("正文偏短，可以再补一层例子、步骤或证据。")

    if not _contains_any(script, EVIDENCE_PATTERNS):
        score -= 8
        general.append("证据感偏弱，建议补案例、截图、数据或过程细节。")

    if _contains_any(script, COMPLIANCE_PATTERNS):
        score -= 25
        severe.append("存在绝对化或收益承诺类表达，合规风险较高。")

    sell_index = min([script.find(pattern) for pattern in HARD_SELL_PATTERNS if pattern in script] or [-1])
    if sell_index != -1 and sell_index < max(60, len(script) // 4):
        score -= 18
        severe.append("商业动作出现过早，广告感压过了内容价值。")
    elif sell_index != -1:
        score -= 6
        general.append("商业引导已经出现，建议再往后放，让价值交付更完整。")

    cta_hits = sum(script.count(pattern) for pattern in HARD_SELL_PATTERNS)
    if cta_hits >= 3:
        score -= 6
        general.append("CTA 偏多，建议只保留一个主要动作。")

    if _line_count(script) <= 1 and len(script) > 120:
        score -= 5
        general.append("脚本几乎没有分段，拍摄和字幕节奏会比较吃力。")

    return max(score, 0), severe, general


def _xhs_review(data: ReviewInput) -> tuple[int, list[str], list[str]]:
    score = 0
    severe: list[str] = []
    general: list[str] = []
    title = data.title

    if not title:
        score -= 10
        severe.append("缺少标题，小红书点击和搜索入口不完整。")
    else:
        if len(title) < 8 or len(title) > 24:
            score -= 6
            general.append("标题长度不够理想，建议压到更容易扫读的长度。")
        if not re.search(r"[0-9]|怎么|为什么|清单|模板|避坑|普通人|上班族", title):
            score -= 6
            general.append("标题里的结果、人群或具体问题不够突出。")

    if not data.cover_title:
        score -= 5
        general.append("缺少封面短标题，建议准备一条一眼能看懂的封面文案。")
    elif len(data.cover_title) > 16:
        score -= 4
        general.append("封面短标题偏长，第一眼记忆点不够集中。")

    if len(data.script) < 180:
        score -= 6
        general.append("正文的收藏价值偏弱，建议补步骤、案例或清单。")

    if not data.hashtags:
        score -= 4
        general.append("没有标签，搜索和人群归类信号偏弱。")
    elif len(data.hashtags) > 6:
        score -= 4
        general.append("标签偏多，容易分散主题。")

    return score, severe, general


def _douyin_review(data: ReviewInput) -> tuple[int, list[str], list[str]]:
    score = 0
    severe: list[str] = []
    general: list[str] = []
    opening = _sentence_start(data.script, 50)

    if len(opening) > 36 and not _contains_any(opening, TRIGGER_PATTERNS):
        score -= 10
        severe.append("前三秒抓停能力偏弱，开头没有明显刺激点。")

    if _line_count(data.script) < 3:
        score -= 8
        general.append("节奏层次偏少，建议拆成更清晰的口播段和字幕段。")

    if not re.search(r"[？?]|评论|你会|你选|你更|说说", data.script):
        score -= 6
        general.append("互动设计偏弱，评论区延展空间不够。")

    if not re.search(r"前3秒|前三秒|开头|第一句|第一屏|画面|镜头|字幕", data.script):
        score -= 5
        general.append("画面和字幕节奏提示偏少，执行时容易变成平口播。")

    return score, severe, general


def _wechat_review(data: ReviewInput) -> tuple[int, list[str], list[str]]:
    score = 0
    severe: list[str] = []
    general: list[str] = []
    opening = _sentence_start(data.script, 60)

    if not re.search(r"我是|我做|这些年|这几年|我见过|我发现|我们团队", opening):
        score -= 8
        general.append("开头身份感偏弱，视频号里信任建立会比较慢。")

    if not _contains_any(data.script, ("案例", "朋友", "客户", "经历", "场景", "复盘")):
        score -= 8
        severe.append("具体案例不足，难以建立微信生态需要的信任感。")

    if _contains_any(data.script, ("冲爆", "秒杀", "炸裂", "赶紧冲", "闭眼买")):
        score -= 12
        severe.append("表达过于抖音化或营销化，不利于熟人转发。")

    if not re.search(r"转给|发给|朋友圈|社群|公众号|私信聊|聊聊|留言", data.script):
        score -= 5
        general.append("缺少微信生态承接动作，转发和后续转化链路不够完整。")

    return score, severe, general


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _verdict(score: int, severe_count: int) -> str:
    if severe_count >= 3 or score < 45:
        return "不建议发布"
    if severe_count >= 2 or score < 65:
        return "建议重写"
    if severe_count >= 1 or score < 82:
        return "小改后发布"
    return "可以直接发布"


def _platform_label(platform: str) -> str:
    return {
        "xiaohongshu": "小红书",
        "douyin": "抖音",
        "wechat-channels": "视频号",
    }[platform]


def _suggestions(data: ReviewInput, verdict: str, severe: list[str], general: list[str]) -> dict[str, str]:
    topic = _topic_phrase(data)
    if data.platform == "xiaohongshu":
        new_opening = f"如果你也在为{topic}发愁，先别急着追热点，先把最容易踩坑的这一步看明白。"
        cover_title = (data.cover_title or f"{topic}避坑清单")[:16]
        caption = f"{topic}这件事，最怕一开始方向就错了。这次我把常见误区、可执行做法和判断标准整理成一版，方便你直接保存对照。"
        pinned = "如果你现在卡在选题、标题还是转化承接，直接留言你最卡的一步，我按评论区问题继续拆。"
    elif data.platform == "douyin":
        new_opening = f"很多人做{topic}，不是内容不够努力，而是前3秒根本没有让人停下来的理由。"
        cover_title = (data.cover_title or f"{topic}前3秒改法")[:16]
        caption = f"{topic}真正拉开差距的，往往不是多说，而是前几秒先把人留住。这里我把开头、节奏和评论承接一起拆开。"
        pinned = "你觉得这条内容最该加强的是开头、节奏还是评论承接？留言一个点，我按最高频问题继续改。"
    else:
        new_opening = f"如果你身边也有人正在经历{topic}，这条内容更适合慢一点讲清楚，而不是一上来就急着推销。"
        cover_title = (data.cover_title or f"{topic}这样讲更可信")[:16]
        caption = f"{topic}在视频号里更重要的不是刺激，而是让人愿意相信、愿意转给熟人、愿意继续聊下去。"
        pinned = "如果你准备把这类内容发到朋友圈或社群，可以留言你的场景，我给你补一句更适合转发的承接话术。"

    script_lines = [
        f"1. 开头直接点出人群和问题：{new_opening}",
        "2. 中段先给一个具体场景或案例，再解释为什么多数人会做错。",
        "3. 接着给出 2 到 3 个可执行动作，避免空泛结论。",
        "4. 最后只保留一个 CTA，让用户评论、留言或私信其中一个动作。",
    ]
    if severe:
        script_lines.insert(2, f"2.5 优先修掉最严重的问题：{severe[0]}")
    elif general:
        script_lines.insert(2, f"2.5 优先补强的一点：{general[0]}")

    return {
        "new_opening": new_opening,
        "optimized_script": "\n".join(script_lines),
        "cover_title": cover_title,
        "caption": caption,
        "pinned_comment": pinned,
        "verdict_note": verdict,
    }


def review_content(path: str, platform: str | None = None) -> dict[str, Any]:
    data = load_review_input(path, platform)
    common_score, common_severe, common_general = _common_review(data)
    platform_score = 0
    platform_severe: list[str] = []
    platform_general: list[str] = []

    if data.platform == "xiaohongshu":
        platform_score, platform_severe, platform_general = _xhs_review(data)
    elif data.platform == "douyin":
        platform_score, platform_severe, platform_general = _douyin_review(data)
    elif data.platform == "wechat-channels":
        platform_score, platform_severe, platform_general = _wechat_review(data)

    score = max(0, min(100, common_score + platform_score))
    severe = _dedupe(common_severe + platform_severe)
    general = _dedupe(common_general + platform_general)
    verdict = _verdict(score, len(severe))
    suggestions = _suggestions(data, verdict, severe, general)

    return {
        "platform": _platform_label(data.platform),
        "platform_key": data.platform,
        "source_path": data.source_path,
        "score": score,
        "verdict": verdict,
        "serious_issues": severe,
        "general_issues": general,
        "suggestions": suggestions,
    }


def review_to_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# 发布前检查",
        "",
        f"平台：{result['platform']}",
        f"综合得分：{result['score']}/100",
        f"发布结论：{result['verdict']}",
        "",
        "## 严重问题",
    ]
    serious = result["serious_issues"] or ["无"]
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(serious, start=1))
    lines.extend(["", "## 一般问题"])
    general = result["general_issues"] or ["无"]
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(general, start=1))
    lines.extend(
        [
            "",
            "## 建议修改",
            f"- 新开头：{result['suggestions']['new_opening']}",
            f"- 完整优化脚本：\n\n{result['suggestions']['optimized_script']}",
            f"- 封面短标题：{result['suggestions']['cover_title']}",
            f"- 发布配文：{result['suggestions']['caption']}",
            f"- 置顶评论：{result['suggestions']['pinned_comment']}",
            "",
        ]
    )
    return "\n".join(lines)


def run_prepublish_review(input_path: str, platform: str | None = None, output_path: str | None = None, output_format: str = "json") -> str:
    result = review_content(input_path, platform)
    if output_format not in {"json", "markdown"}:
        raise ValueError(f"Unsupported output format: {output_format}")

    rendered = json.dumps(result, ensure_ascii=False, indent=2) if output_format == "json" else review_to_markdown(result)
    if output_path:
        target = Path(output_path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        if output_format == "json":
            write_json(target, result)
        else:
            target.write_text(rendered + "\n", encoding="utf-8")
        return str(target)
    return rendered
