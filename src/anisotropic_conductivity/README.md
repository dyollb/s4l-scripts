# Subject-specific anatomical model with anisotropic conductivity from diffusion weighted imaging
This folder contains scripts to create a subject-specific head model with inhomogeneous anisotropic conductivity distribution in Sim4Life, e.g. for transcranial electric/magnetic stimulation simulations. The workflow demonstrates how to reconstruct diffusion weighted images to diffusion tensor fields compatible with Sim4Life.

The file [main.py](main.py) implements the top-level workflow. The example downloads a demo dataset from the [Stanford digital repository](https://purl.stanford.edu/ng782rw8378) using the open-source package [dipy](https://dipy.org/). The key steps include:

- download the data
- reconstruct diffusion tensors and convert to Sim4Life ordering
- import diffusion tensors and evaluate conductivity based on [Tuch et al.](https://www.pnas.org/content/98/20/11697.short) in Sim4Life
- visualize largest eigenvector of conductivity tensors
- convert label infos to a Sim4Life-compatible tissue list format
- import labels and extract surface model in Sim4Life
- setup Ohmic Quasi-Stationary simulation with inhom. anisotropic conductivity
