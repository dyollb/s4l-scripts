# Copyright (c) 2021 The Foundation for Research on Information Technologies in Society (IT'IS).
#
# This file is part of s4l-scripts
# (see https://github.com/dyollb/s4l-scripts).
#
# This software is released under the MIT License.
#  https://opensource.org/licenses/MIT

from pathlib import Path
from typing import Dict, List
import shutil
from tempfile import NamedTemporaryFile

from dipy.data import (
    fetch_stanford_hardi,
    fetch_stanford_labels,
    fetch_stanford_t1,
    get_fnames,
)

from ._download import download_and_extract_archive


def download_ixi_data(download_dir: Path) -> Dict[str, List[Path]]:
    base_url = "http://biomedic.doc.ic.ac.uk/brain-development/downloads/IXI/{filename}"
    md5_dict = {
        "IXI-T1.tar": "34901a0593b41dd19c1a1f746eac2d58",
        "IXI-T2.tar": "e3140d78730ecdd32ba92da48c0a9aaa",
        "IXI-PD.tar": "88ecd9d1fa33cb4a2278183b42ffd749",
        "IXI-MRA.tar": "29be7d2fee3998f978a55a9bdaf3407e",
        "IXI-DTI.tar": "636573825b1c8b9e8c78f1877df3ee66",
        "bvals.txt": "e34276bad42272657225ef038ea08c13",
        "bvecs.txt": "7cb2982dedd13da52dd0ff381d257c74",
    }
    filename_dict = {
        "bvals": "bvals.txt",
        "bvecs": "bvecs.txt",
        "dwi": "IXI-DTI.tar",
        "t2": "IXI-T2.tar",
    }

    all_files: Dict[str, List[Path]] = {}
    for modality in ("bvals", "bvecs", "t2"):
        filename = filename_dict[modality]
        url = base_url.format(filename=filename)
        md5 = md5_dict[filename]

        modality_dir = download_dir / modality
        if modality_dir.is_dir() and list(modality_dir.glob("*")):
            continue
        modality_dir.mkdir(exist_ok=True, parents=True)

        with NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as f:
            download_and_extract_archive(
                url,
                download_root=modality_dir,
                filename=f.name,
                md5=md5,
            )
        all_files[modality] = list(modality_dir.glob("*"))
    return all_files


def download_small_dwi_data(download_dir: Path) -> Dict[str, List[Path]]:
    """Download small test dwi data, no t1 or labels are provided

    Args:
        download_dir: specify folder where data is copied
    """
    download_dir.mkdir(exist_ok=True)
    files = []
    for f in get_fnames(name="small_25"):
        files.append(Path(download_dir) / Path(f).name)
        shutil.copyfile(Path(f), files[-1])
    return {"dwi": files}


def download_stanford_data(download_dir: Path) -> Dict[str, List[Path]]:
    """Download standford dwi data, t1 image and labelfield

    Args:
        download_dir: specify folder where data is copied
    """

    def _fetch_and_copy(fetch_fun):
        files, dipy_dir = fetch_fun()
        for f in files.keys():
            shutil.copyfile(Path(dipy_dir) / f, Path(download_dir) / f)
        return [download_dir / f for f in files.keys()]

    download_dir.mkdir(exist_ok=True)
    dwi_files = _fetch_and_copy(fetch_stanford_hardi)
    t1_files = _fetch_and_copy(fetch_stanford_t1)
    label_files = _fetch_and_copy(fetch_stanford_labels)
    return {"dwi": dwi_files, "t1": t1_files, "labels": label_files}


if __name__ == "__main__":
    output_dir = Path("/Users/lloyd/Models/IXI")
    files = download_ixi_data(download_dir=output_dir)

    for f in output_dir.glob("*.*"):
        print(f)
