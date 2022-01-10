# Copyright (c) 2021 The Foundation for Research on Information Technologies in Society (IT'IS).
#
# This file is part of s4l-scripts
# (see https://github.com/dyollb/s4l-scripts).
#
# This software is released under the MIT License.
#  https://opensource.org/licenses/MIT

import sys
from pathlib import Path
import argparse

from s4l_scripts.anisotropic_conductivity.download_data import download_stanford_data
from s4l_scripts.anisotropic_conductivity.load_labels import (
    load_stanford_label_info,
    save_iseg_label_info,
)
from s4l_scripts.anisotropic_conductivity.reconstruct_diffusion_tensors import (
    reconstruct_diffusion_tensors,
)


def import_in_sim4life(
    t1_file: Path, seg_file: Path, tissuelist_file: Path, s4l_tensors_file: Path
):
    try:
        import s4l_v1 as s4l
        import ImageModeling  # TODO: make sure this works with s4l
        import MeshModeling  # TODO: make sure this works with s4l
    except ImportError as error:
        print("ERROR: Could not import Sim4Life Python modules", sys.exc_info()[0])
        return

    # not used, but nice to visualize model with MRI
    # t1_image = ImageModeling.ImportImage(f"{t1_file}")

    # import label field
    labelfield = ImageModeling.ImportImage(f"{seg_file}", True, f"{tissuelist_file}")

    # extract surface-based model
    surfaces = MeshModeling.ExtractSurface(labelfield, min_edge_length=0.5)

    stl_dir = seg_file.parent / "stl"
    stl_dir.mkdir(exist_ok=True)
    for e in surfaces:
        s4l.model.Export([e], f"{stl_dir / e.Name}.stl")

    # load dwi data, compute conductivity

    # s4l.analysis.import(s4l_tensors_file) ?


def main(data_dir: Path):
    files = download_stanford_data(download_dir=data_dir)

    # reconstruct DTI using the dipy package
    bvec_file = next(f for f in files["dwi"] if f.name.endswith("bvec"))
    s4l_tensors_file = bvec_file.parent / bvec_file.name.replace(".bvec", "_s4l.nii.gz")
    reconstruct_diffusion_tensors(bvec_file, s4l_tensors_file)

    # convert label infos so we get tissue names in Sim4Life
    label_info_file = next(f for f in files["labels"] if f.name.endswith("txt"))
    iseg_tissue_list_file = label_info_file.parent / label_info_file.name.replace(
        ".txt", "_iseg.txt"
    )
    label_infos = load_stanford_label_info(label_info_file)
    save_iseg_label_info(label_infos, iseg_tissue_list_file)

    # load image and segmentation data in Sim4Life
    labels_file = next(f for f in files["labels"] if f.name.endswith("nii.gz"))
    t1_file = files["t1"][0]

    assert labels_file.exists()
    assert t1_file.exists()

    import_in_sim4life(t1_file, labels_file, iseg_tissue_list_file, s4l_tensors_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run subject-specific simulation.")
    parser.add_argument(
        "--data_dir",
        dest="data_dir",
        type=Path,
        help="Directory to download image data and store simulation",
    )
    args = parser.parse_args()

    main(data_dir=args.data_dir)
