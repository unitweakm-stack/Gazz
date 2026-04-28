from __future__ import annotations

import asyncio
import logging
import os
import re
import tempfile
from pathlib import Path

from mutagen.id3 import APIC, ID3, ID3NoHeaderError, TIT2, TPE1
from mutagen.mp4 import MP4, MP4Cover

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Retags supported audio files and embeds cover art when possible."""

    async def process(
        self,
        source_bytes: bytes,
        source_name: str | None,
        new_title: str,
        performer: str,
        cover_bytes: bytes,
    ) -> tuple[str, bytes]:
        return await asyncio.to_thread(
            self._process_sync,
            source_bytes,
            source_name,
            new_title,
            performer,
            cover_bytes,
        )

    def _process_sync(
        self,
        source_bytes: bytes,
        source_name: str | None,
        new_title: str,
        performer: str,
        cover_bytes: bytes,
    ) -> tuple[str, bytes]:
        suffix = Path(source_name or "track.mp3").suffix.lower() or ".mp3"
        safe_stem = self._slugify(new_title) or "track"
        target_name = f"{safe_stem}{suffix}"

        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)

        try:
            with open(temp_path, "wb") as file:
                file.write(source_bytes)

            if suffix == ".mp3":
                self._tag_mp3(temp_path, new_title, performer, cover_bytes)
            elif suffix in {".m4a", ".mp4"}:
                self._tag_m4a(temp_path, new_title, performer, cover_bytes)
            else:
                logger.warning("Unsupported retag format %s. Returning original bytes.", suffix)
                return target_name, source_bytes

            with open(temp_path, "rb") as file:
                return target_name, file.read()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    @staticmethod
    def _tag_mp3(path: str, title: str, performer: str, cover_bytes: bytes) -> None:
        try:
            tags = ID3(path)
        except ID3NoHeaderError:
            tags = ID3()

        tags.delall("TIT2")
        tags.delall("TPE1")
        tags.delall("APIC")
        tags.add(TIT2(encoding=3, text=title))
        tags.add(TPE1(encoding=3, text=performer))
        tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=cover_bytes))
        tags.save(path, v2_version=3)

    @staticmethod
    def _tag_m4a(path: str, title: str, performer: str, cover_bytes: bytes) -> None:
        audio = MP4(path)
        audio["\xa9nam"] = [title]
        audio["\xa9ART"] = [performer]
        audio["aART"] = [performer]
        audio["covr"] = [MP4Cover(cover_bytes, imageformat=MP4Cover.FORMAT_JPEG)]
        audio.save()

    @staticmethod
    def _slugify(value: str) -> str:
        value = re.sub(r"[^\w\-\s]+", "", value, flags=re.UNICODE).strip()
        value = re.sub(r"[\s\-]+", "_", value)
        return value[:80]
