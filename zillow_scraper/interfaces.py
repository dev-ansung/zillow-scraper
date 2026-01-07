from abc import ABC, abstractmethod
from typing import List

from .models import PropertyData


class IPageSourceProvider(ABC):
    @abstractmethod
    def fetch_source(self, url: str) -> str:
        """Navigates to URL and returns raw HTML source."""
        pass

    @abstractmethod
    def close(self):
        """Clean up resources."""
        pass


class IParser(ABC):
    @abstractmethod
    def parse(self, html_content: str) -> List[PropertyData]:
        """Extracts property data from raw HTML."""
        pass
