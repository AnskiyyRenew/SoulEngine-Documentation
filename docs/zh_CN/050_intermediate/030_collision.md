---
title: 碰撞库
---

碰撞库负责"两个形状有没有重叠"的**判定**，不管移动、不管推挤。

路径： `Scripts/Libraries/Collisions.lua`

它在 `main.lua` 里被导入成全局 `Collisions` ，可直接使用，无需自行 `ImportFile` ：

```lua
-- main.lua 顶部
Collisions = ImportFile("Collisions")
```

!!! note "还有一个小写别名"
    兼容层 `Scripts/Libraries/Engine/2_0.lua` 里额外挂了 `collisions`（全小写）。
    两者是同一个表，统一使用大写 `Collisions` 便于检索，也不会与局部变量重名。

---

## 形状表

库里所有函数都用同一种"形状表"描述一个矩形/椭圆：

```lua
{
    x = 320,    -- 中心 x（世界坐标）
    y = 240,    -- 中心 y（世界坐标）
    w = 32,     -- 宽
    h = 32,     -- 高
    angle = 0,  -- 旋转角度，**单位是度**
    shape = "rect"  -- 可选：填 "ellipse" 就按椭圆判定，
                    -- 其它值或没这个字段都是矩形
}
```

- `x` / `y` 是**中心点**，不是左上角。
- `angle` 是**度**，函数内部会自己 `math.rad` 。别传弧度。
- `w` / `h` 在矩形里就是边长；在椭圆里是**两条轴的直径**（见下方警告）。
- `shape` 可选，用来说明这个形状表的种类： `"ellipse"` 表示按「内切于这个 `w × h` 方框」的椭圆判定，其它值（包括没有这个字段）都是矩形，见下文「矩形还是椭圆：SetHitboxShape」。

---

## 方法一览

!!! example "全部方法"

    | 函数 | 判定 | 备注 |
    |---|---|---|
    | `Collisions.FollowShape(sprite)` | —— | 把一张**贴图**转成形状表（带上了贴图的 `shape`） |
    | `Collisions.RectangleWithPoint(rect, point)` | 矩形 × 点 | 点用 `{x = , y = }` |
    | `Collisions.CircleWithPoint(circle, point)` | 椭圆 × 点 | 见下方警告， `w/h` 当半径用 |
    | `Collisions.RectangleWithRectangle(rect1, rect2)` | 矩形 × 矩形 | 用 SAT，支持任意旋转 |
    | `Collisions.RectangleWithCircle(rect, circle)` | 矩形 × 椭圆 | 椭圆按 `w/2` 半轴处理 |
    | `Collisions.CircleWithCircle(c1, c2)` | 椭圆 × 椭圆 | 两个正圆走快速距离判定 |
    | `Collisions.ShapeWithShape(a, b)` | **任意 × 任意** | 按两边的 `shape` 自动挑对应的判定 |
    | `Collisions.ShapeWithPoint(shape, point)` | **任意 × 点** | 同上，顺手修正 `CircleWithPoint` 的单位 |
    | `Collisions.ShapeName(name)` | —— | `"circle"` → `"ellipse"` ， `"box"` → `"rect"` ，认不出返回 `nil` |
    | `Collisions.IsEllipse(shape)` | —— | 这个形状表是不是写着 `"ellipse"` |

    除最后两个外全部返回 `true` / `false` ，**不做任何位移**。

!!! danger "CircleWithPoint 的 w/h 单位和其它函数不一致"
    `CircleWithPoint` 内部是 `local a, b = circ.w, circ.h` 然后判 `X²/a² + Y²/b² ≤ 1` ，
    也就是把 `w/h` 当成**半径（半轴）**。
    而 `CircleWithCircle` 和 `RectangleWithCircle` 都是 `w/2` ，当成**直径**。

    同一个 `{w = 16, h = 16}` 的形状：

    | 函数 | 实际覆盖范围 |
    |---|---|
    | `CircleWithPoint` | 32 × 32 |
    | `CircleWithCircle` / `RectangleWithCircle` | 16 × 16 |

    要绕开就给 `CircleWithPoint` 传**已经除过 2** 的值：

    ```lua
    local c = {x = px, y = py, w = 8, h = 8, angle = 0}   -- 想要半径 8
    Collisions.CircleWithPoint(c, {x = mx, y = my})
    ```

---

## 结合贴图：FollowShape

手写形状表很麻烦，引擎里真正的用法是**直接把贴图丢进去**：

```lua
local shape = Collisions.FollowShape(mySprite)
-- -> {x, y, w, h, angle, shape}
```

