# -*- coding: utf-8 -*-
# First create a spline called 'FlyThru'
# Execute script to smoothly move the view, following the path described by the spline
#
import os
import screenshots
import XCore
import XCoreModeling as model
import XCoreModeling
import time
import json
import copy
from quaternions import quaternions as quat
import win32gui

global _CAMERA

_CAMERA = None


def refresh_view():
    """allows Sim4Life GUI to refresh itself"""
    win32gui.PumpWaitingMessages()


def get_keyframes():
    configfile = get_config_file()
    if os.path.exists(configfile):
        keyframes = json.load(open(configfile, "r"))
    else:
        keyframes = {}
    return keyframes


def get_config_file():
    document = XCore.GetApp().Document
    assert (
        len(document.FilePath) > 1
    ), "Please save a smash file so we can store the configuration"
    configfile = document.FilePath[0:-5] + "json"
    return configfile


def get_current_camera(force_perspective=True, update_to_current_view=True):
    global _CAMERA
    if not update_to_current_view and _CAMERA is not None:
        cam = _CAMERA
        _CAMERA.Parent.OnChildModified.DisconnectAll()  # attempt to fix memory leak when camera settings are changed...
    else:
        print(
            "creating new Camera object - do not do that too often, it is not good for the UI..."
        )
        cam = screenshots.set_camera("current", 0)
        _CAMERA = cam
    if force_perspective:
        cam.Perspective.Value = True
    return cam


def save_keyframes_to_config_file(keyframes, config_file):
    json.dump(keyframes, open(config_file, "w"))


def view_to_keyframe():
    cam = get_current_camera()
    keyframe = {
        "OrbitCenter": list(cam.OrbitCenter.Value),
        "Orientation": list(cam.Orientation.Value),
        "Distance": cam.Distance.Value,
    }
    return keyframe


def register_keyframe(keyframe):
    key = keyframe["Id"]
    keyframes = get_keyframes()
    if key in keyframes:
        print("overwriting existing keyframe with id: {}".format(key))
    else:
        print("registering keyframe with id: {}".format(key))
    keyframes[key] = copy.deepcopy(keyframe)
    print(keyframe)
    save_keyframes_to_config_file(keyframes, get_config_file())


def deregister_keyframe(keyframe):
    """remove keyframe from datastructure"""
    key = keyframe["Id"]
    keyframes = get_keyframes()
    try:
        keyframes.pop(key)
        save_keyframes_to_config_file(keyframes, get_config_file())
    except KeyError:
        print("could not find keyframe with key {} in keyframes dictionary".format(key))


def get_keypoints_group():
    try:
        key_points_group = {e.Name: e for e in model.GetActiveModel().GetEntities()}[
            "KeyFrames"
        ]
    except KeyError:
        key_points_group = model.CreateGroup("KeyFrames")
    return key_points_group


def save_keyframe():
    keyframe = view_to_keyframe()
    ref_point = model.CreatePoint(model.Vec3(keyframe["OrbitCenter"]))
    keyframe["Id"] = ref_point.Id.str()
    ref_point.Name = "Frame %03.f" % len(get_keyframes())
    register_keyframe(keyframe)
    key_points_group = get_keypoints_group()
    key_points_group.Add(ref_point)


def delete_selected_keyframes():
    for keyframe, point in get_selected_keyframes():
        deregister_keyframe(keyframe)
        point.Delete()


def replace_selected_keyframe():
    """replace selected keyframe with current view"""
    keyframe, point = get_selected_keyframe()
    new_keyframe = view_to_keyframe()
    new_keyframe["Id"] = keyframe["Id"]
    point.Transform = model.Translation(
        model.Vec3(new_keyframe["OrbitCenter"])
    )  # is that really the only way to change the position of a point??
    point.EvaluateParameters()
    register_keyframe(new_keyframe)


def load_keyframe_from_point(point_entity):
    keyframes = get_keyframes()
    keyframe = keyframes[point_entity.Id.str()]
    keyframe["Name"] = point_entity.Name
    return keyframe


def load_keyframes():  # sorted by Name
    key_points_group = {e.Name: e for e in model.GetActiveModel().GetEntities()}[
        "KeyFrames"
    ]
    return [
        load_keyframe_from_point(p)
        for p in sorted(key_points_group.Entities, key=lambda x: x.Name)
    ]


def get_selected_keyframe():
    point = XCoreModeling.GetActiveModel().SelectedEntities[0]
    return load_keyframe_from_point(point), point


def get_selected_keyframes():
    points = XCoreModeling.GetActiveModel().SelectedEntities
    for point in points:
        yield load_keyframe_from_point(point), point


def view_selected_keyframe():
    view_from_keyframe(get_selected_keyframe()[0])


def view_from_keyframe(keyframe, delay=0, callback=None, param=0.0):
    cam = get_current_camera(update_to_current_view=False)
    cam.OrbitCenter.Value = model.Vec3(keyframe["OrbitCenter"])
    cam.Orientation.Value = keyframe["Orientation"]
    cam.Distance.Value = keyframe["Distance"]
    screenshots.set_view(cam)

    if callback:
        callback(param)

    time.sleep(delay)
    if "Name" in keyframe:
        print("Keyframe: %s" % keyframe["Name"])
    else:
        print("Keyframe: interpolated")
    refresh_view()


def fly_keyframes(
    nb_subframes, delay, max_frames, interp_mode, restore_view=True, callback=None
):
    first_frame = True

    keyframes = quat.interpolate_keyframes(
        load_keyframes(), num=nb_subframes, mode=interp_mode
    )
    num_keyframes = len(keyframes)

    for i, keyframe in enumerate(keyframes):
        print("frame number {}".format(i))
        s = i / float(num_keyframes)
        view_from_keyframe(
            keyframe, delay=1.0 if first_frame else delay, callback=callback, param=s
        )
        first_frame = False
        if i > max_frames:
            break
    # restore view
    if restore_view:
        view_from_keyframe(load_keyframes()[0])


def main(**kwargs):
    nb_subframes = kwargs.pop(
        "nb_subframes", 10
    )  # number of interpolated frames between 2 keyframes
    delay = kwargs.pop(
        "delay", 0.5
    )  # number of seconds to wait for the view to refresh, between 2 frames
    max_frames = kwargs.pop("max_frames", 150)
    interp_mode = kwargs.pop("interp", "cubic")

    fly_keyframes(
        nb_subframes=nb_subframes,
        delay=delay,
        max_frames=max_frames,
        interp_mode=interp_mode,
        callback=None,
    )


if __name__ == "__main__":
    main()
