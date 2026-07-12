import json
from pathlib import Path

from universe_viral_radar.prepublish import review_content


def test_xiaohongshu_review_flags_missing_title_and_tags(tmp_path: Path):
    payload = {
        "platform": "xiaohongshu",
        "script": "如果你是刚开始做副业的上班族，这条内容先讲一个真实案例，再告诉你怎么少走弯路。",
    }
    path = tmp_path / "draft.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    result = review_content(str(path))
    assert result["platform"] == "小红书"
    assert result["score"] < 100
    assert any("标题" in issue for issue in result["serious_issues"])


def test_wechat_review_marks_marketing_tone_as_serious(tmp_path: Path):
    payload = {
        "platform": "wechat-channels",
        "title": "这个观点很多人都误解了",
        "script": "赶紧冲，这波闭眼买。我是做私域的，今天直接告诉你怎么立刻暴富，马上下单就行。",
    }
    path = tmp_path / "wechat.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    result = review_content(str(path))
    assert result["platform"] == "视频号"
    assert result["verdict"] in {"建议重写", "不建议发布"}
    assert any("营销化" in issue or "合规" in issue for issue in result["serious_issues"])
