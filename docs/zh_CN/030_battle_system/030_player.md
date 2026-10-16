---
title: 玩家与灵魂
---

本页包含两部分内容：**玩家本身**（血量、受伤、KR）与**灵魂**（决定玩家的移动方式）。

路径： `Scripts/Libraries/Battle/Player/` 。<br>
在战斗场景中以 `Player` 作为全局变量存在。

---

## 玩家

`Player` 保存了玩家的战斗数据，同时持有那颗灵魂的贴图。

!!! example "玩家属性"
    - `name` 玩家名字。
    - `lv` 等级。
    - `maxhp` / `hp` 最大血量 / 当前血量。
    - `kr` 当前 `KR` （ karma ，即持续扣血的紫色伤害）数值。
    - `canMove` 玩家此刻能不能操作灵魂。
    - `sprite` 灵魂的贴图对象。
    - `action` **灵魂模块本身**（见下一节）。
    - `soul` 当前灵魂的名字，例如 `"red"` 、 `"blue"` 。
    - `souls` 通过 `NewSoul` 额外生成的灵魂列表。
    - `platforms` 单向平台列表（ `Player.BluePlatform` 建的）。**任何灵魂都能用**，见本页末尾的「单向平台」。
    - `platform_ground` 玩家此刻是否站在某个单向平台上。
    - `hurt_time` 受伤无敌帧剩余时间。

!!! example "玩家方法"
    - `Player.SetSoul(id, args, use_sound)` 切换灵魂。
        - `id` 灵魂名字，或数字快捷方式： `1` = `"red"` 、 `2` = `"orange"` 、 `6` = `"blue"` 。
        - `args` 传给灵魂 `Init` 的额外参数。
        - `use_sound` 为 `true` 时播放 `snd_ding.wav` 。
    - `Player.NewSoul(id, args, use_sound)` 额外生成一颗**独立**的灵魂（自己的贴图、自己的状态），常用于双子灵魂之类的效果。
        - `args` 同样传给 `Init` 。
    - `Player.SetHitBox(width, height, soul)` 设置灵魂的碰撞盒，默认是 `{4, 4}` 。
        - `soul` 省略时改主灵魂，传入灵魂表时改那一颗。
        - 传 `0` 或负数会被改为 `1` 。需要关闭判定时，自行跳过判定循环。
    - `Player.SetPerfectPixel(enabled)` 把主灵魂和 `Player.souls` 里每一颗附加灵魂都切成**完美像素碰撞**（按贴图真实像素判定，而不是 `_hitbox` 方框），返回 `(是否可用, 矩形数量)` 。
        - 对 `16×16` 的心形来说，开启后判定范围**比默认的 `4×4` 更大**，与 `SetHitBox` 二选一。
    - `Player.Heal(amount, use_sound)` 回血，不会超过 `maxhp` 。
    - `Player.Hurt(amount, time, use_sound)` 扣血。
        - `amount` 扣多少（传负数即为回血）。
        - `time` 无敌帧长度，默认 `60` ，这段时间灵魂会闪烁且不再判定碰撞。
    - `Player.AddKR(kramount)` 增加 `KR` 。只有开了 `KR` 才生效，且不会直接把血扣到 `0` 以下。
    - `Player.AddParticle()` 在当前位置生成一个灵魂残影。
    - `Player.Update(dt)` 引擎每帧调用，一般不需要手动调。

!!! warning "血量归零会直接切场景"
    `Player.Update` 里写死了： `hp + kr <= 0` 时立刻 `Scenes.switchTo("scene_gameover")` 。<br>
    需要实现锁血不死的剧情战时，自行管理 `hp` ，或在 `OnHit` 回调中拦截伤害。

![BA-03](../img/030_battle_system/ba_03_souls.png)

---

## 灵魂

**灵魂是一个 Lua 模块**，其中至少包含一个 `Update(dt)` 。

灵魂路径： `Game/Souls/` （Game 区，优先）、 `Scripts/Libraries/Battle/Player/Souls/` （引擎默认，兜底）。

!!! danger "`Player.action` 就是灵魂模块本身"
    `SetSoul` **不会**把灵魂模块复制一份，而是直接把模块表挂到 `Player.action` 上。<br>
    这意味着灵魂里写的所有 `self.xxx` 都留在模块表里。引擎在每次加载灵魂时都会**重新执行一遍文件**，以避免上一场战斗的状态被带入下一场。**因此不要在灵魂中缓存只需初始化一次的数据**，每次 `Update` 均按新一局的初始状态编写。

