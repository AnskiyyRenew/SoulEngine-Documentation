---
title: 数学教程
---

本页不做数学推导，只说明**在 SoulEngine 里的写法与运行效果**。
三部分：绝对值 → 三角函数 `A·sin(ωx + φ)` → 矩阵变换（旋转框的坐标换算）。

!!! warning "单位约定：引擎里角度一律是「度」"
    贴图 `rotation` 、Arena 的 `angle` 、形状表的 `angle` —— 全是**度**。
    但 Lua 的 `math.sin` / `math.cos` 只吃**弧度**。

    所以正确的写法永远是：

    ```lua
    math.sin(math.rad(30))   -- 对
    math.sin(30)             -- 错！30 弧度 ≈ 1718 度
    ```

    反方向用 `math.deg` 。 `math.atan2(dy, dx)` 返回弧度，要转回度再写进 `rotation` 。

---

## 绝对值

`math.abs(x)` 把负数翻正。它对应的三类用法如下。

### 距离

两个坐标差 `dx` 可能为正也可能为负，距离只看大小：

```lua
local dx = a.x - b.x
if (math.abs(dx) < 4) then
    -- 横向已经很接近了
end
```

配合 `dy` 就是常见的**粗略距离判定**。注意这不是圆形判定
（真正圆形要 `dx*dx + dy*dy < r*r` ），但作为粗筛写法开销较低。

### 对称

让某个效果左右 / 上下对称，即移动方向不影响结果：

```lua
-- 灵魂离框中心越远，颜色越红（左右都一样）
local offset = math.abs(Player.sprite.x - arena.x)
Player.sprite.color = {1, 1 - offset / 200, 1 - offset / 200}
```

### 收敛

引擎中多处采用如下写法：每帧朝目标靠近固定步长（ `Arenas.lua` 顶部的**局部**函数 `smooth_value` ，没挂在 `Arenas` 表上）：

```lua
local function smooth_value(value, target, speed)
    if (value > target) then return math.max(value - speed, target) end
    if (value < target) then return math.min(value + speed, target) end
    return value
end
```

这里没写 `abs` ，但**距离本身是 `abs(target - value)`** ，
需要计算"还要几帧到位"就得算它。 `Arenas.lua` 的 `ResizeWithTime` 就是这么反推速度的：

```lua
local dw = math.abs(arena.target.width - arena.width)
arena.speeds.width = math.floor(dw / timew)   -- 想在 timew 帧内走完
```

!!! example "常用搭配"

| 用途 | 写法 |
|---|---|
| 夹在范围里 | `math.max(min, math.min(v, max))` |
    | 判断是否接近 | `math.abs(a - b) < eps` |
    | 变化量大小 | `math.abs(target - current)` |
    | 负缩放也不出错 | `w = math.abs(width * xscale)` |

---

## 三角函数：`A · sin(ω·x + φ)`

### 先记住这几个值

| 角度 | `sin` | `cos` |
|---|---|---|
| 0° | 0 | 1 |
| 90° | 1 | 0 |
| 180° | 0 | -1 |
| 270° | -1 | 0 |
| 360° | 0 | 1 |

`sin` 的输出永远在 `[-1, 1]` 之间来回，一整圈 360°。
`cos` 就是 `sin` **往前挪 90°**（ `cos(x) == sin(x + 90°)` ）。

!!! warning "屏幕的 y 轴是向下的"
    数学课上 y 向上，屏幕上 y 向下。所以 `+sin` 的效果是**往下**，
    想让东西往上飘要写 `-A * sin(...)` 或者用 `-y` 方向。

### 三个参数各管什么

```
y = A * sin(ω * x + φ)
    │      │       └─ φ（相位）：从波形的哪里开始
    │      └─ ω（角速度）：来回一趟有多快
    └─ A（振幅）：摆多大
```

| 参数 | 含义 | 单位 |
|---|---|---|
| `A` | 摆动的**半宽**。 `A = 20` 就是在中心左右各 20 像素，总共 40 像素宽 | 像素（或任何指定的单位） |
| `ω` | 一圈 360°，所以**周期 `T = 360 / ω`** | 度 / 单位 x |
| `φ` | 整条波左右平移。两个物体差 φ 就是差一段**时间**出发 | 度 |