它会读取贴图的这几个字段：

| 贴图字段 | 参与计算的方式 |
|---|---|
| `x` / `y` | 世界坐标（**不经过摄像机变换**，和绘制时的平移保持一致） |
| `width` / `height` | 图片原始尺寸 |
| `xscale` / `yscale` | 缩放倍率， `w = width * xscale` |
| `rotation` | 角度（度） |
| `xpivot_px` / `ypivot_px` | 像素锚点，**非 0 时优先** |
| `xpivot` / `ypivot` | 比例锚点，默认 `0.5` （中心） |
| `_hitbox_shape` | 原样写进 `shape` ： `"ellipse"` 表示按椭圆判定，默认 `"rect"` |

内部逻辑（简化）：

```lua
-- 1. 锚点到图片中心的偏移，按缩放后的世界单位算
local dx = (width * 0.5 - ox) * xscale
local dy = (height * 0.5 - oy) * yscale

-- 2. 把这个偏移按贴图旋转角转到世界方向（局部 → 世界）
data_tab = {
    x = x + dx * cosA - dy * sinA,
    y = y + dx * sinA + dy * cosA,
    w = math.abs(w),
    h = math.abs(h),
    angle = angle,
    shape = sprite._hitbox_shape or "rect"
}
```

!!! warning "`Scale()` 是倍率不是像素"
    `spr:Scale(2, 2)` 把图片放大到 2 倍， `w` 变成 `width * 2` 。
    只有 `px.png` 这种 1×1 纯白图， `Scale(155, 130)` 的数值才刚好等于 155×130 像素
    （战斗框就是这么画的）。换成普通贴图别把 `Scale` 的参数当像素看。

!!! warning "负缩放会被取绝对值"
    `w` / `h` 都过了 `math.abs` 。横向翻转（ `xscale = -1` ）的贴图，
    碰撞盒尺寸不变。若用负缩放表达"变小"，碰撞盒不会跟着变。

---

## 引擎里的真实例子：子弹打灵魂

`Scripts/Libraries/Battle/Player/init.lua` 的 `Player.Update` 每帧对所有子弹做一次判定：

```lua
for _, b in ipairs(Sprites.images) do
    if (b.isBullet) then
        local coll_b = Collisions.FollowShape(b)
        -- 灵魂自己的盒子：贴图的图形矩形，若设了 `_hitbox` 就收缩成那个尺寸
        local coll_p = Sprites.GetHitbox(Player.sprite)

        -- 两个形状表都自带种类，标了 "ellipse" 的子弹按椭圆判，普通的按矩形判
        if (Collisions.ShapeWithShape(coll_b, coll_p)) then
            -- 粗判命中。任一方开了完美像素（SetPPCollision(true)）时，
            -- 真正的答案来自矩形化后的形状；nil 表示两边都没开，就用矩形结果。
            local pp = Sprites.PPCollide(b, Player.sprite)
            if (pp == nil or pp == true) then
                Battle.OnHit(b)
                break
            end
        end
    end
end
```

这段代码包含以下五点：

1. **遍历 `Sprites.images` 并用 `isBullet` 过滤**：这是引擎标记子弹的约定字段，骨头、炮火、追踪炮创建时都会打上它。
2. **用 `Sprites.GetHitbox(sprite)` 代替手改 `w/h`**：它把贴图的图形矩形收成 `_hitbox`（默认 `{4, 4}`）。贴图可能有 32×32 的发光边缘，但判定只用中心 4×4，因此灵魂判定远小于图片。
3. **`FollowShape` 只负责算 `x/y/angle`**：锚点与旋转都在其中处理，尺寸交给 `GetHitbox`。
4. **`PPCollide` 是第二道复核**：矩形判中之后才需要做像素级复核，顺序不能反，否则会把大量不可能命中的子弹也送进像素算法。
5. **用 `ShapeWithShape` 而不是写死 `RectangleWithRectangle`**：它会读两边自带的 `shape`
   字段，所以标了 `"ellipse"` 的圆形子弹在这里自动按圆判定，不需要改循环（见下文）。

### 改灵魂判定盒

```lua
Player.SetHitBox(width, height)           -- 改主灵魂
Player.SetHitBox(width, height, soulObj)  -- 改某个灵魂对象
```

默认是 `{4, 4}` 。

!!! warning "SetHitBox 会把 0 和负数改成 1"
    源码是 `local w = (width > 0 and width or 1)` ，传入 `0` 会变成 `1` ，判定依然生效。
    要真正关闭判定，需自行跳过判定循环（例如临时把 `isBullet` 置为 `false`）。

