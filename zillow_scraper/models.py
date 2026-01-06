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

    def to_csv_row(self) -> list:
        return [
            self.timestamp,
            self.price,
            self.beds,
            self.baths,
            self.sqft,
            self.address,
            self.link,
        ]