from ylva.conversion import convert_names_to_ids


def test_playground() -> None:
    class Entry:
        def __init__(self, n: str, i: str) -> None:
            self._name = n
            self._id = i

        def name(self) -> str:
            return self._name

        def id(self) -> str:
            return self._id

    lut = [
        Entry("a", "0"),
        Entry("b", "1"),
        Entry("c", "2"),
        Entry("d", "3"),
        Entry("e", "4"),
    ]

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

    result = convert_names_to_ids(names, lut)

    assert result == expected
