---
title: 贴图
---

所有的美术资源都将使用贴图库来完成。

<u>贴图（Sprite）也称精灵图，两者指同一概念。</u>

所有贴图的路径： `Resources/Sprites/`<br>
贴图库路径： `Scripts/Libraries/Sprites.lua`

覆盖引擎自带的贴图（例如替换默认的 `px.png` ）时，将同名图片放入 `Game/Resources/Sprites/` 即可，Game 区优先，主目录兜底。

---

## 创建一个贴图

使用 `Sprites.CreateSprite(path, layer)` 来创建一个贴图：

- `path` 贴图的路径，从 `Resources/Sprites/` 开始为根目录查找图片，需要加上 `.png` 后缀进行创建。
- `layer` 贴图的图层，可以使用 `数字` 或 `字符串` 。若没能顺着字符串找到对应图层，不会报错，而是自动把 layer 设置为 0 。

!!! example "创建一张图片"

    ```lua
    Sprites.CreateSprite("poseur.png", 0)
    ```

默认情况下，这张图片会生成到屏幕正中心，也就是 `(320, 240)` 的位置。

---

## 贴图的属性

属性设置分为 `直接属性` 与 `方法调用` 两类。

`直接属性` 通过点号（ `.` ）设置；<br>
`方法调用` 通过冒号（ `:` ）设置。

!!! tip "直接属性"
    - `x` 图片的水平坐标，越往右越大。
    - `y` 图片的竖直坐标，越往下越大。
    - `rotation` 图片的旋转角度，为 `角度制` ，角度增大时图片顺时针旋转。
    - `xscale` 图片水平方向上的缩放倍数，默认为 `1` ，表示原大小。
    - `yscale` 图片竖直方向上的缩放倍数，默认为 `1` ，表示原大小。
    - `layer` 图片的图层，数字越大图层越高。
    - `velocity` 图片的速度，设置一次即可让图片按速度持续运行下去：
        - `x` 水平方向速度。
        - `y` 竖直方向速度。
        - `r` 旋转速度。
    - `xpivot` 图片水平轴点，默认为 `0.5` ，代表图片水平方向上的正中心。
    - `ypivot` 图片竖直轴点，默认为 `0.5` ，代表图片竖直方向上的正中心。
    - `xpivot_px` 图片的水平轴点，按像素设置轴点。
    - `ypivot_px` 图片的竖直轴点，按像素设置轴点。
    - `xanchor` 在拥有父对象的前提下调整相对于父对象的水平方向偏移。
    - `yanchor` 在拥有父对象的前提下调整相对于父对象的竖直方向偏移。
    - `color` 图片的颜色，由一张三个 `0 ~ 1` 大小的数字组成。例如 `{1, 0, 0}` ，分别表示红绿蓝。
    - `alpha` 图片的透明度，由 `0 ~ 1` 的数字构成，数字越小图片越透明。
    - `visible` 图片是否可见，默认为 `true` 。
    - `pixel_snap` 这张图是否做像素吸附。默认跟随全局开关 `sprites.pixel_snap` （默认 `true` ）；单独写 `true` / `false` 可以只覆盖这一张。详见下方「像素吸附」。
    - `outline` 图片描边颜色和厚度，由五个参数构成 `{r, g, b, a, thickness}` ，分别代表 `{红, 绿, 蓝, 透明度, 厚度}`
    - `follow_mode` 用于跟随父对象的设置，支持两种，一个是 `position` ：表示只跟随位置，父对象旋转不进行干扰；第二种是 `full` ：跟随父对象的位置和旋转情况。
    - `isBullet` 是否为可伤害类型（弹幕类型），一个贴图就是通过此变量转化成弹幕的，默认 `false` 。
    - `HurtMode` 弹幕伤害的类型，例如：橙色、蓝色、红色、绿色。