`x` 的取值由调用方决定，引擎里有两个现成的时间源：

| 变量 | 含义 | 备注 |
|---|---|---|
| `Battle.TIME_F` | 战斗开始后的**帧数**，每帧 +1 | 写法简单，但速度跟着帧率走 |
| `Battle.TIME_R` | 战斗开始后的**秒数**，每帧 +dt | 帧率无关 |

!!! example "周期与 ω 的对应关系"

    | 目标效果 | 用帧 `TIME_F` | 用秒 `TIME_R` |
    |---|---|---|
    | 1 秒一个来回（60fps） | `ω = 6` | `ω = 360` |
    | 2 秒一个来回 | `ω = 3` | `ω = 180` |
    | 半秒一个来回（快抖） | `ω = 12` | `ω = 720` |
    | 引擎 wave1 的效果 | `ω = 1` （6 秒一趟） | —— |

### 场景 1：来回巡逻

引擎自带的 `Scripts/Waves/bones/wave1.lua` 就是这么写的：

```lua
p.image.x = 320 + 20 * math.sin(math.rad(Battle.TIME_F))
```

拆开看：中心 `320` ， `A = 20` ， `ω = 1°/帧` → 周期 360 帧 ≈ 6 秒， `φ = 0` 。
骨头会在 x 从 300 到 340 之间慢慢晃。

想让它晃得快一倍、幅度大一点：

```lua
p.image.x = 320 + 60 * math.sin(math.rad(Battle.TIME_F * 3))
```

### 场景 2：上下漂浮

道具、提示箭头、"此处可交互"的光点，都用得上：

```lua
-- 在原地上下飘 ±6 像素，2 秒一趟
local t = Battle.TIME_R
arrow.y = arrow_y0 - 6 * math.sin(math.rad(t * 180))
```

!!! note "使用减号的原因"
    屏幕上 y 越大越靠下， `-sin` 对应"往上飘"。

### 场景 3：呼吸缩放

```lua
-- 尺寸在 0.95 ~ 1.05 倍之间呼吸
local s = 1 + 0.05 * math.sin(math.rad(Battle.TIME_R * 180))
heart:Scale(s, s)
```

### 场景 4：闪烁 / 无敌帧

`sin` 的值域是 `[-1, 1]` ，想变成 `[0, 1]` 的透明度，写成 `0.5 + 0.5 * sin(...)` ：

```lua
-- alpha 在 0.2 ~ 1.0 之间脉动
Player.sprite.alpha = 0.6 + 0.4 * math.sin(math.rad(Battle.TIME_F * 12))
```

想做"一闪一闪"的硬切换（不是渐变），把结果二值化：

```lua
local v = math.sin(math.rad(Battle.TIME_F * 8))
Player.sprite.alpha = (v > 0) and 1 or 0.3
```

### 场景 5：一排骨头的波浪（相位 φ）

一排 10 根骨头，每根比前一根**晚一点**出发，就形成波浪。
差别全在 `φ` 上：

```lua
for i = 1, 10 do
    local phi = i * 30                      -- 每根差 30°
    bone[i].y = 300 + 25 * math.sin(math.rad(Battle.TIME_F * 4 + phi))
end
```

`φ` 差 30°、ω 是 4°/帧，等价于"每根骨头比前一根晚 30/4 = 7.5 帧动"。

### 场景 6：绕圈 / 圆形排布

`cos` 管 x、 `sin` 管 y，两者就是圆周运动：

```lua
-- 一颗子弹绕着中心 (320, 320) 转圈，半径 90，3 秒一圈
local a = math.rad(Battle.TIME_R * 120)
bullet.x = 320 + 90 * math.cos(a)
bullet.y = 320 + 90 * math.sin(a)
```

要一圈摆 N 颗子弹（弹幕环），把 `φ` 换成"每颗差 360/N 度"：

