import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import requests

from api.api import chapter_post_process, create_chapter_obj
from reader.models import Chapter, Group, Series, Volume

from ..scraper import BaseScraper


class MangaDex(BaseScraper):
    def __init__(self, series):
        self.series = series
        self.groups = {}
        try:
            scraping_info = json.loads(self.series.scraping_identifiers)
            self.md_series_id = scraping_info["series_id"]
            self.group_whitelist = scraping_info.get("group_whitelist", None)
            self.group_blacklist = scraping_info.get("group_blacklist", None)
            self.chapter_id_blacklist = scraping_info.get("chapter_id_blacklist", None)
            self.released_within_days = scraping_info.get("released_within_days", 30)
            self.initialized = True
        except Exception:
            self.initialized = False

    def get_source_chapters_list(self, series_id: int):
        md_series_api = (
            f"https://api.mangadex.org/v2/manga/{series_id}?include=chapters"
        )
        chapter_dict = {}
        resp = requests.get(md_series_api)
        if resp.status_code == 200:
            api_data = resp.json()["data"]
            groups = {group["id"]: group["name"] for group in api_data["groups"]}
            for chapter_metadata in api_data["chapters"]:
                md_chapter_id = chapter_metadata["id"]
                if chapter_metadata["language"] == "gb":
                    chapter_number = float(chapter_metadata["chapter"])
                    chapter_metadata["group_name"] = groups[
                        chapter_metadata["groups"][0]
                    ]
                    if chapter_number not in chapter_dict:
                        chapter_dict[chapter_number] = [
                            (md_chapter_id, chapter_metadata)
                        ]
                    else:
                        chapter_dict[chapter_number].append(
                            (md_chapter_id, chapter_metadata)
                        )
        return chapter_dict

    def get_source_chapter_data(self, md_chapter_id: int):
        resp = requests.get(f"https://api.mangadex.org/v2/chapter/{md_chapter_id}")
        if resp.status_code == 200:
            api_data = resp.json()["data"]
            domain = (
                api_data["server"]
                if not api_data["server"].startswith("/")
                else "https://mangadex.org" + api_data["server"]
            )
            return {
                "hash": api_data["hash"],
                "pages": [
                    f"{domain}{api_data['hash']}/{page}" for page in api_data["pages"]
                ],
            }
        return None

    def generate_source_chapter_hash(self, source_chapter_data) -> str:
        return hashlib.md5(f"{source_chapter_data['hash']}".encode()).hexdigest()

    def is_valid_source_chapter(
        self, series: Series, md_chapter_id, md_chapter_metadata, md_group
    ):
        if str(md_chapter_id) in self.chapter_id_blacklist:
            return False
        if (self.group_whitelist and md_group not in self.group_whitelist) or (
            self.group_blacklist and md_group in self.group_blacklist
        ):
            return False
        return True

    def is_valid_group(self, md_group):
        group = self.groups.get(md_group, False)
        if not group:
            group = Group.objects.filter(name=md_group).first()
            if group:
                self.groups[group.name] = group
                return group
            else:
                return False
        return group

    def is_source_chapter_updated(
        self, downloaded_chapters, chapter_number, md_chapter_id, md_group
    ):
        ch_obj = downloaded_chapters[chapter_number][md_group]
        if (
            datetime.utcnow().replace(tzinfo=timezone.utc) - ch_obj.uploaded_on
        ) > timedelta(days=self.released_within_days):
            return False, None
        md_chapter_data = self.get_source_chapter_data(md_chapter_id)
        if not md_chapter_data:
            return False, None
        source_chapter_hash = self.generate_source_chapter_hash(md_chapter_data)
        # check if the source chapter has updated.
        if ch_obj.scraper_hash == source_chapter_hash:
            return False, None
        return True, md_chapter_data

    def get_valid_source_chapters(
        self,
        series: Series,
        md_chapters,
        *,
        specific_chapters: Dict[float, List[str]] = [],
    ):
        for chapter_number, md_chapters_by_group in md_chapters.items():
            for md_chapter_id, md_chapter_metadata in md_chapters_by_group:
                md_group = md_chapter_metadata["group_name"]
                if specific_chapters and (
                    chapter_number not in specific_chapters
                    or md_group not in specific_chapters[chapter_number]
                ):
                    continue
                group = self.is_valid_group(md_group)
                if (
                    group
                    and specific_chapters
                    or (
                        self.is_valid_source_chapter(
                            series, md_chapter_id, md_chapter_metadata, md_group
                        )
                    )
                ):
                    yield (
                        md_chapter_id,
                        md_chapter_metadata["title"],
                        chapter_number,
                        series,
                        group,
                    )

    def pre_source_check_setup(self, series):
        downloaded_chapters = {}
        for chapter in Chapter.objects.filter(series=series):
            if chapter.chapter_number not in downloaded_chapters:
                downloaded_chapters[chapter.chapter_number] = {
                    chapter.group.name: chapter
                }
            else:
                downloaded_chapters[chapter.chapter_number][
                    chapter.group.name
                ] = chapter

        md_chapters = self.get_source_chapters_list(self.md_series_id)
        return downloaded_chapters, md_chapters

    def download_source_chapter(
        self,
        title: str,
        chapter_number: float,
        series: Series,
        group: Group,
        latest_volume: int,
        md_chapter_id: int,
        md_chapter_data: Optional[Dict[str, Any]] = None,
    ):
        if not md_chapter_data:
            md_chapter_data = self.get_source_chapter_data(md_chapter_id)
            if not md_chapter_data:
                return None
            md_chapter_pages = md_chapter_data["pages"]
        else:
            md_chapter_pages = md_chapter_data["pages"]
        if not md_chapter_pages:
            print(
                f"Failed to get chapter pages of md chapter {chapter_number} with id: {md_chapter_id} on MangaDex for {series.slug}.",
                group.name,
            )
            return
        ch_obj, chapter_folder, group_folder, is_update = create_chapter_obj(
            chapter_number, group, series, latest_volume, title
        )
        ch_obj.scraper_hash = self.generate_source_chapter_hash(md_chapter_data)
        ch_obj.save()
        padding = len(str(len(md_chapter_pages)))
        print(
            f"Downloading chapter: {chapter_number} group: {series.name} series: {series.name} from Mangadex..."
        )
        print(f"Found {len(md_chapter_pages)} pages...")
        for idx, page in enumerate(md_chapter_pages):
            extension = page.rsplit(".", 1)[1]
            page_file = f"{str(idx+1).zfill(padding)}.{extension}"
            resp = requests.get(page)
            if resp.status_code == 200:
                page_content = resp.content
                with open(
                    os.path.join(chapter_folder, group_folder, page_file), "wb",
                ) as f:
                    f.write(page_content)
            else:
                print("failed at mangadex_download", idx, page)
        chapter_post_process(ch_obj, is_update=is_update)
        return ch_obj

    def scrape_chapters(
        self,
        check_updates: bool = True,
        specific_chapters: Dict[float, List[str]] = [],
    ):
        scraped_chapters = []
        latest_volume = (
            Volume.objects.filter(series=self.series)
            .order_by("-volume_number")[0]
            .volume_number
        )
        downloaded_chapters, md_chapters = self.pre_source_check_setup(self.series)
        for (
            md_chapter_id,
            title,
            chapter_number,
            series,
            group,
        ) in self.get_valid_source_chapters(
            self.series, md_chapters, specific_chapters=specific_chapters,
        ):
            # if checking updates and not getting missing chapters only, skip exisitng chapters from groups if there isn't a newer version of it on the source
            md_chapter_data = None
            if not specific_chapters and (
                chapter_number in downloaded_chapters
                and group.name in downloaded_chapters[chapter_number]
            ):
                if not check_updates:
                    continue
                is_updated, md_chapter_data = self.is_source_chapter_updated(
                    downloaded_chapters, chapter_number, md_chapter_id, group.name,
                )
                if not is_updated:
                    continue
            ch_obj = self.download_source_chapter(
                title,
                chapter_number,
                series,
                group,
                latest_volume,
                md_chapter_id,
                md_chapter_data,
            )
            if ch_obj:
                scraped_chapters.append(ch_obj)
        return scraped_chapters
