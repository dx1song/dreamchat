from app.services.zodiac import get_zodiac


def test_zodiac_normal():
    assert get_zodiac(4, 5) == "白羊座"
    assert get_zodiac(5, 15) == "金牛座"
    assert get_zodiac(6, 1) == "双子座"
    assert get_zodiac(7, 10) == "巨蟹座"
    assert get_zodiac(8, 5) == "狮子座"
    assert get_zodiac(9, 10) == "处女座"


def test_zodiac_boundary():
    assert get_zodiac(3, 21) == "白羊座"
    assert get_zodiac(4, 19) == "白羊座"
    assert get_zodiac(4, 20) == "金牛座"
    assert get_zodiac(9, 23) == "天秤座"


def test_zodiac_capricorn_cross_year():
    assert get_zodiac(12, 22) == "摩羯座"
    assert get_zodiac(12, 31) == "摩羯座"
    assert get_zodiac(1, 1) == "摩羯座"
    assert get_zodiac(1, 19) == "摩羯座"
    assert get_zodiac(1, 20) == "水瓶座"
