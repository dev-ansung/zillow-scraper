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
    
    # Check column order: [Timestamp, Price, Beds, Baths, Sqft, Address, Link, Property_Type, Year_Built, Lot_Size, HOA]
    assert row[1] == "$100" 
    assert row[5] == "123 Main St"
    assert len(row) == 11  # Updated to include new fields


def test_property_data_with_additional_fields():
    """Test PropertyData with additional detail fields."""
    prop = PropertyData(
        address="456 Oak Ave",
        price="$750k",
        link="http://test2.com",
        beds="3",
        baths="2",
        sqft="1500",
        property_type="Single Family",
        year_built="1990",
        lot_size="5000 sqft",
        hoa="$100/month"
    )
    
    assert prop.property_type == "Single Family"
    assert prop.year_built == "1990"
    assert prop.lot_size == "5000 sqft"
    assert prop.hoa == "$100/month"
    
    row = prop.to_csv_row()
    assert row[7] == "Single Family"
    assert row[8] == "1990"
    assert row[9] == "5000 sqft"
    assert row[10] == "$100/month"