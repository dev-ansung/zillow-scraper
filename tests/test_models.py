from datetime import datetime

from zillow_scraper.models import PropertyData


def test_property_data_timestamp():
    prop = PropertyData(
        address="123 Main St",
        price="$500k",
        link="http://test.com",
        beds="2",
        baths="1",
        sqft="1000"
    )
    
    assert prop.timestamp is not None
    # Verify it looks like an ISO date
    dt = datetime.fromisoformat(prop.timestamp)
    assert isinstance(dt, datetime)

def test_csv_row_format():
    prop = PropertyData(
        address="123 Main St",
        price="$100",
        link="http://link",
        beds="1",
        baths="1",
        sqft="100"
    )
    
    row = prop.to_csv_row()
    
    # Check column order: [Timestamp, Price, Beds, Baths, Sqft, Address, Link]
    assert row[1] == "$100" 
    assert row[5] == "123 Main St"