---

## 矩形还是椭圆：SetHitboxShape

圆形子弹按矩形判定时，会在自己那个方框的四个空角上产生命中：美术离得还远，玩家已经掉血。
此前唯一的解法是开**完美像素碰撞**，但它要付一次矩形化的开销（还要每帧比一串小方框），
用来表达"它是圆的"这件事代价过高。

`SetHitboxShape` 介于两者之间：贴图仍然只有一个盒子，但这个盒子按**内切椭圆**去判定。

```lua
bullet:SetHitboxShape("ellipse")   -- 这颗子弹从此按圆判定
bullet:SetHitboxShape("circle")    -- 同一个意思（别名）
bullet:SetHitboxShape("rect")      -- 退回普通方框（默认值）
bullet:GetHitboxShape()            -- -> "ellipse" / "rect"
```

!!! example "全套接口"

    | 调用 | 说明 |
    |---|---|
    | `sprite:SetHitboxShape(kind)` | `"ellipse"` / `"rect"` （别名 `circle` / `oval` 、 `rectangle` / `box` ），返回 `ok` |
    | `sprite:GetHitboxShape()` | 当前种类，没设过就是 `"rect"` |
    | `Player.SetHitboxShape(kind, soulObj)` | 给灵魂用的同一个开关， `soulObj` 不填就是主灵魂 |
    | `Collisions.ShapeWithShape(a, b)` | 会读两边 `shape` 的重叠判定 |
    | `Collisions.ShapeWithPoint(shape, pt)` | 会读 `shape` 的点判定 |
    | `Collisions.ShapeName(name)` | 把别名归一化成 `"rect"` / `"ellipse"` ，认不出返回 `nil` |

    种类存在 `sprite._hitbox_shape` 上，并会被抄进这张贴图产出的每一个形状表
    （ `FollowShape` 、 `Sprites.GetHitbox` ），所以整条链路都认它。

```lua
-- 一颗圆形弹幕，不需要开像素判定
local orb = Sprites.CreateSprite("Bullets/orb.png", 0)
orb.isBullet = true
orb:SetHitboxShape("ellipse")
```

!!! note "椭圆是内切在同一个方框里的"
    `w` / `h` 的含义不变：32×32 的子弹变成半径 16 的圆 —— 中心一样、最远点一样，
    只是四个角没了。所以这个开关只会让判定**变小**，不会变大。想变大请改 `_hitbox` 或图片尺寸。

    方框不是正方形时自然就是椭圆（ `w = 40, h = 20` 就是 40×20 的椭圆）， `angle` 的旋转照常带过去。

!!! warning "无法识别的名称会被拒绝"
    `SetHitboxShape("elipse")`（拼错）会打印一条警告并返回 `false` ，贴图保持原来的种类。
    拼写错误不会改变子弹的判定方式。

!!! warning "完美像素的优先级比它高"
    只要**任意一边**开了完美像素，答案就由 `Sprites.PPCollide` 给出，而像素形状是矩形，
    椭圆设置根本不会被用到。真正不规则的美术（锯齿石块、细长箭头）继续用像素判定；
    椭圆只覆盖圆 / 椭圆这一类形状。

!!! tip "开销与调试方式"
    椭圆判定就是一次解析式的比较：创建时不用矩形化，每帧不用遍历矩形列表，也不占额外内存，
    开销与 `RectangleWithRectangle` （SAT）处于同一量级。

    引擎的子弹循环和 `Collisions.ShapeWithShape` 已经接好了，两边都无需额外编写代码。
    战斗里按 `F7` （或 `Battle.ToggleHitboxes(true)` ），标了椭圆的贴图会画成椭圆轮廓，
    底下仍然淡淡地留着它那个方框。

---

## 完美像素碰撞

上面那套全是**矩形与椭圆**。如果美术是一个不规则的形状（例如不规则石块、锯齿、细长的箭头），
矩形判定会产生较多误判。

引擎在 `Sprites.lua` 里内建了一套**完美像素碰撞**（Pixel-Perfect，底层库在
`Scripts/Libraries/PerfectPixel/` ），思路是：读贴图的**真实像素**，把不透明的部分
矩形化成多个小方框，再拿这些方框去互相比。

