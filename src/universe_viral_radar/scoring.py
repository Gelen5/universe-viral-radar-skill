from __future__ import annotations

from typing import Any

from .utils import parse_cn_number

BENCHMARK_WEIGHTS = {
    "audience_overlap": 20,
    "stage_fit": 15,
    "recent_activity": 10,
    "viral_repeatability": 15,
    "content_replicability": 15,
    "monetization_clarity": 15,
    "creator_capability_fit": 10,
}


def weighted_score(values: dict[str, float], weights: dict[str, int]) -> float:
    score = 0.0
    for key, weight in weights.items():
        raw = float(values.get(key, 0))
        raw = min(max(raw, 0), 10)
        score += (raw / 10.0) * weight
    return round(score, 2)


def score_benchmark(values: dict[str, float]) -> dict[str, Any]:
    total = weighted_score(values, BENCHMARK_WEIGHTS)
    if total >= 80:
        tier = "主对标账号"
    elif total >= 65:
        tier = "相邻参考账号"
    elif total >= 45:
        tier = "单条内容样本"
    else:
        tier = "暂不推荐"
    return {"score": total, "tier": tier, "weights": BENCHMARK_WEIGHTS, "inputs": values}


def engagement_metrics(item: dict[str, Any]) -> dict[str, float | int]:
    likes = parse_cn_number(item.get("likes") or item.get("liked_count"))
    comments = parse_cn_number(item.get("comments") or item.get("comment_count"))
    saves = parse_cn_number(item.get("saves") or item.get("collected_count"))
    shares = parse_cn_number(item.get("shares") or item.get("share_count"))
    followers = parse_cn_number(item.get("followers") or item.get("follower_count"))
    denominator = max(likes, 1)
    return {
        "likes": likes,
        "comments": comments,
        "saves": saves,
        "shares": shares,
        "followers": followers,
        "comment_to_like": round(comments / denominator, 4),
        "save_to_like": round(saves / denominator, 4),
        "share_to_like": round(shares / denominator, 4),
    }
