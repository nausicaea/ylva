import tempfile

import pytest
from ofxstatement import ofx, plugin, ui


@pytest.mark.parametrize(
    "plugin_",
    [
        "mt940",
    ],
)
def test_playground(plugin_: str) -> None:
    appui = ui.UI()
    plg = plugin.get_plugin(plugin_, appui, dict())
    prs = plg.get_parser(
        "/Users/young0000/Crypt/Arkiv/2022/09/lohnkonto-20220912-20220921-mt940.sta"
    )
    stmt = prs.parse()
    stmt.assert_valid()

    with tempfile.TemporaryFile("wt") as f:
        wrtr = ofx.OfxWriter(stmt)
        f.write(wrtr.toxml())


def test_mt940_plugin_is_present() -> None:
    ps = dict(plugin.list_plugins())
    assert "mt940" in ps
