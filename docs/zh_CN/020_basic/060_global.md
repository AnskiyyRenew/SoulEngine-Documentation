---
title: 全局变量
---

全局变量通常指的是在游戏任何一个地方都可以获取或修改的变量，也包括存储变量在内。

全局库路径： `Scripts/Libraries/Global.lua`

---

## 游戏内全局变量

这类游戏变量在退出游戏后就会消失清空，通常只用在游戏内划分阶段等操作。

使用 `Global.SetVariable(name, value)` 来设置一个名为 `name` 的全局变量。

- `name` 全局变量的名字。
- `value` 全局变量的值。支持字符串、数字、布尔值、表、函数等类型，也包括 `io` 打开的文件。

!!! example "设置全局变量"
    将名为 `name` 的全局变量设置为 `Chara` 。
    ```lua
    Global.SetVariable("name", "Chara")
    ```

使用 `Global.GetVariable(name)` 来获取一个名为 `name` 的全局变量的值。

!!! example "获取全局变量"
    获取名为 `player` 的全局变量。
    ```lua
    Global.GetVariable("player")
    ```

使用 `Global.EnsureVariable(name, value)` 获取已有的全局变量；若不存在，则创建值为 `value` 的全局变量。

!!! warning "EnsureVariable 在新建那一次返回 `nil`"
    该函数仅在变量**已存在**时返回值；新建的那一次只赋值，不返回值。写成 `local x = Global.EnsureVariable("x", 1)` 时，首次调用得到的 `x` 为 `nil` 。

    获取值时需再调用一次 `GetVariable`：

    ```lua
    Global.EnsureVariable("config", {master = 1, sfx = 1})
    local config = Global.GetVariable("config")
    ```

!!! example "框定全局变量"
    如果 `config` 现在还不存在，以 `{master = 1, sfx = 1}` 为值创建一个 `config` 变量，若存在则直接读取 `config` 。
    ```lua
    Global.EnsureVariable("config", {
        master = 1,
        sfx = 1
    })
    ```

**不使用 `EnsureVariable` 时，也可手动检测 `nil` 并调用 `GetVariable` ：**

!!! example "原始方法"
    非条件判断中的 `or` 用法见 [短路选择](../000_before/020_lua.md) 专题。<br>
    该写法可直接取得值，因为 `SetVariable` 会把设置的值**返回**出来。
    ```lua
    local config =  Global.GetVariable("config") or
                    Global.SetVariable("config", {
                        master = 1,
                        sfx = 1
                    })
    ```

---

## 本地存储变量

此栏目下的变量都会存储在本地，适用于游戏存档读档等操作。<br>
注：不是 `PS Flowey` 的存档读档攻击，这是单独的战斗效果。

!!! tip "函数区别"
    - 所有 `set` 、 `get` 、 `ensure` 操作在名称后加 `save` 。
    - 仅支持存储：字符串、数字、表。

以下列出全部函数名称，用法与上一节一致：

- `Global.SetSaveVariable(name, value)`
- `Global.GetSaveVariable(name)`
- `Global.EnsureSaveVariable(name, value)`
- `Global.DeleteSaveVariable(name)`

额外的 `Delete` 操作用于清除存储，可用于重置存档。

**对表的存储操作使用的库为 `dkjson` ，使用详情见 [高阶开发 → JSON 库](../050_intermediate/000_dkjson.md)**