```lua
for i = 1, 12 do
    local a = math.rad(Battle.TIME_R * 120 + (i - 1) * 30)   -- 360 / 12
    local b = Attacks.New(...)
    b.x = 320 + 90 * math.cos(a)
    b.y = 320 + 90 * math.sin(a)
end
```

### 场景 7：半周期做缓动

`sin` 从 0° 走到 180° 是 `0 → 1 → 0` 的一个完整来回。
拿它当"进度"用，就是**缓入缓出**：
两头慢、中间快，不用写 Tween。

```lua
-- t 从 0 走到 1，值从 0 升到 1 再落回 0
local t = progress            -- 0..1
local v = math.sin(math.rad(t * 180))
```

只想单向 `0 → 1` 且**开头慢结尾慢**，用 `cos` 的变形：

```lua
-- (1 - cos) / 2 ：t=0 -> 0，t=1 -> 1，两头平缓
local v = (1 - math.cos(math.rad(t * 180))) / 2
```

!!! note "与 Tween 的适用区别"
    `Tween` 适合"从 A 去 B，到了就结束"； `sin` 适合"永远在循环、随时要知道当前值"。
    波次里的持续运动都用 `sin` ，一次性演出用 `Tween` 。

### 场景 8：衰减震动

震动要"越晃越小"，做法是让 `A` 自己变小：

```lua
shake_time = 30                                  -- 震 30 帧
-- 每帧：
if (shake_time > 0) then
    local amp = shake_time / 30 * 8              -- 振幅 8 -> 0
    sprite.x = base_x + amp * math.sin(math.rad(shake_time * 30))
    shake_time = shake_time - 1
else
    sprite.x = base_x
end
```

### 注意事项

!!! warning "用帧数驱动，速度会跟着帧率变"
    `math.sin(math.rad(Battle.TIME_F * 6))` 在 60fps 下是 1 秒一趟，
    在 120fps 的高刷屏上就是 **0.5 秒一趟**。
    要帧率无关请统一用 `Battle.TIME_R * 360 / 秒数` 。

!!! warning "别忘了乘 A"
    `math.sin(...)` 的返回值在 ±1 之间，直接写进 `x` 只会动 1 像素。
    动画幅度过小时先检查这一项。

!!! warning "sin 的相位是叠加在 ω·x 里面的"
    想"晚 0.5 秒出发"，不是 `sin(ω*x) + 0.5` ，而是 `sin(ω*x + ω*0.5)` 。

---

## 矩阵变换：旋转框

本节说明旋转框的坐标换算方式。
理解它之后，`Arenas.lua` 里那一大段坐标运算即为同一套公式。

### 要解决什么问题

战斗框会转： `arena.rotation = 30` 。
转了之后，"玩家在不在框里"就没法用 `x > left and x < right` 判断了 ——
框的边不再是横平竖直的。

**思路不是去算斜着的边，而是把点"转回"框的本地坐标系。**
在框自己的坐标系里，它就是一个规规矩矩、没转过的矩形：

```
     世界坐标（框转了 30°）          局部坐标（框没转）
        ／￣￣￣￣＼                    ┌────────┐
       ／    ·P    ＼        ==>        │   ·P    │
       ＼          ／                   │         │
        ＼＿＿＿＿／                    └────────┘
     四条边都是斜的                  四条边横平竖直，直接比
```

### 两个公式

设框中心 `(cx, cy)` ，旋转角 `θ` ， `cos = cos(θ)` ， `sin = sin(θ)` 。

**世界 → 局部**（判断"点在不在这个斜框里"用这个）：

```lua
local dx, dy = px - cx, py - cy
local lx = dx * cos + dy * sin      -- 局部 x
local ly = dy * cos - dx * sin      -- 局部 y
-- 之后就当框没转过：
local inside = (lx >= -w/2 and lx <= w/2 and ly >= -h/2 and ly <= h/2)
```

**局部 → 世界**（知道框上的某个位置，算它在屏幕哪里用这个）：

```lua
local wx = cx + lx * cos - ly * sin
local wy = cy + lx * sin + ly * cos
```

