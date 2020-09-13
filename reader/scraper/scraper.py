from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List

from ..models import Chapter


class BaseScraper(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        self.initialized = True

    @abstractmethod
    def get_source_chapter_data(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    @abstractmethod
    def generate_source_chapter_hash(
        self, source_chapter_data: Any, *args, **kwargs
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_valid_source_chapters(self, *args, **kwargs) -> Generator[Any, None, None]:
        raise NotImplementedError

    @abstractmethod
    def download_source_chapter(self, *args, **kwargs) -> Chapter:
        raise NotImplementedError

    @abstractmethod
    def scrape_chapters(
        self,
        *,
        check_updates: bool = True,
        specific_chapters: Dict[
            float, List[str]
        ] = [],  # dict of {chapter_number: list of group names}
        **kwargs
    ) -> List[Chapter]:
        raise NotImplementedError
