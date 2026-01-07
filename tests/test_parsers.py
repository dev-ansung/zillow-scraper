from zillow_scraper.parsers import ZillowExactParser


def test_parser_extracts_correct_count(raw_html_fixture):
    parser = ZillowExactParser()
    results = parser.parse(raw_html_fixture)
    assert len(results) == 2


def test_parser_extracts_data_correctly(raw_html_fixture):
    parser = ZillowExactParser()
    results = parser.parse(raw_html_fixture)
    first_house = results[0]

    assert first_house.price == "$1,188,000"
    assert first_house.address == "748 Cottage Ct, Mountain View, CA 94043"
    assert first_house.beds == "2"
    assert first_house.sqft == "1,150"


def test_parser_handles_missing_fields():
    malformed_html = """
    <article data-test="property-card">
    </article>
    """
    parser = ZillowExactParser()
    results = parser.parse(malformed_html)

    assert len(results) == 1
    assert results[0].price == "N/A"
    assert results[0].address == "N/A"
