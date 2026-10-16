---
title: Layers System
---

Besides sprites and Typers, we can also directly use Layers to create content, managed directly under the Layers.

Management file path: `Scripts/Libraries/Layers.lua`.

Note: this library was written relatively early, so you will most likely see functions named in snake_case, while other libraries use camelCase naming.

---

## Creating a Layer

Use `Layers.new_layer(name, layer)` to create a Layer.

- `name` The Layer's name.
- `layer` Roughly which level this Layer is.

Since the created Layer is only for convenient direct use during development, it ultimately has to be categorized into a number, after all only numbers are most convenient for Layer ordering.

!!! example "Layer creation in the battle system"

    ```lua
    Layers.new_layer("BOTTOM", -1000)
    Layers.new_layer("Background", -10)
    Layers.new_layer("UI", 0)
    Layers.new_layer("ArenasExtraW", 10)
    Layers.new_layer("ArenasExtraB", 10.01)
    Layers.new_layer("UponArena", 11)
    Layers.new_layer("BelowPlayer", 12)
    Layers.new_layer("Player", 13)
    Layers.new_layer("BelowBullets", 25)
    Layers.new_layer("Bullets", 30)
    Layers.new_layer("ArenasCoverW", 50)
    Layers.new_layer("ArenasCoverB", 50.01)
    Layers.new_layer("TopAll", 60)
    Layers.new_layer("TOP", 1000)
    ```

If the Layer with the entered name does not exist (most likely not created or mistyped), it is automatically defined as `0`.

When mistyped, a warning pops up in the sidebar and does not affect gameplay:

!!! warning "Terminal hint"
    `[WARNING] Layers.add: Layer "xxx" not found, defaulting to 0`

---

## Editing a Layer

Besides creating, you can also perform operations like removal; the table below gives all methods:

??? example "Layer operations"
    - `get_layer(name)` Returns the Layer with this name, returns `nil` directly if it does not exist.
    - `remove_layer(name)` Deletes the Layer matching this name.
    - `set_layer_active(name, active)` Whether to enable the Layer with this name.
    - `add(obj)` Adds an object to a Layer.
    - `remove(obj)` **Detaches** `obj` from the Layer system — only detaches, does not destroy. To also destroy, use the following line:
        ```lua
        Layers.get_layer("Bullets"):remove(obj)   -- remove from the specified layer, and call obj:Destroy()
        ```
    - `add_external(draw_func, layer)` Draw function and Layer height.
    - `remove_external(t)` Since `add_external` returns a table, put it in this function to delete it.
    - `remove_externals(list)` Clears all `external` content written in `list`.
    - `remove_external_by_layer(layer)` Clears all `external` draw content of a certain layer.
    - `clear_external()` Clears all `external` draw operations across all Layers.
    - `sort()` Not commonly used; sorts objects inside a Layer by Layer size.
    - `make_dirty()` Not commonly used; re-issues the sort signal to make sort run.
    - `draw()` Located in `main.lua`; here it draws all sprites and Typers.
    - `clear() / Clear()` Commonly called when cleaning up and exiting a Scene.
    - `count()` Returns how many objects are now in the Layer.
    - `external_count()` Returns how many `external` draw operations are now in the Layer.
    - `find_by_id(id)` Finds a Layer, object, or `external` draw operation via the unique `_id` property.
    - `debug()` Prints the Layer's current internal info, including how many objects, how many layers, how many `external` draw operations, etc.

---

## Drawing Directly with Layers

As said at the beginning, this part is actually the focus.

Use `Layers.add_external(draw_func, layer)` to draw content.

- `draw_func` The draw function. For more detail on how to draw and what methods are available, see [With LOVE Development → Graphics](../060_with_love/000_graphics.md); only a case is provided here.
- `layer` The Layer height it is at.

!!! example "draw_func case"

    ```lua
    local font = Fonts.New("determination_mono.ttf", 27, "mono")

    Layers.add_external(function ()
        SE.graphics.setFont(font)
        SE.graphics.printf("Name the fallen human", 0, 40, 640, "center")
    end, 0)
    ```
