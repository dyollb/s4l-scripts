"""
Most of this code is from torchvision (BSD 3-Clause License):
see https://github.com/pytorch/vision/blob/main/torchvision/datasets/utils.py
"""

import os
import gzip
import shutil
import urllib
from urllib import request, error
import zipfile
import hashlib
import tarfile
from typing import Optional, Union

TypePath = Union[str, os.PathLike]


def calculate_md5(fpath, chunk_size=1024 * 1024):
    md5 = hashlib.md5()
    with open(fpath, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            md5.update(chunk)
    return md5.hexdigest()


def check_md5(fpath, md5, **kwargs):
    return md5 == calculate_md5(fpath, **kwargs)


def check_integrity(fpath, md5=None):
    if not os.path.isfile(fpath):
        return False
    if md5 is None:
        return True
    return check_md5(fpath, md5)


def gen_bar_updater():
    class bar:
        last_kb: int = 0

        def update(self, count, block_size, total_size):
            progress_mb = count * block_size // 1048576
            if progress_mb > self.last_kb:
                self.last_kb = progress_mb
                print(f"{progress_mb} / {total_size // 1048576} MB", end="\r")

    b = bar()
    return b.update


# Adapted from torchvision, removing print statements
def download_and_extract_archive(
    url: str,
    download_root: TypePath,
    extract_root: Optional[TypePath] = None,
    filename: Optional[TypePath] = None,
    md5: str = None,
    remove_finished: bool = False,
) -> None:
    download_root = os.path.expanduser(download_root)
    if extract_root is None:
        extract_root = download_root
    if not filename:
        filename = os.path.basename(url)
    download_url(url, download_root, filename, md5)
    archive = os.path.join(download_root, filename)
    extract_archive(archive, extract_root, remove_finished)


def _is_tarxz(filename):
    return filename.endswith(".tar.xz")


def _is_tar(filename):
    return filename.endswith(".tar")


def _is_targz(filename):
    return filename.endswith(".tar.gz")


def _is_tgz(filename):
    return filename.endswith(".tgz")


def _is_gzip(filename):
    return filename.endswith(".gz") and not filename.endswith(".tar.gz")


def _is_zip(filename):
    return filename.endswith(".zip")


def _is_txt(filename):
    return filename.endswith(".txt")


def extract_archive(from_path, to_path=None, remove_finished=False):
    if to_path is None:
        to_path = os.path.dirname(from_path)

    if _is_tar(from_path):
        with tarfile.open(from_path, "r") as tar:
            tar.extractall(path=to_path)
    elif _is_targz(from_path) or _is_tgz(from_path):
        with tarfile.open(from_path, "r:gz") as tar:
            tar.extractall(path=to_path)
    elif _is_tarxz(from_path):
        with tarfile.open(from_path, "r:xz") as tar:
            tar.extractall(path=to_path)
    elif _is_gzip(from_path):
        stem = os.path.splitext(os.path.basename(from_path))[0]
        to_path = os.path.join(to_path, stem)
        with open(to_path, "wb") as out_f, gzip.GzipFile(from_path) as zip_f:
            out_f.write(zip_f.read())
    elif _is_zip(from_path):
        with zipfile.ZipFile(from_path, "r") as z:
            z.extractall(to_path)
    elif _is_txt(from_path):
        shutil.copyfile(
            from_path, os.path.join(to_path, os.path.split(to_path)[-1] + ".txt")
        )
    else:
        raise ValueError(f"Extraction of {from_path} not supported")

    if remove_finished:
        os.remove(from_path)


# Adapted from torchvision, removing print statements
def download_url(
    url: str,
    root: TypePath,
    filename: Optional[TypePath] = None,
    md5: str = None,
) -> None:
    """Download a file from a url and place it in root.

    Args:
        url: URL to download file from
        root: Directory to place downloaded file in
        filename: Name to save the file under.
            If ``None``, use the basename of the URL
        md5: MD5 checksum of the download. If None, do not check
    """

    root = os.path.expanduser(root)
    if not filename:
        filename = os.path.basename(url)
    fpath = os.path.join(root, filename)
    os.makedirs(root, exist_ok=True)
    # check if file is already present locally
    if not check_integrity(fpath, md5):
        try:
            # print("Downloading " + url + " to " + fpath)  # noqa: T001
            request.urlretrieve(url, fpath, reporthook=gen_bar_updater())
        except (error.URLError, OSError) as e:
            if url[:5] == "https":
                url = url.replace("https:", "http:")
                message = (
                    "Failed download. Trying https -> http instead."
                    " Downloading " + url + " to " + fpath
                )
                print(message)  # noqa: T001
                request.urlretrieve(url, fpath, reporthook=gen_bar_updater())
            else:
                raise e
        # check integrity of downloaded file
        if not check_integrity(fpath, md5):
            raise RuntimeError("File not found or corrupted.")


if __name__ == "__main__":
    pass
