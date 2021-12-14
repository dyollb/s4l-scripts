# -*- coding: utf-8 -*-
import XRendererUI
import XCore
from XCoreModeling import Vec3
import numpy as np
import os

import win32gui
import time

import random, string


def randomword(length):
    return "".join(random.choice(string.lowercase) for i in range(length))


def camera(viewname, distance, target, theta):
    cam = XRendererUI.SaveCamera("")  # load or create a new camera setting
    cam.OrbitCenter.Value = Vec3(0, 0, 0)
    cam.Distance.Value = distance
    target.Normalize()

    cam.Orientation.Value = [np.cos(theta / 2.0)] + list(
        np.sin(theta / 2) * target
    )  # quaternions
    return cam


def set_camera(keyword, distance):
    if keyword == "current":
        cam = XRendererUI.SaveCamera(
            randomword(20)
        )  # create a new camera setting from current view settings
    elif keyword == "XY":
        cam = camera("XY", distance, Vec3(1, 0, 0), -np.pi / 2.0)
    elif keyword == "XZ":
        cam = camera("XZ", distance, Vec3(0, 1, 0), np.pi / 2.0)
    elif keyword == "YZ":
        cam = camera("YZ", distance, Vec3(0, 0, 1), np.pi / 2.0)
    elif keyword == "ZXY":
        cam = camera("ZXY", distance, Vec3(1, 1, 1), np.pi)
    else:
        raise RuntimeError("Invalid option (%s) for camera setting" % keyword)
    return cam


def set_view(cam):
    XRendererUI.RestoreCamera(cam)


def makeScreenshots(
    target_dir=None,
    distance=200.0,
    transparent_bg=True,
    delay=0.001,
    width=1024,
    height=1024,
    prefix="",
    views="default",
):

    if target_dir is None:
        target_dir = XCore.GetApp().Document.FileFolder
    assert os.path.exists(target_dir)

    if views == "default":
        viewnames = ["XY", "XZ", "YZ", "ZXY"]
    else:
        viewnames = views
    assert all(
        [view in ["current", "XY", "XZ", "YZ", "ZXY"] for view in viewnames]
    ), "View not implemented"

    screenshot_paths = []
    for viewname in viewnames:
        cam = set_camera(viewname, distance)
        set_view(cam)

        time.sleep(delay)  # wait for 3D rendering to complete
        win32gui.PumpWaitingMessages()  # update view

        filename = XCore.GetApp().Document.FileName
        if not prefix:
            prefix = os.path.splitext(filename)[0]
        screenshot_name = prefix + "_" + viewname

        # Workaround to remove counter
        # delete file if it already exists
        actual_screenshot_name = os.path.join(target_dir, screenshot_name + "-001.png")
        desired_screenshot_name = os.path.join(target_dir, screenshot_name + ".png")
        if os.path.isfile(desired_screenshot_name):
            os.remove(desired_screenshot_name)

        XRendererUI.SaveScreenCapture(
            width=width,
            height=height,
            output_folder=target_dir,
            output_prefix=screenshot_name,
            transparent_background=transparent_bg,
        )

        # actual_screenshot_name = os.path.join(target_dir, os.path.splitext(filename)[0] + '-001.png')
        os.rename(actual_screenshot_name, desired_screenshot_name)

        screenshot_paths.append(desired_screenshot_name)

    return screenshot_paths


# Example usage:
# Take 4 screenshots at a distance of 200 units from 4 different view angles
# and place the pictures (PNG files) in the same folder as the project file.

if __name__ == "__main__":
    makeScreenshots(distance=200.0, transparent_bg=True)
