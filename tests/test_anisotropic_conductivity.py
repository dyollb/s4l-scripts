from pathlib import Path
from tempfile import TemporaryDirectory

from s4l_scripts.anisotropic_conductivity.download_data import download_small_dwi_data
from s4l_scripts.anisotropic_conductivity.reconstruct_diffusion_tensors import (
    reconstruct_diffusion_tensors,
)


def test_download_stanford_data():
    with TemporaryDirectory() as temp_dir:
        # download test data
        files = download_small_dwi_data(download_dir=Path(temp_dir))
        for f in files["dwi"]:
            assert f.exists()

        # reconstruct
        bvec_file = next(f for f in files["dwi"] if f.name.endswith("bvec"))
        s4l_tensors_file = Path(temp_dir) / "tensor_s4l.nii.gz"
        reconstruct_diffusion_tensors(bvec_file, s4l_tensors_file)
        assert s4l_tensors_file.exists()
