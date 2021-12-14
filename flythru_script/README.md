# Fly-through
This folder contains scripts to control the camera view in Sim4Life, e.g. to create animations.

The flythru tools allow to animate flying through a scene in Sim4Life. Following steps should provide enough information to use these tools:
- run the script `tool_flythru.py`
  - set the camera settings (orbit, zoom etc.)
  - to create keyframe *points* would call `save_keyframe()` from the interactive terminal
  - repeat until you have the whole sequence
- the keyframes are attached to the entities in the `EntityGroup` **KeyFrames**
- to run the animation, call
```
fly_keyframes(20, 0.5, 10000, 'cubic', restore_view=False)
```
