# Copyright (c) 2021 The Foundation for Research on Information Technologies in Society (IT'IS).
#
# This file is part of s4l-scripts
# (see https://github.com/dyollb/s4l-scripts).
#
# This software is released under the MIT License.
#  https://opensource.org/licenses/MIT

from pathlib import Path
from os import fspath
import nibabel as nib
from dipy.core.gradients import gradient_table
from dipy.io import read_bvals_bvecs
from dipy.segment.mask import median_otsu
from dipy.reconst.dti import TensorModel


def reconstruct_diffusion_tensors(bvec_file: Path, s4l_dti_file: Path) -> None:
    """Reconstruct DTI from bvec/bval files

    Args:
        bvec_file: location of bvec file
        s4l_dti_file: location of (output) tensor image in format supported by Sim4Life
    """
    # assumes image and bval file have same file path, except for extension
    img_file = bvec_file.with_suffix(".nii.gz")
    bval_file = bvec_file.with_suffix(".bval")

    bvals, bvecs = read_bvals_bvecs(fspath(bval_file), fspath(bvec_file))
    img = nib.load(img_file)

    data = img.get_data()
    maskdata, _ = median_otsu(
        data,
        vol_idx=range(1, 15),
        median_radius=3,  # range(10, 50)
        numpass=1,
        autocrop=False,
        dilate=2,
    )

    gtab = gradient_table(bvals, bvecs)
    tenmodel = TensorModel(gtab)
    tenfit = tenmodel.fit(maskdata)

    # lower_triangular returns DTI tensor components in order:
    #   Dxx, Dxy, Dyy, Dxz, Dyz, Dzz
    D = tenfit.lower_triangular()

    # Sim4Life expects this order: XX, YY, ZZ, XY, YZ, ZX
    ids = [0, 2, 5, 1, 4, 3]
    D_s4l = D[..., ids]
    image2 = nib.Nifti1Image(D_s4l, img.affine)
    nib.save(image2, s4l_dti_file)
