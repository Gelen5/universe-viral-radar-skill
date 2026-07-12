from universe_viral_radar.utils import parse_cn_number


def test_parse_cn_number():
    assert parse_cn_number("1.5万") == 15000
    assert parse_cn_number("2.4亿") == 240000000
    assert parse_cn_number("1,200") == 1200
    assert parse_cn_number(42) == 42
    assert parse_cn_number(None) == 0
