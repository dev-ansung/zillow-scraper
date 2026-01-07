import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class AddressInfo:
    """Structured address information."""

    street: str = "N/A"
    city: str = "N/A"
    state: str = "N/A"
    zip_code: str = "N/A"


@dataclass
class PriceDetails:
    """Detailed price and financial information."""

    list_price: Optional[int] = None
    price_per_sqft: Optional[int] = None
    est_monthly_payment: Optional[int] = None
    zestimate: Optional[int] = None
    tax_assessed_value: Optional[int] = None
    annual_tax_amount: Optional[int] = None


@dataclass
class PropertyBasics:
    """Basic property characteristics."""

    home_type: str = "N/A"
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    full_bathrooms: Optional[int] = None
    square_footage: Optional[int] = None
    year_built: Optional[int] = None
    stories: Optional[int] = None
    zoning: str = "N/A"
    parcel_number: str = "N/A"


@dataclass
class ParkingInfo:
    """Parking details."""

    total_spaces: Optional[int] = None
    garage_spaces: Optional[int] = None
    features: List[str] = field(default_factory=list)


@dataclass
class InteriorFeatures:
    """Interior features and amenities."""

    flooring: List[str] = field(default_factory=list)
    kitchen: List[str] = field(default_factory=list)
    bathroom_features: List[str] = field(default_factory=list)
    laundry: str = "N/A"
    cooling: str = "N/A"
    heating: str = "N/A"
    additional_rooms: List[str] = field(default_factory=list)
    highlights: List[str] = field(default_factory=list)


@dataclass
class CommunityAmenities:
    """Community and HOA amenities."""

    hoa_fee_monthly: Optional[int] = None
    parking: ParkingInfo = field(default_factory=ParkingInfo)
    pool: str = "N/A"
    accessibility: List[str] = field(default_factory=list)
    storage: str = "N/A"


@dataclass
class LocationScores:
    """Walk, transit, and bike scores."""

    walk_score: Optional[int] = None
    transit_score: Optional[int] = None
    bike_score: Optional[int] = None


@dataclass
class SchoolInfo:
    """Information about a nearby school."""

    name: str = "N/A"
    rating: str = "N/A"
    grades: str = "N/A"


@dataclass
class ListingInfo:
    """Listing status and agent information."""

    status: str = "N/A"
    days_on_zillow: Optional[int] = None
    mls_number: str = "N/A"
    listing_agent: str = "N/A"
    last_updated: str = "N/A"


@dataclass
class PropertyDetail:
    """Complete detailed property information."""

    address: AddressInfo = field(default_factory=AddressInfo)
    price_details: PriceDetails = field(default_factory=PriceDetails)
    property_basics: PropertyBasics = field(default_factory=PropertyBasics)
    interior_features: InteriorFeatures = field(default_factory=InteriorFeatures)
    community_amenities: CommunityAmenities = field(default_factory=CommunityAmenities)
    location_scores: LocationScores = field(default_factory=LocationScores)
    nearby_schools: List[SchoolInfo] = field(default_factory=list)
    listing_info: ListingInfo = field(default_factory=ListingInfo)
    url: str = "N/A"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


# Legacy model for backward compatibility with listing scraping
@dataclass
class PropertyData:
    address: str
    price: str
    link: str
    beds: str
    baths: str
    sqft: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    # Additional fields for detailed property information
    property_type: str = "N/A"
    year_built: str = "N/A"
    lot_size: str = "N/A"
    hoa: str = "N/A"

    def to_csv_row(self) -> list:
        return [
            self.timestamp,
            self.price,
            self.beds,
            self.baths,
            self.sqft,
            self.address,
            self.link,
            self.property_type,
            self.year_built,
            self.lot_size,
            self.hoa,
        ]
