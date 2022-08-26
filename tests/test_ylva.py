import mt940
from ylva import __version__


def test_version():
    assert __version__ == '0.1.0'


def test_load_mt940() -> None:
    with open("/Users/young0000/Downloads/lohnkonto-20220401-20220823-mt940.sta") as f:
        data = mt940.parse(f)
        print(data)
