---
title: 角色
---

主世界中可移动的玩家角色。它由一个物理体驱动，一张贴图跟随，行走动画按贴图帧轮播。

模块路径： `Scripts/Libraries/Overworld/char.lua` ，以全局 `Char` 出场。

---

## 走路贴图

四向各一组帧，默认用 `Frisk` 那套：

```lua
Char.sprites = {
    up    = {"Overworld/Frisk/spr_f_maincharau_0.png", ...},
    down  = {"Overworld/Frisk/spr_f_maincharad_0.png", ...},
    left  = {"Overworld/Frisk/spr_f_maincharal_0.png", ...},
    right = {"Overworld/Frisk/spr_f_maincharar_0.png", ...},
}
```

!!! example "贴图方法"
    - `Char.SetPlayerSprites(tab)` 整组替换。表结构必须和上面一致（四个方向各一个数组）。
    - `Char.SetPosition(x, y, direction)` 设置位置与朝向。地图载入后由引擎自动调用。
    - `Char.Init()` 创建贴图与物理体。地图载入时自动调用，通常无需手动调用。
    - `Char.Destroy()` 销毁贴图与物理体。

!!! tip "替换主角贴图无需修改代码"
    这些路径由 `Sprites` 解析，遵循**Game 区优先**规则。<br>
    若需替换角色，将同名文件放入 `Game/Resources/Sprites/Overworld/Frisk/` 即可被自动使用（前提是**文件名与帧数一致**）。<br>
    另一种方式是在场景中调用 `Char.SetPlayerSprites{...}` 替换为另一套路径。

贴图的**锚点在脚底**，因此 `Char.currentSprite.y` 比物理体的 `y` 小 `20` （半个身位）。获取玩家脚下位置时使用精灵坐标，获取碰撞体位置时使用 `Char.collision.body` 。

---

## 属性

!!! example "Char 属性"
    - `currentSprite` 当前贴图对象。玩家尚未生成时为 `nil` ，编写场景逻辑时需判空。
    - `direction` 当前朝向（ `"up"` / `"down"` / `"left"` / `"right"` ）。
    - `controlling` **玩家能不能操作**。对话、菜单、存档页都会把它置为 `false` 。
    - `isMoving` 这一帧是否真的移动了。
    - `animationFrame` / `animationTime` 走路动画帧号与计时。
    - `x` / `y` 出生（或最近一次 `SetPosition` ）的坐标。
    - `collision.body` / `.shape` / `.fixture` 物理三件套。碰撞盒默认 `38 x 20` 。
    - `friskdance` 是否启用 Frisk Dance 彩蛋（读自全局开关 `EnableFriskDance` ）。
    - `frisk_dancing` 此刻是否正在跳。

---

## 锁定操作

所有**打断玩家**的界面都通过 `Char.controlling` 实现：

```lua
Char.controlling = false   -- 玩家停下、不再读输入
-- ... 演出 ...
Char.controlling = true    -- 恢复
```

`Overworld.dialogNew` 、 `Save.Show` 、 `Chest.Show` 与 `Stat` 菜单都会自行维护该字段，因此正常流程中无需干预——**除非自行实现了需要锁定玩家的界面**。

!!! warning "未恢复 `controlling` 的后果"
    设为 `false` 后未恢复时，玩家将持续无法移动，且不会有任何报错提示。

---

## Frisk Dance

原版中**贴着墙按上+下**触发的彩蛋。开关为全局变量 `EnableFriskDance` ，引擎启动时会读入 `Char.friskdance` 。

- **开始**：面朝上、正顶着墙、同时按住上+下。
- **维持**：持续按住上+下，并且**竖直方向位移为 0**（即仍贴着墙），就会继续跳——**左右滑动不算中断**。
- **中断**：竖直方向一旦发生位移（走离墙面、被顶穿、掉落），或松开上/下，立即停止并转回面朝上。

跳跃时角色在 `up` / `down` 两组贴图之间切换，同时仍可左右移动。

如需关闭，在场景中设置：

```lua
Char.friskdance = false
```

---

## 移动的实现

`Char.Update` 每帧执行四步：

1. 读取四个方向键，计算速度（每帧 `±2` ）。
2. 记录**第一个按下的方向**，在松开之前不会被其他方向取代，因此改变方向前必须先松开按键。
3. 将速度写入物理体，由 Box2D 处理撞墙。
4. 让贴图跟随物理体，并按速度切换行走帧。

!!! tip "顶到墙的判定条件"
    引擎判定**顶到墙**的方式是：物理体该帧在**竖直方向位移为 0**。斜向推动不满足该条件，必须先正对墙面；同理，跳跃过程中竖直方向一旦滑动，判定即失效，彩蛋中断。<br>
    判定带 `0.5` 像素的容差，因此贴墙时的细微抖动不会导致判定失效。

---

## 传送玩家

不切换场景，仅改变玩家位置：

```lua
Char.collision.body:setPosition(x, y)   -- 物理体
Char.SetPosition(x, y, "down")          -- 同步记录
```

切场景则走 `Overworld.ChangeScene` ，详见 [交互与对话](./030_interact.md) 。