!!! tip "记法"
    局部 → 世界是标准的旋转矩阵：

    ```
    [ wx ]   [ cos  -sin ] [ lx ]
    [ wy ] = [ sin   cos ] [ ly ]
    ```

    世界 → 局部就是它的**逆矩阵**，而旋转矩阵的逆 = 转置（把 sin 的符号换掉）：

    ```
    [ lx ]   [  cos  sin ] [ dx ]
    [ ly ] = [ -sin  cos ] [ dy ]
    ```

    所以两个公式长得几乎一样，只是 `sin` 的符号换了。这就是"矩阵变换"在这套代码里的全部内容。

### 一个算得出来的例子

框在 `(320, 320)` ，宽 155，转了 30°。问它的**右边框中点**在屏幕哪里？

- 局部坐标： `(77.5, 0)` （宽的一半，横向）
- `cos30 ≈ 0.866` ， `sin30 = 0.5`

```lua
wx = 320 + 77.5 * 0.866 - 0 * 0.5 = 387.1
wy = 320 + 77.5 * 0.5   + 0 * 0.866 = 358.75
```

右边框中点跑到了 `(387, 359)` —— 往右**也往下**，
这就是 30° 顺时针旋转该有的样子。

---

### 引擎中的五处实现

同一套矩阵，在引擎里出现了五次：

??? example "① 判断点能不能站人 —— `Arenas.lua` 的 `is_point_valid`"
    ```lua
    local dx, dy = px - a.x, py - a.y
    local cos, sin = math.cos(math.rad(a.rotation)), math.sin(math.rad(a.rotation))
    local lx = dx * cos + dy * sin
    local ly = dy * cos - dx * sin

    -- 之后就是普通的矩形比较（还往里缩了 8 像素，因为灵魂是 16×16）
    if (lx >= -w / 2 + 8 and lx <= w / 2 - 8 and ly >= -h / 2 + 8 and ly <= h / 2 - 8) then
        in_plus = true
    end
    ```

    注意它是个**文件级局部函数**（ `local function is_point_valid` ），没挂在 `Arenas` 表上，
    也没导出成全局——所以外部拿不到它，只能通过 `Arenas` 的公开行为间接受它影响。

??? example "② 把玩家推出 minus 框 —— 局部算完再转回世界"
    `Arenas.lua` 里它是**内联展开**的，没有单独的函数名，但每一句都是那两条公式：

    ```lua
    -- 世界 → 局部：lx = dx·cos + dy·sin ，ly = dy·cos − dx·sin
    while ((p.x - arena.x) * math.cos(math.rad(arena.rotation))
         + (p.y - arena.y) * math.sin(math.rad(arena.rotation)) < -w / 2 + 8) do
        ...
    end

    -- 循环结束后再转回世界
    p.x = arena.x + lx * cos - ly * sin
    p.y = arena.y + lx * sin + ly * cos
    ```

    这一段的 `cos` / `sin` 每次循环都重新算一遍，因为 `arena.rotation` 可能在途中被改。

??? example "③ 取框上的某个点 —— `GetCornerPos` / `GetCenterPos`"
    两个方法用的都是"先把局部偏移算出来、再转到世界"：

    ```lua
    -- GetCornerPos：角点的局部坐标就是一个 (±corner_x, ±corner_y)，再转出去
    res[1] = arena.x + corner_x * cos - corner_y * sin
    res[2] = arena.y + corner_x * sin + corner_y * cos
    ```

    `GetCenterPos(side)` 的写法不同（写成 `arena.x + length * sin` / `arena.y - length * cos` 这种交叉形式），
    但那是同一个矩阵换个写法—— `side == "up"` 取的就是"转过的框的上边中点"：
    `Arena:GetCenterPos("up")` 能正确跟随旋转，原因就在这里。

??? example "④ 贴图转形状 —— `Collisions.FollowShape`"
    ```lua
    -- 锚点相对图片中心的偏移（dx, dy），按贴图旋转角转到世界
    x = x + dx * cosA - dy * sinA
    y = y + dx * sinA + dy * cosA
    ```

    碰撞库用的也是同一个矩阵，见 **[碰撞库](./030_collision.md)** 。
    完美像素碰撞那套（ `Sprites.GetPPShapes` ）内部的 `imageRectsToWorld` 也采用完全相同的公式，
    所以两条判定路径描述的一定是同一个盒子。

