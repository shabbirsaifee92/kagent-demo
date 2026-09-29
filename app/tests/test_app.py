import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import app  # noqa: E402


class TestConnectCache:
    def test_absent_config_is_not_fatal(self):
        assert app.connect_cache("") is None

    def test_redis_is_supported(self):
        assert app.connect_cache("redis://cache:6379") == "redis"

    def test_unknown_backend_is_rejected(self):
        with pytest.raises(ValueError, match="unsupported cache backend"):
            app.connect_cache("mysql://db:3306")


class TestRenderPage:
    def test_includes_version(self):
        assert "9.9.9" in app.render_page("9.9.9", None)

    def test_shows_disabled_when_no_cache(self):
        assert "disabled" in app.render_page("1.0.0", None)

    def test_renders_the_button(self):
        html = app.render_page("1.0.0", "redis")
        assert app.BUTTON_LABEL in html
        assert app.BUTTON_COLOR in html


class TestChartDefaults:
    def test_app_starts_when_cache_url_is_empty(self):
        cache = app.connect_cache("")
        assert cache is None
        page = app.render_page(app.VERSION, cache)
        assert "disabled" in page
