# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Utilities for extraction based on configuration dictionaries."""

from abc import ABC, abstractmethod
import io
from pathlib import Path
from hashlib import md5
from PIL import Image


def should_skip_images(configuration: dict) -> bool:
    """
    Checks if the 'image/*' mime type is in 'skip_mime_types' for a
    configuration dict.
    """
    if configuration:
        if skip_types := configuration.get("skip_mime_types"):
            return "image/*" in skip_types

    return False


class Filter(ABC):
    """A Filter postprocesses the output directory of an external tool to make
    it more suitable for OS2datascanner."""

    @abstractmethod
    def apply(self, tmpdir: str) -> str:
        """Filters the content of the specified temporary folder before
        returning it."""
        pass

    @abstractmethod
    def apply_dict(self, data_dict: dict) -> dict:
        """Filters a dictionary of in-memory objects (filename: bytes) before
        returning it."""
        pass


class DeduplicationFilter(Filter):
    """A filter for removing duplicate output files."""

    def get_hash(self, filename):
        """
        Opens and calculates hash value for a file using
        the _checksum() function.
        """
        with open(filename, "rb") as fp:
            checksum = self._checksum(fp.read())
            return checksum.hexdigest()

    def __init__(self, checksum):
        self._checksum = checksum

    def _deduplicate(self, folder):
        """
        Traverses a folder and returns a dictionary of all
        duplicate files using their hash values.
        """
        hashes = {}
        for filename in Path(folder).glob("*"):
            hash_val = self.get_hash(filename)
            hashes.setdefault(hash_val, []).append(filename)

        return hashes

    def apply(self, tmpdir):
        """
        Removes duplicate images if their hash values match.
        """
        for paths in self._deduplicate(tmpdir).values():
            for dup in paths[1:]:
                dup.unlink()

        return tmpdir

    def apply_dict(self, data_dict):
        """
        Removes duplicate objects from an in-memory dictionary if their
        hash values match.
        """
        hashes_seen = set()
        deduplicated_dict = {}
        for filename, content in data_dict.items():
            hash_val = self._checksum(content).hexdigest()
            if hash_val not in hashes_seen:
                hashes_seen.add(hash_val)
                deduplicated_dict[filename] = content

        return deduplicated_dict


MD5DeduplicationFilter = DeduplicationFilter(checksum=md5)


class ImageSizeFilter(Filter):
    """A filter for removing images that are too small to contain any text."""

    def __init__(self, x_dim, y_dim):
        self.dimensions = (x_dim, y_dim)

    def _image_too_small(self, image):
        """
        Checks whether an image is too small to contain
        any (OCR) readable text using dimensions specified
        in constructor.
        """
        return Image.open(image).size <= self.dimensions

    def apply(self, tmpdir):
        """
        Removes images that are too small to contain (OCR) readable text.
        """

        for image in Path(tmpdir).glob("*.png"):
            if self._image_too_small(image):
                image.unlink()

        return tmpdir

    def apply_dict(self, data_dict):
        """
        Removes images from an in-memory dictionary that are too small.
        """
        filtered_dict = {}
        for filename, content in data_dict.items():
            # Only attempt to filter files with common image extensions
            if Path(filename).suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                try:
                    img = Image.open(io.BytesIO(content))
                    if not self._image_too_small(img):
                        filtered_dict[filename] = content
                except Exception:
                    # If it's not a valid image, keep it?
                    filtered_dict[filename] = content
            else:
                # Keep non-image files
                filtered_dict[filename] = content
        return filtered_dict


TinyImageFilter = ImageSizeFilter(8, 8)