!!! example "开关与查询"
    - `sprite:SetPPCollision(enabled)` 开关这张贴图的像素级碰撞，返回 `(ok, 矩形数)` 。
        - `ok` 是否成功形成可用的矩形化结果（贴图全透明时会失败）。
        - `enabled` 传 `false` 即关闭。
    - `sprite:IsPPCollision()` 当前是否开着。
    - `Sprites.PPCollide(a, b)` 判定两个贴图。返回**三态**：

    | 返回 | 含义 |
    |---|---|
    | `nil` | **两边都没开**，调用方应该沿用矩形判定的结论 |
    | `true` | 至少一边开着，并且真实像素命中了 |
    | `false` | 至少一边开着，但真实像素**没有**命中（粗判的假阳性） |

    - `Sprites.GetPPRects(sprite)` 拿到**图片空间**的矩形化结果，即一张 `{{x, y, w, h}, ...}` 的列表（原点在贴图左上角、y 向下、没经过缩放旋转），主要是调试用。
    - `Sprites.GetPPShapes(sprite)` 拿到**世界空间**的结果，即与 `Collisions.FollowShape` 同构的 `{{x, y, w, h, angle}, ...}` ，可以直接丢进 `Collisions.RectangleWithRectangle` 。
    - `Sprites.ClearPPCache()` 清掉像素缓存的贴图。

!!! note "矩形之间是重叠的，不是拼图"
    矩形化算法追求的是"覆盖面积最大"，不是把图形切成互不相交的小块，所以相邻矩形会互相压着。
    对判定没影响（每个矩形都在图案内部，取并集就是那堆不透明像素），但**别拿矩形数量当面积估算**。

!!! tip "返回 `nil` 与 `false` 的区分"
    有了 `nil` 这一态，调用方可以写成一句：

    ```lua
    local pp = Sprites.PPCollide(bullet, player.sprite)
    if (pp == nil or pp == true) then
        Battle.OnHit(bullet)
    end
    ```

    没开像素碰撞时 `pp` 是 `nil` ，条件成立，沿用矩形结果；开了之后 `pp` 是真正的 `true` / `false` ，
    由像素判定决定。**调用方不需要在外面判断开关状态。**

!!! example "同时切换所有灵魂"
    ```lua
    Player.SetPerfectPixel(true)    -- 主灵魂 + 所有额外灵魂一起开
    Player.SetPerfectPixel(false)   -- 一起关
    ```

    `Battle` 里的判定循环已经接好了这条链路（见上一个例子），因此只需打开开关。

!!! warning "开了以后判定会变大，不是变小"
    默认的 `_hitbox` 是 `4×4` —— **远小于**一个 16×16 红心。
    开了完美像素之后，判定变成红心**真实的不透明像素**（面积大约 4 倍于 4×4）。
    判定范围比原来更紧。原版那套擦弹手感来自小判定盒，不是来自像素级判定，二者不宜混用。

!!! tip "调试用 F7"
    战斗中按 `F7` （或调 `Battle.ToggleHitboxes(true)` ）会画出判定框覆盖层；
    开了完美像素的地方画出来的是**真实像素轮廓**而不是矩形，可据此核对判定是否有误。

!!! warning "性能：像素复核的开销高于矩形判定"
    `Sprites.PPCollide` 只在**矩形粗判已经命中**之后调用才是划算的（引擎里就是这么写的）。
    不要把它当成第一道筛子去遍历几百颗弹幕。另外后端分两种：

    | 后端 | 位置 | 说明 |
    |---|---|---|
    | C | `Scripts/Libraries/PerfectPixel/cpp.dll` | 快，大约比纯 Lua 快 **10 倍** |
    | 纯 Lua | `Scripts/Libraries/PerfectPixel/pure.lua` | C 库不可用时自动降级，结果一致只是慢 |

    源码在 `Scripts/Libraries/PerfectPixel/rectangulation.cpp` ，用 `init.lua` 统一挑后端。

    两边算出的都是"重叠区域的并集"，所以只能断言"该漏的没漏、不该漏的没漏"，别去比对矩形个数。

---

## 自己写碰撞

!!! example "点击贴图（鼠标 × 矩形）"
    `Keyboard.GetMousePosition()` 返回的是**世界坐标**（已经换算过缩放和摄像机），
    和 `FollowShape` 的产物在同一套坐标里，可以直接比：

    ```lua
    local btn = Sprites.CreateSprite("button.png", 0)
    btn:MoveTo(320, 400)

    function scene.update(dt)
        local mx, my = Keyboard.GetMousePosition()
        local shape = Collisions.FollowShape(btn)
        if (Collisions.RectangleWithPoint(shape, {x = mx, y = my})) then
            btn.color = {1, 1, 0}       -- 悬停高亮
        else
            btn.color = {1, 1, 1}
        end
    end
    ```