### 灵魂模板

```lua
local action = {
    sprite = nil,
    can_move = true,
    is_moving = false,
    -- use_platforms = true,   -- 可选：被 Player.BluePlatform 的单向平台接住
}

-- Default vars.
local speed = 2

-- 每次换到这颗灵魂时调用一次：绑定贴图、上色、把状态复位。
function action.Init(sprite, can_move, args)
    action.sprite = sprite
    if (can_move ~= nil) then
        action.can_move = (can_move ~= false)
    end
    if (sprite) then
        sprite.color = {1, 0, 0}   -- 不要上色就删掉这行
    end

    speed = 2                       -- 自己的计数器 / 开关也在这里复位
    return action
end

function action.Update(dt)
    if (not action.sprite) then return end
    -- TODO: 你的移动逻辑
end

return action
```

!!! example "灵魂可用字段"
    - `sprite` 引擎在 `Init` 里交给灵魂的玩家贴图。
    - `can_move` 切换灵魂那一刻由引擎从 `Player.canMove` **拷进来一份**，为 `false` 时不应移动。注意该字段不会逐帧回写。运行中修改 `Player.canMove` 时，由引擎在 `Player.Update` 中屏蔽移动，无需同步此字段。
    - `is_moving` 自己维护，用来判断是否要播移动动画。
    - `use_platforms` **可选字段，默认不写**。写成 `true` 才会被 `Player.BluePlatform` 的单向平台接住；不写就是直接穿过去。详见本页末尾的「单向平台」。

!!! note "初始化写在灵魂里（引擎不再代劳）"
    `SetSoul` 只做三件事：解析名字、调用 `Init(sprite, can_move, args)` 、把名字记进 `Player.soul` 。<br>
    贴图颜色、开局速度、朝向全部由灵魂自己在 `Init` 里决定，修改这些只需改动灵魂文件，无需修改引擎。<br>
    没有 `Init` 的旧灵魂仍可运行：引擎会自行写入 `sprite` / `can_move` ，并在控制台输出一条提示。

编写自定义灵魂时，读取输入统一使用 `Controller.GetState("left")` 系列函数，不使用 `Keyboard` ，以便支持手柄输入。

---

## 引擎自带的四种灵魂

这四颗灵魂都在各自的 `Init` 里给贴图上色（红 `{1, 0, 0}` 、橙 `{1, 0.5, 0}` 、蓝 `{0, 0, 1}` 、黄 `{1, 1, 0}` ），修改颜色时改动灵魂文件即可。

### 红色 `red`

八向自由移动。按住 `cancel` 时速度减半（对应原版的慢走）。

```lua
Player.SetSoul(1)   -- 或 "red"
```

### 橙色 `orange`

同样是八向移动，但**只能沿八个方向走**（斜向也只能是 45°），并且移动时会在身后留下一串残影。

```lua
Player.SetSoul(2)   -- 或 "orange"
```

### 蓝色 `blue`

带重力的灵魂，会往下掉、能跳。引擎自带的灵魂里**只有它**写了 `use_platforms = true` ，所以只有它默认能踩单向平台——别的灵魂在字段里加上这一行也能踩。

```lua
Player.SetSoul(6)   -- 或 "blue"
```

!!! example "蓝色灵魂方法"
    这些方法挂在灵魂模块上，而 `Player.action` **就是**灵魂模块本身，所以调用时一律**点号**、不传 `self` ：

    ```lua
    Player.action.SlamAuto(0, 1, 10)
    ```

    写成 `Player.action:SlamAuto(...)` 会直接报错。

    - `Angle(angle)` 只旋转贴图，**不改变**重力方向。
    - `AngleDir(direction, angle)` 同时设置重力方向与贴图角度。
    - `AngleAuto(angle)` 设置贴图角度，重力方向由角度自动推导（ `0` = 下、 `90` = 左、 `180` = 上、 `270` = 右）。
    - `Slam(angle, hp, inv)` 朝当前重力方向猛砸。落地时按 `hp` / `inv` 调用 `Player.Hurt` 。
    - `SlamDir(direction, angle, hp, inv)` 指定重力方向再砸。
    - `SlamAuto(angle, hp, inv)` 由角度推导重力方向再砸。
    - `GetDirection()` 返回当前重力方向。
    - `SetDirection(direction)` 只改重力方向，不动贴图角度。
    - `GetSpeed()` 返回当前竖直速度（正数 = 下落）。
    - `SetSpeed(value)` 直接改竖直速度。
    - `SetCanJump(value)` 锁住 / 解锁跳跃。
    - `SetJumping(value)` 强制进入或退出跳跃状态。
    - `Land()` 着陆：速度归零并恢复跳跃能力。
    - `Reset()` 把所有状态恢复默认。
    - `Init(sprite, can_move, args)` 换到这颗灵魂时由引擎调用：上蓝色、贴图转回 `0` 、然后 `Reset()` 。
    - `Update(dt)` 引擎每帧调用。

