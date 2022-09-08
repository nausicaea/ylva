from ylva.conversion import convert_a_to_b, convert_ata_to_btb


def test_convert_a_to_b() -> None:
    lut = {
        "a": "0",
        "b": "1",
        "c": "2",
        "d": "3",
        "e": "4",
    }

    names = [
        "a",
        "b",
        "e",
        "c",
        "f",
    ]

    expected = [
        "0",
        "1",
        "4",
        "2",
    ]

    result = convert_a_to_b(names, lut)

    assert result == expected


def test_convert_ata_to_btb() -> None:
    lut = {
        "a": "0",
        "b": "1",
        "c": "2",
        "d": "3",
        "e": "4",
    }

    ntn = {
        "a": "b",
        "b": "a",
        "e": "c",
        "c": "f",
        "f": "f",
    }

    expected = {
        "0": "1",
        "1": "0",
        "4": "2",
    }

    result = convert_ata_to_btb(ntn, lut, lut)

    assert result == expected
