---
title: Creating and Switching Scenes
---

A scene can be imagined as you creating a new `world`.<br>
All operations within this world are defined by you.

---

## Creating a Scene

In `SoulEngine`, there are two base scene templates: `scene_template.lua` and `scene_template_full.lua`.

When first starting out, we just copy the lightweight `scene_template.lua`.

Place it in the path `Scripts/Scenes/`, <u>i.e. in the same directory as `scene_template.lua`</u>. To override an engine-built-in scene, put a same-named file into `Game/Scenes/`, where the Game area takes priority and the engine directory is the fallback.

!!! tip "Adjust the initialization config"
    After that, don't forget to change `FirstRoom` in `Game/conf_pure.lua` to the name of the scene you just created.

---

## Editing a Scene

### Scene Content

```lua
local scene = {}

function scene.update(dt)
end

function scene.draw()
end

function scene.clear()
    Layers.clear()
end

return scene
```

The lightweight scene contains only this code internally. You may notice that this code divides the entire scene into several different parts. Their functions are as follows:

!!! tip "Same-level code"
    Here, we grade by `number of wrapping levels`.<br>
    In short, the region inside a `function - end` wrapper counts as one level.

    If there is a new wrapper block, it adds another level.

1. The first-level region, outside all `function - end` regions and before `return`, executes <u>exactly once</u> the moment you enter the scene.
2. The second-level region, inside a `function`, executes under specific circumstances.

In more detail:

- The region inside `scene.update` executes every moment (frame), about `60` times per second (default).
- The region inside `scene.draw` executes every moment (frame), about `60` times per second (default).

### Creating the First Feedback

Let's assume you successfully copied and pasted a new scene. Please type the following code in the `first-level region` range:
```lua
print("This is my new scene")
```

After that, when you enter the scene, the console will show the text inside print, which means you succeeded.

### Android Test Feedback

On Android, if there's no console to look at and you don't know whether you've successfully switched to the scene you just wrote, you can copy the following code into the scene's `first-level region`:
```lua
Sprites.CreateSprite("poseur.png")
```

The code above creates a `Poseur` image at the center of the screen.