!!! tip "方法调用"
    - `GetPivotOffset()` 获取当前锚点的像素偏移。
    - `GetFilter()` 获取当前图像所用的渲染方式。
    - `Dust(sound, remove, time)` 令一个图片化成尘埃。
        - `sound` 是否播放音效。
        - `remove` 播放完化尘后是否移除图片。
        - `time` 化尘动画播放多少秒。
    - `Outline(r, g, b, a, t)` 设置贴图的边框。
        - `r, g, b, a` 颜色与透明度，均为 `0 ~ 1` 的数值。
        - `t` 边框厚度，常用取值为 `2` 。
    - `SetFourPointMode(enabled)` 是否开启四角顶点模式，也就是常用的 `拉腿` 变形。
    - `SetFourPoint(p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y)` 四角顶点模式下的四个点位的坐标，按照顺序填写即可。
    - `SetFourPointP(index, x, y)` 设置四点中第 `index` 个点的坐标为 `(x, y)` 。
    - `Move(x, y)` 按 `(x, y)` 的速度移动贴图。
    - `MoveTo(x, y)` 将贴图移动到 `(x, y)` 的位置。
    - `Set(p)` 设置贴图的图片为 `p` 路径下的图片。（要带 `.png` 后缀）
    - `SetAnimation(frames, interval, mode)` 设置图片的动画，动画均由一张张图片组成
        - `frames` 动画所用的图片序列。
        - `interval` 每隔多少秒切换一次。
        - `mode` 动画使用什么模式进行播放，支持 `loop` 循环、 `oneshot` 只播放一次、 `empty` 只播放一次并清除。
    - `Scale(x, y)` 设置图片在水平和竖直方向上的缩放大小为 `(x, y)` 。
    - `Pivot(x, y)` 设置图片在水平和竖直方向上的锚点偏移为 `(x, y)` 。
    - `PivotPixel(x, y)` 设置图片在水平和竖直方向上的锚点像素偏移为 `(x, y)` 。
    - `Anchor(x, y)` 在拥有父对象的情况下，设置图片在水平和竖直方向上的锚点偏移为 `(x, y)` 。
    - `AnchorPixel(x, y)` 在拥有父对象的情况下，设置图片在水平和竖直方向上的锚点像素偏移为 `(x, y)` 。
    - `SetParent(spr)` 将某个贴图设置为当前贴图的父对象， `spr` 为创建好的贴图物体。
    - `SetChildren(children)` 将多个贴图物体设置为当前贴图的子对象。
    - `AddChild(child)` 给子对象组额外添加一个子对象 `child` 。
    - `RemoveChild(child)` 从子对象组中移除 `child` 贴图对象。
    - `GetPosition()` 获取图片的坐标，返回 `x, y` ，可用两个变量接收。
    - `GetPositionParent()` 获取父对象的坐标，返回 `x, y` ，可用两个变量接收。
    - `SetStencils(stencils)` 设置贴图的遮罩，可以使用多个遮罩。
    - `SetShaders(shaders)` 设置贴图的着色器为 `shaders` ，可以使用多个着色器。
    - `GetShaders()` 获取使用的着色器。
    - `ClearShaders()` 清除贴图所有的着色器。
    - `AddShader(shader)` 额外在末尾再添加一个着色器。
    - `InsertShader(index, shader)` 选择 `index` 位置插入着色器。
    - `RemoveShader(shader)` 从着色器列表中移除 `shader` 着色器。
    - `Solid(axis, box)` 给贴图添加一个碰撞体
        - `axis` 可选 `x` 方向或 `y` 方向或 `xy` 方向，代表仅在这个方向上拥有碰撞体积。
        - `box` 可填写 `width` 与 `height` 参数，例如：`{width = 1, height = 1}` ，此为 `1*1` 大小的碰撞盒。
    - `UnSolid()` 移除贴图身上的碰撞体。
    - `IsSolid()` 返回贴图当前是否拥有碰撞体。
    - `GetImagePath()` 返回这张贴图当前用的图片路径（已解析过的真实路径）。
    - `GetAnimationPath()` 返回当前动画的帧序列路径，没有动画时返回 `nil` 。
    - `SetPPCollision(enabled)` 开关这张图的**完美像素碰撞**，返回 `(成功, 矩形数量)` 。详见下方「完美像素碰撞」。
    - `IsPPCollision()` 返回这张图是否开着完美像素碰撞。
    - `SetHitboxShape(kind)` 把判定形状切成**椭圆**或矩形： `"ellipse"` / `"rect"` （别名 `circle` / `oval` 与 `rectangle` / `box` ），返回 `ok` 。详见下方。
    - `GetHitboxShape()` 返回当前种类，没设过就是 `"rect"` 。
    - `Destroy() / Remove()` 删除贴图。