!!! example "自定义子弹判定（椭圆 × 矩形）"
    ```lua
    -- 一颗球形弹，跟灵魂（矩形判定盒）比
    local bullet = Sprites.CreateSprite("bullet.png", 0)
    bullet.isBullet = true
    bullet:MoveTo(320, 200)

    local shape_b = Collisions.FollowShape(bullet)
    local shape_p = Sprites.GetHitbox(Player.sprite)   -- 自动收成 _hitbox（默认 4x4）

    if (Collisions.RectangleWithCircle(shape_p, shape_b)) then
        -- 想让这颗弹按真实像素判，就在粗判命中之后补一道复核
        local pp = Sprites.PPCollide(bullet, Player.sprite)
        if (pp == nil or pp == true) then
            Battle.OnHit(bullet)
        end
    end
    ```

    注意 `Sprites.GetHitbox` 返回的是一张**全新的形状表**，改它不会影响贴图本身；
    但如果想手动覆盖尺寸，直接改返回值的 `w` / `h` 即可（旧代码里的
    `shape_p.w, shape_p.h = Player.sprite._hitbox[1], ...` 现在等价于这一句）。

    每次都手动挑选对应的函数较为繁琐。给子弹设置一次 `bullet:SetHitboxShape("ellipse")` ，
    然后写 `Collisions.ShapeWithShape(shape_b, shape_p)` 即可，结果一样，
    引擎自带的子弹循环也会采用该设置。

!!! example "纯手写形状（不需要贴图）"
    触发区域、看不见的墙、伤害范围都可以不建贴图：

    ```lua
    local zone = {x = 500, y = 300, w = 120, h = 80, angle = 0}
    if (Collisions.RectangleWithPoint(zone, {x = Player.sprite.x, y = Player.sprite.y})) then
        -- 进入区域
    end
    ```

---

## 注意事项

!!! warning "只判不推"
    这个库**没有**碰撞响应。要把玩家推出框外、要沿墙滑动，都得自己写。
    战斗框那套推挤逻辑在 `Scripts/Libraries/Battle/Arenas.lua` 里，
    而且它是**自己内联实现的**，并没有调用 `Collisions` 。

!!! warning "旋转矩形必须用 RectangleWithRectangle"
    不要用 `abs(dx) < w/2 and abs(dy) < h/2` 这种 AABB 写法判断旋转过的框：框转 45° 后
    判定结果完全不对。`RectangleWithRectangle` 用的是 SAT（分离轴定理），支持任意角度。

!!! warning "Overworld 的接触判定不走这里"
    Overworld 里的"走到 NPC 旁边按 Z 说话""踩到传送点"是 Overworld 自己的
    `FindObject` / `getTouchResult` / `getInteractResult` 在做（基于 Tiled 对象层），
    与本库无关。见 **[Overworld → 交互与对话](../040_overworld/030_interact.md)** 。

!!! warning "性能：子弹多时是 O(n)，像素复核更贵"
    `Player.Update` 每帧对所有 `isBullet` 做一次 `FollowShape` + 一次 SAT。
    弹幕数量达到数百时，这是每帧数百次三角函数运算。手机上需要控制数量，或者自己做粗筛
    （先算中心距离，超过阈值直接跳过）。

    `Sprites.PPCollide` 内部先做了一次**开销较低的 AABB 排除**（ `shapeHalfExtents` ），
    开销较高的矩形化对比只在包围盒相交时才跑。顺序仍为**先粗判，再像素**，
    不要把它当第一道筛子。

    另外，如果美术只是**圆的**： `sprite:SetHitboxShape("ellipse")` 就能以接近矩形的开销
    消除大部分角落误判，开启像素判定前可先采用它。

!!! warning "椭圆和完美像素不能叠加"
    `SetHitboxShape("ellipse")` 只描述贴图贡献的**那一个**形状。只要任意一边开了完美像素，
    答案就由 `Sprites.PPCollide` 用矩形化的像素给出，椭圆会被完全忽略 —— 一张贴图二选一，
    别指望两个一起生效。

!!! warning "坐标是世界坐标，不含摄像机"
    `FollowShape` 明确**没有**走 `love.graphics.transformPoint` 。
    好处是和 `sprite.x/y` 直接可比。贴图挂在有 `Camera` 偏移的场景里时，
    绘制位置和碰撞位置是一致的（因为绘制时才应用 Camera）；
    如果自行实现了摄像机偏移，两边需要同步。