`Slam` 系列三个函数的 `hp` / `inv` 用于砸地自伤：砸地需要产生代价时填入数值，否则填 `0` 或省略。

### 黄色 `yellow`

同样是八向移动，但按 `confirm` 会打出**心形子弹**。子弹受轻微重力影响，飞行过程中逐渐变大，出屏或与其他子弹碰撞后消失。需要接住子弹时，为目标子弹添加 `HitCall` 函数。

```lua
Player.SetSoul("yellow")   -- 没有数字快捷方式，只能写名字
```

- 射击冷却 5 帧，声音是 `snd_shoot.wav` 。
- 子弹图片是 `Soul Library Sprites/spr_heartbullet_1.png` 。
- 按住 `cancel` 一样会把移动速度减半。

!!! note "蓄力演出已实现，大子弹尚未实现"
    按住 `confirm` 会开始蓄力（总时长 `60` 帧），分两段演出：

    1. 蓄到 1/3 时，四颗小圆点从四周**螺旋收拢**到灵魂上；
    2. 蓄满时，灵魂上再叠一层**半透明、会脉动的黄色影子**（表示充能完成，每帧跟随灵魂）。

    任何一次**松手**都会把蓄力清零，上面两层特效自行淡出，半路松手不会残留特效。

    但**松手不会打出大子弹**：该弹幕尚未实现，此段目前只有可见的演出效果。

    需要主动清除屏幕上残留的蓄力特效时（例如波次切换），调用：

    ```lua
    Player.action.ClearBigshot()
    ```

    它只清特效、不动蓄力计数。换灵魂时 `Init` 里已经自动清过一次了。

---

## 单向平台

一套**只从上方接住玩家**的平台：玩家可以从下方跳穿，也不会在位于平台下方时被吸附上去。

平台本身**和灵魂无关**，`Player.BluePlatform` 这个函数名是历史遗留（当初只为蓝色灵魂写的）。

!!! example "平台方法"
    - `Player.BluePlatform(x, y, width, args)` 创建一块平台，返回平台对象。
        - `x` / `y` 中心坐标，默认 `320, 320` 。
        - `width` 宽度（像素），默认 `50` 。
        - `args` 可选设置表：
            - `mode` `"none"` （静止）或 `"move"` （平台横移时带着玩家一起走），默认 `"none"` 。
            - `speed` `{x = n, y = n}` 每帧位移。**只要填了就生效，与 `mode` 无关**。 `mode` 不再控制平台是否移动。
            - `rotation` 平台角度，默认 `0` 。
            - `color` 平台颜色，默认 `{1, 0.3, 1}` 。
            - `layer` 所在图层，默认 `"BelowBullets"` 。
            - `active` 是否参与碰撞，默认 `true` 。
            - `surface_offset` 判定面相对顶边的额外偏移，默认 `0` 。
            - `surface_tolerance` 判定带的半厚度，默认 `2` 。
            - `line_color` / `line_alpha` 顶部高光线的颜色与透明度。
    - `Player.ClearPlatforms()` 销毁所有平台。

!!! example "平台对象方法"
    - `MoveTo(x, y)` 移动平台（高光线会自动跟上）。
    - `SetRotation(angle)` 设置角度。
    - `SetWidth(w)` 设置宽度。
    - `Sync()` 手动同步高光线，一般不用调。
    - `SetStencils(stencils)` 给平台贴图**和高光线**一起套遮罩，一般写 `platform:SetStencils({Arena.mask})` 。
    - `Step` 约定字段，不是内置函数：写 `platform.Step = function (self) ... end` ， `Player.UpdatePlatforms(dt)` 每帧会调它一次——在平台移动并 `Sync()` 之后、落地判定之前。**不传 `dt`**。详见 [基础开发 → Step 钩子](../../020_basic/170_step.md) 。
    - `Destroy()` / `Delete()` 销毁这块平台。

