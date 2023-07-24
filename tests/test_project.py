from check_filter import __app_name__, __version__, __author__


def test_name():
    assert __app_name__ == 'check-filter'


def test_version():
    assert __version__ == '2.0.1'


def test_author():
    assert __author__ == 'Arash Hatami <info@arash-hatami.ir>'