!!! example "设置颜色与位置"

    ```lua
    local a = Sprites.CreateSprite("poseur.png", 0)
    a.color = {1, 0, 0}
    a:MoveTo(320, 0)
    ```

    运行后，图片变为红色并移动至 `(320, 0)` ，屏幕顶端只显示图片的下半部分。

---

## 库级方法

上述方法作用于单个贴图对象，以下方法由 `Sprites` 库提供：

!!! tip "库级方法"
    - `Sprites.CreateSpriteQuad(path, quad, layer)` 只取图片里 `quad` 指定的一块来创建贴图，`quad` 填 `{x = , y = , width = , height = }` 。用于图集（tileset）裁切。
    - `Sprites.MultiDust(sprs, sound, remove, time)` 让**一整组**贴图一起化成尘埃，整体按包围盒扩散，无需逐张调用 `Dust` 。
    - `Sprites.ShakeSprite(sprite, magnitude, duration, speed)` 让贴图抖动一段时间。`magnitude` 可以是一个数，也可以是 `{x = , y = }` 。
    - `Sprites.ShadowSprite(sprite, target_scale, duration, speed)` 生成一个跟着贴图放大淡出的影子，返回该影子贴图对象。
    - `Sprites.GetCacheInfo()` 返回 `(缓存数量, 明细列表)` ，用于查看当前图片缓存的内容。
    - `Sprites.CleanupCache()` 手动跑一次 LRU 清理（正常流程下引擎会按 `OPT_LRU_SPRITES` 自动跑）。

---

## 每帧回调 Step

为贴图挂载 `Step` 函数后，引擎每帧自动调用，可用于飘动、跟随、计时自毁等逻辑：

```lua
spr.Step = function (self, dt)
    -- 每帧一次
end
```

骨头与蓝灵魂平台上也有同名钩子，该钩子不传入 `dt` 。完整说明见 [Step 每帧回调](./170_step.md) 。

---

## 像素吸附

贴图坐标带小数时，采样出的边缘会明暗闪烁，即半像素抖动。引擎默认启用像素吸附。

全局开关是 `sprites.pixel_snap` （默认 `true` ），也可以用 `Sprites.SetPixelSnap(enabled)` 改；单张图可以自己覆盖：

```lua
sprites.pixel_snap = false      -- 全局关掉
Sprites.SetPixelSnap(true)      -- 全局打开
spr.pixel_snap = false          -- 只放过这一张
```

吸附的规则是**吸边、不吸中心**：真正被取整的是四边形四条**边**所在的坐标，不是图片的中心点。这两者只有在图片尺寸为偶数时才刚好相等，所以奇数尺寸的贴图直接用中心取整会歪半像素。

由多个零件拼合的复合体（例如骨头的头 / 身 / 尾）需**只对共享锚点取整一次**：将各零件设为 `pixel_snap = false` ，再用 `Sprites.SnapEdge(centre, offset)` 吸附锚点，然后按锚点摆放零件。若各零件分别取整，接缝处会错位。

- `Sprites.SnapCoord(v)` 单个数取整，等价于 `math.floor(v + 0.5)` 。
- `Sprites.SnapEdge(centre, offset)` 把「边」吸到整数： `centre` 是中心坐标， `offset` 是这条边相对中心的偏移（例如半宽），返回吸附后的中心坐标。

!!! warning "旋转过的贴图不适用边吸附"
    贴图旋转角度后，四边形不再与坐标轴平行，`SnapEdge` 不再适用。旋转件不执行吸附，其几何结果与关闭吸附时一致。

---

## 完美像素碰撞

默认的碰撞判定用的是包围盒：一张 32×32 的心形图，判定就是一个 32×32 的方框。想让判定贴着贴图真实的像素形状，就把这张图开起来：

```lua
spr:SetPPCollision(true)    -- 返回 ok, 矩形数量
spr:SetPPCollision(false)   -- 退回普通包围盒
spr:IsPPCollision()         -- 查询当前状态
```

