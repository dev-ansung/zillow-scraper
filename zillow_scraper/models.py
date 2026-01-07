from dataclasses import dataclass, field
from datetime import datetime


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