??? example "⑤ 3D 骨头也是它 —— `Attacks/Bones.lua` 的 `_rotateZ`"
    ```lua
    return {
        center[1] + x * cos_a - y * sin_a,
        center[2] + x * sin_a + y * cos_a,
        point[3]
    }
    ```

    `_rotateX` / `_rotateY` / `_rotateZ` 三个函数，本质都是**同一个 2×2 矩阵**，
    只是作用在 (y,z)、(x,z)、(x,y) 三对不同的轴上。

---

### 灵魂转了之后：探针

蓝色灵魂会"倒过来"（重力朝上），实现上是把 `Player.sprite.rotation` 设成 180。
那么"脚下"就不在屏幕下方了，而在**局部**的下方。

`Arenas.PlayerOnGround` 是这么写的：

```lua
local psin, pcos = math.sin(math.rad(player.rotation)), math.cos(math.rad(player.rotation))
return side_touching(player, -psin * 10, pcos * 10)
```

探针偏移 `(-sin θ, cos θ) * 10` 就是"局部向下"方向在世界里的样子：

| 灵魂 rotation | 探针方向 | 屏幕上 |
|---|---|---|
| 0 | `(0, 10)` | 脚下 ↓ |
| 90 | `(-10, 0)` | 左边 ← |
| 180 | `(0, -10)` | 头顶 ↑ |
| 270 | `(10, 0)` | 右边 → |

**一次矩阵变换即可覆盖四种重力方向。**

!!! warning "`PlayerOnCeiling` 是 x、y **两个分量都反号**"
    不是只把 x 反过来：

    ```lua
    -- PlayerOnGround
    return side_touching(player, -psin * 10,  pcos * 10)
    -- PlayerOnCeiling
    return side_touching(player,  psin * 10, -pcos * 10)
    ```

    两个分量各翻一次符号，因为那是 **180°** 的反方向，不是镜像。
    只改一个分量得到的是"侧面"，探针会指向左右，判断自然全错。

### 变换的顺序

正确的顺序永远是 **缩放 → 旋转 → 平移**：

1. 先按局部尺寸（ `w/2` 、 `h/2` ）取点 —— 缩放已经在 `w/h` 里了
2. 再乘旋转矩阵
3. **最后**加中心坐标 `cx, cy`

!!! warning "先平移再旋转会把框甩飞"
    写成 `x = (px + dx) * cos - ...` 是错的。
    平移一定在最后一步。

---

### 注意事项

!!! warning "角度用错单位"
    框的 `rotation` 是度，矩阵里要的是弧度。忘写 `math.rad` 时框会持续旋转，
    因为 30 弧度 ≈ 1718 度。

!!! warning "正角度在屏幕上是顺时针"
    因为 y 轴向下。 `rotation = 90` 不是"逆时针转 90°"，
    视觉上是顺时针 90°。和 LÖVE 的 `love.graphics.rotate` 一致。

!!! warning "旋转过的矩形不能再用 AABB"
    `abs(dx) < w/2 and abs(dy) < h/2` 只对没转过的框成立。
    要么走上面那套局部坐标，要么用 `Collisions.RectangleWithRectangle` （内部是 SAT）。

!!! warning "Arenas 的 speeds 没有乘 dt"
    ```lua
    arena.rotation = smooth_value(arena.rotation, arena.target.rotation, arena.speeds.rotation)
    ```

    这里的 `speeds.rotation = 15` 是**每帧 15 度**，不是每秒。
    120Hz 的机器上旋转会快一倍。要做帧率无关的旋转，自己在外面按 `dt` 调 `speeds` 。

!!! warning "缩放只吃 xscale/yscale"
    `FollowShape` 里的 `w = width * xscale` 只看贴图自己的缩放字段，
    不看父级、不看图层缩放。挂在父节点下的贴图要自己把父级倍率乘进去。
