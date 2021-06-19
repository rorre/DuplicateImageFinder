import mimetypes
import os
import pathlib
from typing import Callable, Dict, List, Union

import imagehash
from PIL import Image

Path = Union[str, pathlib.Path]
FileHashes = Dict[str, List[Path]]


def get_all_images(folder: Path) -> List[Path]:
    """Get all image files from a folder."""
    image_paths: List[Path] = []

    for root, _, files in os.walk(folder):
        full_root = os.path.join(folder, root)

        for filename in files:
            file_path = os.path.join(full_root, filename)
            mime = mimetypes.guess_type(file_path)[0]
            if not mime or not (mime and mime.startswith("image")):
                continue

            image_paths.append(file_path)
    return image_paths


def find_duplicates(
    image_paths: List[Path],
    increment_func: Callable = None,
) -> FileHashes:
    """Find duplicates from list of images."""
    hashes: FileHashes = {}

    for file_path in image_paths:
        try:
            with Image.open(file_path) as im:
                hash_value = str(imagehash.phash(im))
                if hash_value in hashes:
                    hashes[hash_value].append(file_path)
                else:
                    hashes[hash_value] = [file_path]
        except:
            continue

        if increment_func:
            increment_func()

    final_hashes = {k: v for k, v in hashes.items() if len(v) > 1}
    return final_hashes