??? example "一块会左右移动的平台"
    ```lua
    local p = Player.BluePlatform(320, 350, 60, {
        mode  = "move",
        speed = {x = 2, y = 0},
        color = {1, 1, 0.3}
    })

    -- 也可以在波次的 Update 里自己推
    function wave.Update(dt)
        p.image.x = 320 + 40 * math.sin(math.rad(Battle.TIME_F))
    end
    ```

!!! tip "灵魂需声明 `use_platforms` 才会被平台接住"
    平台是**自愿加入**的：灵魂表里写了 `use_platforms = true` 才会被接住，**不写就直接穿过去**。

    ```lua
    local action = {
        sprite = nil,
        can_move = true,
        use_platforms = true,   -- <- 加这一行，Player.BluePlatform 就会接住它
    }
    ```

    - 引擎自带的灵魂里，目前**只有蓝色**写了这个字段，因此默认行为未变：切换为红、橙、黄灵魂时会穿过平台下落。
    - 字段**只在缺失时**才回退到旧的判断（ `Player.soul == "blue"` ），因此未添加该字段的 `Game/Souls/blue.lua` 仍可踩平台，无需修改。
    - 判定本身（ `Player.BluePlatformCollide(sprite, 垂直速度)` ）只看贴图和竖直速度，**与灵魂无关**。<br>
      `Player.NewSoul` 生成的附加灵魂不会被引擎自动判定，需要让其踩平台时，在其自身的 `Update` 中调用一次：

    ```lua
    Player.BluePlatformCollide(soul.sprite, soul.GetSpeed())
    ```

---

## 受伤判定

碰撞不是灵魂自己算的，而是 `Player.Update` 统一做的：

1. 处于无敌帧（ `hurt_time > 0` ）时，直接跳过所有碰撞。
2. 否则遍历所有带 `isBullet` 的贴图，先用 `Sprites.GetHitbox` 取灵魂的判定盒（内含 `_hitbox` 覆盖），再用 `Collisions.ShapeWithShape` 做粗判 —— 正常是矩形 × 矩形，某一方标了 `SetHitboxShape("ellipse")` 就按椭圆判。
3. 粗判命中后，再用 `Sprites.PPCollide(bullet, Player.sprite)` 做一次精细判定：
    - 返回 `true` / `false` 就以此为准（说明弹幕或灵魂**任意一方**开了完美像素）；
    - 返回 `nil` 表示两边都没开，沿用第 2 步的矩形结论。
4. 最终判定为命中则调用 `Battle.OnHit(bullet)` —— **该回调在场景文件中自行实现**，详见 [战斗场景与回调](./070_scene.md) 。

!!! warning "按真实像素判定的开启方式"
    ```lua
    Player.SetPerfectPixel(true)          -- 主灵魂 + 所有附加灵魂一起切
    bullet:SetPPCollision(true)           -- 或者只让某几颗弹幕走像素判定
    ```
    单张贴图级别的开关是 `sprite:SetPPCollision(enabled)` / `sprite:IsPPCollision()` ，细节见 [贴图 → 完美像素碰撞](../020_basic/020_sprites.md) 。

!!! tip "圆形弹幕：使用椭圆判定，无需像素判定"
    圆形弹幕只需消除方框的四个角，椭圆判定的开销接近矩形判定，无需做矩形化处理，也无需每帧比对多个小方框：

    ```lua
    bullet:SetHitboxShape("ellipse")   -- 这颗弹幕按圆判定
    Player.SetHitboxShape("ellipse")   -- 或者灵魂本身（传灵魂对象可指定某一个）
    ```

    椭圆内切在同一个方框里，所以只会让判定变小。详见 [进阶 → 碰撞判定](../../050_intermediate/030_collision.md) 。

!!! example "弹幕颜色"
    弹幕对象上的 `HurtMode` 字段决定了它算不算伤害，常见的取值：

    - `"normal"` 碰到就受伤。
    - `"blue"` / `"cyan"` **移动中才会**受伤，站着不动安全。
    - `"orange"` **站着不动才会**受伤，移动中安全。
    - `"safe"` 完全无害。

    该字段如何写入场景的 `OnHit` 由开发者决定，引擎只负责把它挂在贴图上传递过来。
