from pathlib import Path
from typing import Dict, List
import shutil

from dipy.data import (
    fetch_stanford_hardi,
    fetch_stanford_labels,
    fetch_stanford_t1,
    get_fnames,
)


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
    output_dir = Path("/Users/lloyd/Models/StandfordData")
    files = download_stanford_data(download_dir=output_dir)

    for f in output_dir.glob("*.*"):
        print(f)
