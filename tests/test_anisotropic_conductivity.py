# Copyright (c) 2021 The Foundation for Research on Information Technologies in Society (IT'IS).
#
# This file is part of s4l-scripts
# (see https://github.com/dyollb/s4l-scripts).
#
# This software is released under the MIT License.
#  https://opensource.org/licenses/MIT

from anisotropic_conductivity.download_data import download_small_dwi_data
from anisotropic_conductivity.reconstruct_diffusion_tensors import (
    reconstruct_diffusion_tensors,
)


def test_download_stanford_data(tmp_path):
    # download test data
    files = download_small_dwi_data(download_dir=tmp_path)
    for f in files["dwi"]:
        assert f.exists()

    # reconstruct
    bvec_file = next(f for f in files["dwi"] if f.name.endswith("bvec"))
    s4l_tensors_file = tmp_path / "tensor_s4l.nii.gz"
    reconstruct_diffusion_tensors(bvec_file, s4l_tensors_file)
    assert s4l_tensors_file.exists()
