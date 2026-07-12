from universe_viral_radar.scoring import score_benchmark


def test_benchmark_score_tier():
    values = {
        "audience_overlap": 9,
        "stage_fit": 9,
        "recent_activity": 9,
        "viral_repeatability": 9,
        "content_replicability": 9,
        "monetization_clarity": 9,
        "creator_capability_fit": 9,
    }
    result = score_benchmark(values)
    assert result["score"] == 90.0
    assert result["tier"] == "主对标账号"
