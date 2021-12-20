import random
from pathlib import Path
from typing import Dict


def load_stanford_label_info(file_path: Path) -> Dict[int, str]:
    """Load tissue names and labels from stanford example dataset

    Args:
        file_path: label info file to parse

    The file is assumed to by in CSV format with 3 columns, where the first row is a header, e.g.

        new label, freesurfer label, freesurfer name
        1, 2, "Left-Cerebral-White-Matter"
        1, 41, "Right-Cerebral-White-Matter"
        1, 77, "WM-hypointensities"
        ...
    """
    with open(file_path, "r") as f:
        lines = f.readlines()
    label_info: Dict[int, str] = {}
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) != 3:
            continue
        label = int(parts[0].strip())
        name = parts[2].strip().strip('"').replace(" ", "_")
        if label in label_info:
            label_info[label] += f"_{name}"
        else:
            label_info[label] = name
    return label_info


def save_iseg_label_info(label_info: Dict[int, str], file_path: Path):
    """save label info dictionary as iSEG compatible tissue list

    Args:
        tissue_list: input label info dictionary
        file_path: tissue list file

    Example file:
        V7
        N3
        C0.00 0.00 1.00 0.50 Bone
        C0.00 1.00 0.00 0.50 Fat
        C1.00 0.00 0.00 0.50 Skin
    """
    max_label = max(label_info.keys())
    tissue_names = ["tissue%03d" % i for i in range(max_label + 1)]
    for id, name in label_info.items():
        tissue_names[id] = name

    with open(file_path, "w") as f:
        print("V7", file=f)
        print("N%d" % max_label, file=f)
        for i in range(1, max_label):
            # assign random color
            r = random.randint(0, 255) / 255.0
            g = random.randint(0, 255) / 255.0
            b = random.randint(0, 255) / 255.0
            print("C%.2f %.2f %.2f 0.50 %s" % (r, g, b, tissue_names[i]), file=f)


if __name__ == "__main__":
    label_info_file = Path("/Users/lloyd/Models/StandfordData") / "label_info.txt"
    label_info = load_stanford_label_info(label_info_file)
    save_iseg_label_info(label_info, label_info_file.parent / "label_info_iseg.txt")
