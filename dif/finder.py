from collections import defaultdict
import mimetypes
import os
import pathlib
from typing import Callable, Dict, List, Optional, Union

import imagehash
from PIL import Image
import numpy as np
import numpy.typing as npt

Path = Union[str, pathlib.Path]
FileHashes = Dict[Path, Optional[npt.NDArray[np.bool_]]]
FileDuplicates = Dict[Path, List[Path]]


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


def get_hashes(
    image_paths: List[Path],
    increment_func: Callable = None,
) -> FileHashes:
    hashes: FileHashes = {}
    for file_path in image_paths:
        try:
            with Image.open(file_path) as im:
                hashes[file_path] = imagehash.phash(im, hash_size=128).hash.flatten()
        except:
            hashes[file_path] = None

        if increment_func:
            increment_func()

    return hashes


def find_duplicates(
    image_paths: List[Path],
    hashes: FileHashes,
    increment_func: Callable = None,
) -> FileDuplicates:
    """Find duplicates from list of images."""
    dups: FileDuplicates = defaultdict(list)

    img_len = len(image_paths)
    for i in range(img_len):
        base = image_paths[i]
        base_hash = hashes[base]
        if base_hash is None:
            if increment_func:
                increment_func()
            continue

        for j in range(i + 1, img_len):
            target = image_paths[j]
            target_hash = hashes[target]
            if target_hash is None:
                continue

            if np.count_nonzero(base_hash != target_hash) / (8**2) < 0.2:
                dups[base].append(target)

        if increment_func:
            increment_func()

    final_hashes = {k: v for k, v in dups.items() if len(v) > 1}
    return final_hashes
