from pathlib import Path

import pytest


@pytest.fixture
def raw_html_fixture():
    """
    Returns a snippet of valid Zillow HTML loaded from a file.
    """
    base_dir = Path(__file__).parent
    fixture_path = base_dir / "fixtures" / "zillow_sample.html"

    with open(fixture_path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def property_detail_html_fixture():
    """
    Returns a snippet of a Zillow property detail page HTML loaded from a file.
    """
    base_dir = Path(__file__).parent
    fixture_path = base_dir / "fixtures" / "property_detail_sample.html"

    with open(fixture_path, "r", encoding="utf-8") as f:
        return f.read()