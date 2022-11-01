from superset_ext.main import app


def test_app_name() -> None:
    assert app.info.name == "superset"
