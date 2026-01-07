from zillow_scraper.parsers import ZillowPropertyDetailParser


def test_property_detail_parser_extracts_basic_info(property_detail_html_fixture):
    """Test that the property detail parser extracts basic information."""
    parser = ZillowPropertyDetailParser()
    result = parser.parse_detail(property_detail_html_fixture)

    assert result is not None
    assert result.price == "$1,500,000"
    assert "123 Main St" in result.address
    assert result.beds == "3"
    assert result.baths == "2"
    # Note: sqft parser removes commas
    assert result.sqft == "1800"


def test_property_detail_parser_extracts_additional_info(property_detail_html_fixture):
    """Test that the property detail parser extracts additional property information."""
    parser = ZillowPropertyDetailParser()
    result = parser.parse_detail(property_detail_html_fixture)

    assert result is not None
    assert result.property_type == "Single Family"
    assert result.year_built == "1985"
    assert result.lot_size == "5,000 sqft"
    assert result.hoa == "$200/month"


def test_property_detail_parser_extracts_link(property_detail_html_fixture):
    """Test that the property detail parser extracts the canonical URL."""
    parser = ZillowPropertyDetailParser()
    result = parser.parse_detail(property_detail_html_fixture)

    assert result is not None
    assert "zillow.com" in result.link
    assert "12345_zpid" in result.link


def test_property_detail_parser_handles_missing_fields():
    """Test that the property detail parser handles missing fields gracefully."""
    malformed_html = """
    <html>
        <body>
            <h1>Some Address</h1>
        </body>
    </html>
    """
    parser = ZillowPropertyDetailParser()
    result = parser.parse_detail(malformed_html)

    # Should still return a result with N/A values
    assert result is not None
    assert result.price == "N/A"
    assert result.property_type == "N/A"


def test_property_detail_parser_handles_empty_html():
    """Test that the property detail parser handles empty HTML."""
    parser = ZillowPropertyDetailParser()
    result = parser.parse_detail("")

    # Should return None or handle gracefully
    assert result is None or (result.price == "N/A" and result.address == "N/A")
