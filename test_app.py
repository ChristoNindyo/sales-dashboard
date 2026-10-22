"""UI smoke tests using Streamlit's built-in testing tool. Run with:  pytest"""
from streamlit.testing.v1 import AppTest


def test_app_runs_without_errors():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    assert not at.exception
    assert at.title[0].value == "📊 Sales Dashboard"
    assert len(at.metric) == 4


def test_unselecting_all_regions_shows_warning():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    at.sidebar.multiselect[0].set_value([]).run()  # first multiselect = Region
    assert not at.exception
    assert len(at.warning) == 1