!!! tip "圆形与椭圆使用形状判定"
    若所需形状为圆或椭圆，使用 `spr:SetHitboxShape("ellipse")` 即可完成判定，无需矩形化，也无需逐帧遍历多个小方框：

    ```lua
    spr:SetHitboxShape("ellipse")   -- 这张图按椭圆判定
    spr:SetHitboxShape("rect")      -- 退回方框（默认）
    spr:GetHitboxShape()            -- -> "ellipse" / "rect"
    ```

    椭圆内切于同一个方框，只削去四个角，见
    [进阶 → 碰撞判定](../../050_intermediate/030_collision.md) 。
    椭圆无法描述的美术形状使用完美像素碰撞。

判定本身用 `Sprites.PPCollide(a, b)` ：

```lua
local ok = Sprites.PPCollide(bullet, Player.sprite)
-- true  = 真的撞上了
-- false = 没撞上
-- nil   = 两边都没开完美像素，请沿用包围盒的结论
```

该函数**仅在至少一方启用完美像素碰撞时返回结果**，返回 `nil` 时沿用包围盒的判定结论。

!!! warning "开启后判定范围会变大"
    完美像素使用贴图的**不透明像素**判定。16×16 的心形图启用后，判定范围大于默认的居中 `{4, 4}` 方框。需要擦弹手感时使用 `_hitbox` ，需要贴合形状时使用完美像素，两者择一。

相关辅助：

- `Sprites.GetPPRects(sprite)` 拿到这张图在本地坐标下的所有矩形。
- `Sprites.GetPPShapes(sprite)` 拿到转成世界坐标后的形状。
- `Sprites.GetHitbox(sprite)` 一步得到「包围盒 + `_hitbox` 覆盖」的结果，战斗里判灵魂判定用的就是它。
- `Sprites.ClearPPCache()` 清空矩形缓存。热重载了库或者贴图之后调一次。

底层的矩形化算法在 `Scripts/Libraries/PerfectPixel/` ，有 C 后端（ `cpp.dll` ）与纯 Lua 版（ `pure.lua` ）两份，前者约快 10 倍，可用时自动启用。按 `F7` 可打开碰撞箱叠加层查看判定形状，见 [战斗系统 → 战斗场景](../030_battle_system/070_scene.md) 。

---

## 关于颜色

在这里，颜色被分为 `红、绿、蓝` 三种基本色，后续所有颜色均通过这三个颜色调配而成。

以下列出常用颜色：

- `{1, 0, 1}` KR的大粉色，通过红蓝同比例调配而成。
- `{0.4, 0, 1}` 紫色，但是略显深蓝。
- `{0, 1, 1}` 蓝色攻击的青色骨头颜色。
- `{1, 0.5, 0}` 橙色攻击。
- `{1, 1, 0}` 黄色的确认。

### 浅色与深色

调整深浅时，向颜色中加入白色或黑色。

红色为 `{1, 0, 0}` ，加入 `黑色` `{0, 0, 0}` 得到深色。

逐项相加后取平均：<br>

- `(1 + 0) / 2 = 0.5` 第一项变为 0.5。
- `(0 + 0) / 2 = 0` 第二项变为 0。
- `(0 + 0) / 2 = 0` 第三项变为 0。

得到深红色： `{0.5, 0, 0}` 。

浅色同理：

- `(1 + 1) / 2 = 1` 第一项变为 1。
- `(0 + 1) / 2 = 0.5` 第二项变为 0.5。
- `(0 + 1) / 2 = 0.5` 第三项变为 0.5。

得到浅红色： `{1, 0.5, 0.5}` 。

**该方法的变化幅度可能过大，可将加入的值由 `1` 改为 `0.5` 等较小数值。**

### 彩虹色

对 `{r, g, b}` 进行三角函数周期变换操作，通过调整相位，可以做出彩虹色的效果。

```lua
r = math.sin(time / 8 + 0)
g = math.sin(time / 8 + 8)
b = math.sin(time / 8 + 16)
```

将上述 rgb 应用到贴图的 `color` 上，贴图颜色会按周期变化，呈现彩虹色。