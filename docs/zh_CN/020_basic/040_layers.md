---
title: 图层系统
---

除贴图与打字机外，也可直接使用图层创建内容，由图层管理。

管理文件路径： `Scripts/Libraries/Layers.lua` 。

注：本库编写时间较早，函数使用下划线命名法，其他库均使用驼峰命名法。

---

## 新建图层

使用 `Layers.new_layer(name, layer)` 来创建一个图层。

- `name` 图层的名字。
- `layer` 该图层所在的层级。

创建的图层名最终对应到数字层级，图层排序以数字为准。

!!! example "战斗系统中的图层创建"

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

若输入的图层名不存在，图层会自动定义为 `0` 。

此时侧边栏会输出警告，不影响游戏运行：

!!! warning "终端的提示"
    `[WARNING] Layers.add: Layer "xxx" not found, defaulting to 0`

---

## 编辑图层

除了新建，还可以执行移除等操作，下面这个表给出了所有方法：

??? example "图层操作"
    - `get_layer(name)` 返回这个名字的图层，如果不存在直接返回 `nil` 。
    - `remove_layer(name)` 删除符合这个名字的图层。
    - `set_layer_active(name, active)` 是否开启这个名字的图层。
    - `add(obj)` 给一个图层添加物体。
    - `remove(obj)` 将 `obj` 从图层系统中**移除**，不销毁对象。需要同时销毁时使用下面的写法：
        ```lua
        Layers.get_layer("Bullets"):remove(obj)   -- 从指定图层移除，并调用 obj:Destroy()
        ```
    - `add_external(draw_func, layer)` 绘制函数与图层高低。
    - `remove_external(t)` 删除 `add_external` 返回的表 `t` 。
    - `remove_externals(list)` 以 `list` 为准清除里面写过的所有 `external` 内容。
    - `remove_external_by_layer(layer)` 清除某一层的所有 `external` 绘制内容。
    - `clear_external()` 清除所有图层关于 `external` 绘制的操作。
    - `sort()` 按图层大小对图层内的物体排序。
    - `make_dirty()` 重新发出排序信号，使 `sort` 运行。
    - `draw()` 位于 `main.lua` 中，对所有贴图与打字机执行绘制操作。
    - `clear() / Clear()` 常见于清理退出场景时调用。
    - `count()` 返回图层中当前的物体数量。
    - `external_count()` 返回图层中当前的 `external` 绘制操作数量。
    - `find_by_id(id)` 通过唯一 `_id` 属性查找图层、物体或 `external` 绘制操作。
    - `debug()` 打印当前图层的内部信息，包括物体数量、层数与 `external` 绘制操作数量等。

---

## 直接使用图层绘制

本节说明直接使用图层绘制的方式。

使用 `Layers.add_external(draw_func, layer)` 来绘制内容。

- `draw_func` 绘制函数。可用的绘制方法见 [与LOVE开发 → 图像绘制](../060_with_love/000_graphics.md) 专题，此处仅提供示例。
- `layer` 所处的图层高低。

!!! example "draw_func案例"

    ```lua
    local font = Fonts.New("determination_mono.ttf", 27, "mono")

    Layers.add_external(function ()
        SE.graphics.setFont(font)
        SE.graphics.printf("Name the fallen human", 0, 40, 640, "center")
    end, 0)
    ```