---
title: 战斗初始化
---

---

## 战斗场景

战斗场景图层的初始化方式近期发生变更：原先部分场景各自持有图层，现统一放置在 `init.lua` 下。

以下为全部图层的初始化代码。该配置非强制，可按需调整：

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



---

## 遭遇文件

本文件包含本地化操作，详见 **[本地化](../080_l10n/index.md)** 专题。

此部分称为 `遭遇战` 更为准确。<br>
**此文件的主要目的为：率先初始化战斗场景，使战斗场景从标准化变为定制版本。**

该文件定义以下内容：玩家数据（进入战斗时）、敌人数据（个数、血量、行动等）、物品背包以及其他杂项。<br>
以下为标准模板，内容较长，默认折叠：

??? tip "标准游戏模板"

    ```lua
    local encounter = {
        narration = Localize.localizeText("Battle.Narration.Default"),
        can_flee = true,
        flee_percent = 0.75,
        enemy_id = 1,
        enemies = {
            {
                id = "Poseur",
                name = Localize.localizeText("Battle.EnemiesName.Poseur"),
                animation = require("Game.Animations.Poseur"),

                maxdamage = 400,
                dmg_float = 2,  -- Some random stuff......I hate them

                show_hpbar = true, -- Sans... stop hiding your hp bar.
                maxhp = 100,
                hp = 100,
                gold = 1,
                exp = 1,

                defensetext = "MISS",
                misstext = "MISS",

                canspare = true,
                killable = true,

                position = {320, 140},
                actions = {
                    {id = "Check", name = Localize.localizeText("Battle.Actions.Names.Check")},
                    {id = "Pose",  name = Localize.localizeText("Battle.Actions.Names.Pose")},
                }
            },
        },

        state = "DEFENDING",
        wave = "bones.wave1",

        player = {
            name = "end",
            lv = 20,
            maxhp = 99,
            hp = 99
        },

        items = {
            {id = "CHOCOLATE", _color = {0.4, 1, 1}, name = "Chocolate"},
            {id = "END", _color = {0.4, 0, 1}, name = "END", _cantdestroy = true},
        }
    }

    -- Assign internal _id to each statically-defined enemy
    for i = 1, #encounter.enemies
    do
        local e = encounter.enemies[i]
        e._id = encounter.enemy_id
        encounter.enemy_id = encounter.enemy_id + 1
    end

    -- The following methods are now provided by Battle.game_apis via metatable:
    --   encounter:AddEnemy(data)  — adds a validated enemy with auto-assigned _id
    --   encounter:AddItem(item)    — adds a validated item
    --   encounter:ForceAttack(id)   — makes the enemy whose string `id` matches
    --                                 enter one attack cycle (Battle.attack.Restart)

    return encounter
    ```

通过一个 `encounter` 表来定义游戏主体，下面介绍 `encounter` 表所拥有的属性和方法：

!!! example "遭遇表属性"
    - `narration` 玩家回合时战斗框内打出的旁白文本，目前这里使用了 `本地化` 操作获取文本，可以直接写中文或英文，支持直接显示。
    - `can_flee` 是否在 `仁慈` 按钮中显示 `逃跑` 选项，Boss 战中可关闭。
    - `flee_percent` 逃跑概率， `can_flee` 为 `false` 时该项无作用。
    - `enemy_id` 在添加新敌人时，此项会加一，用于为每个敌人分配新的唯一 id。
    - `state` 刚进入战斗的状态，详见后续章节。可选 `ACTIONSELECT` （玩家回合）或 `DEFENDING` （直接进入敌人回合，开场即进入防御）。
    - `wave` 刚进入战斗的回合，可搭配 `DEFENDING` 状态使用。加载顺序见下方 `回合脚本` 。
    - `enemies` 敌人表，用来存储所有敌人的数据。
        - `id` 这是检测使用的id，一般使用英文，只要没有冲突即可，因为这部分不会被汉化。
        - `name` **这部分是真正显示的名字** ，会被汉化。
        - `animation` 此敌人使用什么动画。
        - `maxdamage` 可以对敌人造成的最大伤害，接入 `Overworld` 后可用公式计算最大伤害。
        - `dmg_float` 造成的伤害会在当前伤害基础上随机加 `0 ~ dmg_float` ，默认是 `2` 。
        - `show_hpbar` 是否显示血条。原版 UNDERTALE 中 `Sans` 为特例，攻击时同样不显示血条。
        - `maxhp` 敌人的最大血量。
        - `hp` 敌人的当前血量。
        - `gold` 敌人所携带的金钱，杀死或饶恕后可获得。
        - `exp` 敌人所携带的经验值，仅杀死后可获得。
        - `defensetext` 击打敌人但不造成伤害时会弹出的文本。
        - `misstext` 未击打敌人错过输入窗口时会弹出的文本。
        - `canspare` 敌人是否可饶恕，会进行自动黄名。
        - `killable` 敌人是否可被杀，若为 `false` ，即便敌人血条已经空了，仍然不会死亡，可用于播放额外的处决动画。
        - `position` 敌人在什么地方站着，并不是敌人自己的动画，而是处理受击动画的坐标定位，届时玩家将朝着这个地方砍。
        - `actions` 行动表，可以对敌人做出什么行为。
            - `id` 行动的id，也是不会被汉化的。
            - `name` 行动的名字，这部分也是真实显示在屏幕上的。
    - `player` 玩家数据。
        - `name` 玩家的名字。
        - `lv` 玩家的等级。
        - `maxhp` 玩家的最大血量。
        - `hp` 玩家的当前血量。
    - `items` 背包。
        - `id` 每个物品的检测 id，不会被汉化。
        - `name` 每个物品真实显示的名字。
        - `_cantdestroy` （可选）若为 `true` 则使用的时候不会被删除。

除了上面的属性， `encounter` 表还通过元表挂载了一批方法（来自 `Scripts/Libraries/Battle/game_apis.lua` ），可以用冒号语法直接调用：

!!! example "遭遇表方法"
    - `AddEnemy(data)` 添加一个敌人。会自动补齐缺失字段并分配一个唯一的 `_id` ，返回补全后的敌人表。
        - `data` 敌人数据表，字段与上面 `enemies` 中列出的完全一致。
    - `AddItem(item)` 添加一个物品。会自动校验物品格式，返回补全后的物品表。
        - `item` 物品数据表。
            - `id` 物品的检测 id，不会被汉化。缺失或不合法时会替换为 `STONE` 。
            - `name` 物品真实显示的名字。缺失或不合法时会替换为 `Stone` 。
            - `_color` （可选）物品的颜色，由三个 `0 ~ 1` 的数字组成。
            - `_cantdestroy` （可选）若为 `true` 则使用的时候不会被删除。
    - `InitAnimation(index, pos)` 初始化第 `index` 个敌人的动画，并返回这个动画实例。
        - `index` 敌人在 `enemies` 表中的序号。
        - `pos` 动画的位置。
        - 返回值：该敌人的动画实例。之后所有操作都写在它身上（ `anim.SetFace(3)` ）；
          重复调用不会重建，而是返回同一个实例。
    - `ForceAttack(id)` 让指定敌人进入一次攻击结算流程（内部调 `Battle.attack.Restart` ）。
        - `id` 敌人的**字符串** `id` （即 `enemy_id` 对应的字符串，不是 `_id` 数字）。
        - 注意：该函数仅按 `id` 匹配敌人，未匹配到时打印一条
          `[Battle - forceAttack] WARNING: No enemy found with id = ...` 并不执行任何操作；
          该警告在匹配成功时同样会输出，以敌人是否实际执行动作为准。

!!! tip "属性与方法的区别"
    属性是**数据**，在表里写死；方法是**操作**，用来往表里追加或改动数据。<br>
    两者的区别在于：属性用点号读取（ `encounter.wave` ），方法用冒号调用（ `encounter:AddEnemy(...)` ）。<br>
    一个字段被定义为函数时它就是方法，所以上面这张表看着和属性表很像，但调用方式不同。

!!! warning "警告并非报错"
    `AddItem` 与 `AddEnemy` 在发现数据不合法时不会中断游戏，而是打印一条警告并替换为默认值：

    ```
    [Battle - Items] WARNING: Invalid item id.
    [Battle - Enemy] WARNING: Invalid enemy id, using default.
    ```

    该行为保证战斗流程不中断，但警告不会指出具体是哪一个敌人或物品的数据不合法，出现警告时需核对遭遇文件中的对应条目。

---

## 回合脚本

`wave` 填写的是回合脚本的名字（不带 `.lua` 后缀），例如 `bones.wave1` 。<br>
这个名字会交给 `Battle.LoadWave` 去解析，查找顺序为：

1. `Game/Waves/<名字>.lua`：Game 区，优先。
2. `Scripts/Waves/<名字>.lua`：引擎默认，兜底。

若两个位置均未找到，或 Game 区那一份**存在但加载时报错**，引擎会打印警告，并自动退回使用默认的 `wave` 脚本，战斗不会因单个波次文件而中断。

!!! warning "回退时的终端输出"
    找不到时：

    ```
    [Battle - Wave] WARNING: wave 'bones.wave1' not found. Searched, in order:
        Game.Waves.bones.wave1  (Game/Waves/bones/wave1.lua)
        Scripts.Waves.bones.wave1  (Scripts/Waves/bones/wave1.lua)
    [Battle - Wave] Falling back to the default wave (Scripts.Waves.wave).
    ```

    Game 区那一份加载失败时（**注意：此时仍会成功回退，但一定会输出覆盖存在问题的提示**，不会静默）：

    ```
    [Battle] WARNING: 'Game.Waves.bones.wave1' exists but failed to load; using Scripts.Waves.bones.wave1 instead.
    [Battle]   <真正的错误信息>
    ```

    因此，输出 `exists but failed to load` 表示 Game 区的覆盖未生效，需修复该文件。

可用方法：

!!! example "回合脚本方法"
    - `Battle.LoadWave(wave_name)` 加载一个回合脚本，返回最终被选中的波次表。
        - `wave_name` 回合脚本名字。留空或填 `nil` 时使用默认的 `wave` 。
    - `Battle.waveModule` 上一次实际加载成功的模块全名，例如 `Game.Waves.bones.wave1` 。可以用来确认覆盖有没有生效。
    - `Battle.ClearWaveModule(wave_name)` 清除回合脚本的缓存。
        - `wave_name` 回合脚本名字。留空时使用当前的 `Battle.wave` 。

!!! tip "清理两处缓存的原因"
    `ClearWaveModule` 会**同时**清掉 Game 区和引擎目录下的同名缓存。<br>
    这样当一份脚本在两个位置之间搬动过（从 `Scripts/Waves/` 挪到 `Game/Waves/` ）时，不会残留上一次的旧版本。

---

## 敌人动画

从 `3.0.0` 开始，动画与遭遇文件互相绑定，战斗过程中对动画的操作由专门的函数接收。

动画**不使用元表**：`New(pos)` 返回的是一张普通表，里面用 `_class` 指回模块本身，
所有函数都用点号声明、第一个参数是实例 `self` 。`New` 结束前会调用一次
`Battle.BindAnimation(self, 本模块)` ，把这些函数**绑定到实例自己身上**，
于是外部分发时写成点号、不传 `self` ：

```lua
anim.SetFace(3)        -- 而不是 cls.SetFace(anim, 3)
anim.Update(dt)
anim.cpos[1] = 100     -- 位置本身就是实例上的普通字段，直接读写
```

写成冒号（ `anim:Update(dt)` ）会把实例多传一次，引擎会直接报错。
（贴图仍然是引擎对象，保持冒号写法 `sprite:Set(...)` 。）

这是一个标准动画模板：

??? example "动画模板"

    ```lua
    local MyMonster = {}

    function MyMonster.New(pos)
        local self = {}

        -- 实例用 `_class` 指回本模块
        self._class = MyMonster

        self.running = true
        self.x = 0
        self.y = 0
        self.elements = {}
        self.hurting = false
        self.hurttime = 0
        self.intensity = 16
        MyMonster.Init(self, pos)

        -- 必写：把本模块的函数绑到实例上，调用方才能写 `anim.Hurt()`
        Battle.BindAnimation(self, MyMonster)

        return self
    end

    function MyMonster.Init(self, pos)
        local _pos = (pos or {320, 140})
        local sprite = Sprites.CreateSprite("poseur.png", "UI")
        sprite:MoveTo(_pos[1], _pos[2])

        self.sprite = sprite
        self.cpos = {sprite.x, sprite.y}
    end

    function MyMonster.Hurt(self)
        self.hurting = true
        self.intensity = 16
    end

    --- OPTIONAL: called the moment an attack is LAUNCHED at this enemy, before the
    --- hit lands. Implement it to react (brace / dodge / telegraph / counter, ...).
    --- `data` may contain:
    ---   data.enemy    → this enemy table
    ---   data.damage   → planned damage for the hit
    ---   data.perfect  → true when the timing landed in the perfect zone
    ---   data.offset   → distance from the perfect zone (0 = perfect)
    ---   data.position → {x, y} of the enemy on screen
    ---   data.attack   → the attack pattern instance
    function MyMonster.OnAttack(self, data)
    end

    function MyMonster.Spare(self)
    end

    function MyMonster.Update(self, dt)
        if (not self.running) then
            return
        end

        -- ====================>
        -- TODO: put your monster's animation code here.
        --
        -- Example: react to engine-provided state
        --   if (self.canspare) then ... end            -- spareable?
        --   if (self.dead) then                        -- HP hit 0 and killable
        --       self.sprite:SetAnimation({"death_0.png", "death_1.png"}, 0.1)
        --   end

        -- Default hurt shake: knock the sprite sideways, decaying toward 0.
        if (self.hurting) then
            local p = self.sprite
            p.x = self.cpos[1] + self.intensity
            if (self.intensity > 0) then
                self.intensity = self.intensity - 1
                self.intensity = -self.intensity
            elseif (self.intensity < 0) then
                self.intensity = -self.intensity
            end
        end
        -- <====================
    end

    function MyMonster.Destroy(self)
        if (not self.sprite) then
            return
        end

        -- TODO: play a death effect here, e.g. sprite:Dust(true, true)
        self.sprite:Dust(true, true)
        self.sprite = nil

        -- Destroy every extra object registered in `elements`.
        for i = #self.elements, 1, -1
        do
            local e = self.elements[i]
            if (e and e.Destroy) then
                e:Destroy()
            end
        end
        self.elements = {}
    end

    return MyMonster
    ```

以下列出全部函数。括号中是**模块内部的签名**，函数体依赖这些 `self` 工作；
从外面（场景、波次、攻击模式）调用时一律写成 `anim.Foo(...)` 、不传 `self` ，
例如 `anim.Hurt()` 、`anim.Update(dt)` 、`anim.SetFace(3)` 。

!!! example "函数方法"
    - `New(pos)` 动画的位置，返回一张独立的普通表实例。
    - `Init(self, pos)` 动画初始化，负责创建贴图和变量。
    - `Hurt(self)` 受伤的时候会执行（玩家武器发出Hurt信号）。
    - `OnAttack(self, data)` 校准的时候按下攻击键则会执行，data存储校准结果等。
    - `Spare(self)` 成功饶恕时会执行，可以制作如敌人变黑等效果。
    - `Destroy(self)` 被杀死时会执行一次，可以用来制作化尘等操作。
    - `Update(self, dt)` 每帧执行，绝大部分动画代码都写在这里。

### 初始化动画

初始化流程部分由引擎完成： `InitAnimation` 由引擎通过 `game_apis` 提供，需在战斗场景中调用，每个敌人调用一次。

`index` 为敌人在 `enemies` 表中的序号。取值超出范围或不匹配时不会报错，终端仅输出一条警告。

!!! warning "终端警告"
    ```
    [Game - Animation] WARNING: Enemy #x has no animation.
    ```

`pos` 用于指定动画位置。战斗中每个敌人的站位不同，在初始化分配敌人时需使用 `pos` 参数调整位置。

!!! example "使用示例"

    ```lua
    local mobs = {"froggit", "whimsum", "migosp"}
    local ypos = {
        ["froggit"] = 160
        ["whimsum"] = 80
        ["migosp"]  = 200
    }

    -- 保存 ypos 之后，指定要生成的敌人
    for i = 1, 3
    do
        -- 从这三个怪物里随机选出一个来
        local name = mobs[math.random(#mobs)]

        Game:AddEnemy(
            {
                id = name,
                name = name,
                animation = require("Game.Animations." .. name),

                maxdamage = 400,
                dmg_float = 2,  -- Some random stuff......I hate them

                show_hpbar = true, -- Sans... stop hiding your hp bar.
                maxhp = 100,
                hp = 100,
                gold = 1,
                exp = 1,

                defensetext = "MISS",
                misstext = "MISS",

                canspare = true,
                killable = true,

                -- 设置位置
                position = {100 + 150 * (i - 1), ypos[name]},

                actions = {
                    {id = "Check", name = Localize.localizeText("Battle.Actions.Names.Check")},
                    {id = "Pose",  name = Localize.localizeText("Battle.Actions.Names.Pose")},
                }
            },
        )
    end
    ```

---

### 编写动画

同人作品可省略 `Spare` 功能，动画代码主要写在 `Update` 函数中。

```lua
function MyMonster.Update(self, dt)
    if (not self.running) then
        return
    end

    -- ====================>
    -- TODO: put your monster's animation code here.
    --
    -- Example: react to engine-provided state
    --   if (self.canspare) then ... end            -- spareable?
    --   if (self.dead) then                        -- HP hit 0 and killable
    --       self.sprite:SetAnimation({"death_0.png", "death_1.png"}, 0.1)
    --   end

    -- Default hurt shake: knock the sprite sideways, decaying toward 0.
    if (self.hurting) then
        local p = self.sprite
        p.x = self.cpos[1] + self.intensity
        if (self.intensity > 0) then
            self.intensity = self.intensity - 1
            self.intensity = -self.intensity
        elseif (self.intensity < 0) then
            self.intensity = -self.intensity
        end
    end
    -- <====================
end
```

注释中给出示例：可用 `canspare` 切换动画，用 `dead` 切换另一套动画。该注释中的代码无法直接运行。<br>
不依赖这些条件时，可另行编写常规动画。

动画编写的详细教程见 **[高阶开发 → 数学教程](../050_intermediate/040_math.md)** 。

以下以 Sans 为例作部分讲解：

??? example "Sans动画"

    ```lua
    function Sans.OnAttack(self, data)
        local ty = 220
        Tween.CreateTween(function (v)
            self.cpos[1] = v
        end, "Quad", "Out", 320, ty, 40)
        Tween.CreateTween(function (v)
            self.cpos[1] = v
        end, "Quad", "Out", ty, 320, 35, 80)
    end

    function Sans.Spare(self)
        -- Spared: sans fades out instead of dying.
        for _, sprite in ipairs(Sans.AllSprites(self)) do
            sprite.alpha = 0.5
        end
    end

    function Sans.Update(self, dt)
        if (not self.running) then
            return
        end

        if (not self.legs or not self.body or not self.head or not self.cpos) then
            return
        end

        -- A "30 FPS frame tick": every counter ported from the original advances by
        -- this much, so the animation speed is frame-rate independent.
        local step = dt * SOURCE_FPS

        -- ====================>
        -- 1) SWAY / BOUNCE ----------------------------------------------------
        -- bounce 0 = still, 1 = idle 8-shape, 2 = medium bob, 3 = tired bob.
        local xoff, yoff = 0, 0
        local bounce = math.floor(self.bounce or 0)

        if (bounce == 3) then
            -- Large, slow vertical breathing (worn-out sans).
            self.siner = self.siner + step
            yoff = math.sin(self.siner / 18) * 2
        elseif (bounce == 2) then
            -- Medium vertical bob.
            self.siner = self.siner + step
            yoff = math.sin(self.siner / 15) * 4
        elseif (bounce == 1) then
            -- Idle: fast vertical + slow horizontal → a small figure 8.
            self.siner = self.siner + step
            yoff = math.sin(self.siner / 3)
            xoff = math.cos(self.siner / 6)
        else
            -- Still.
            self.siner = 0
        end

        local scale = self.bounce_scale or 1
        xoff = xoff * scale
        yoff = yoff * scale
        self.xoff = xoff
        self.yoff = yoff

        -- 2) HURT SHAKE -------------------------------------------------------
        -- Same decay as the reference: flip the sign every tick while the
        -- magnitude shrinks by one unit per tick (0.5 units per frame at 60 FPS).
        local shake_x = 0
        if (self.hurting) then
            shake_x = self.intensity
            if (self.intensity > 0) then
                self.intensity = -(self.intensity - step)
            else
                self.intensity = -self.intensity
            end

            if (math.abs(self.intensity) <= step) then
                self.intensity = 0
                self.hurting = false
            end
        end

        -- 3) HEAD OFFSETS (attack poses) --------------------------------------
        if (self.head_auto_return) then
            local k = math.min(1, (self.head_return_speed or 6) * dt)
            self.headx = self.headx - self.headx * k
            self.heady = self.heady - self.heady * k
            if (math.abs(self.headx) < 0.05) then self.headx = 0 end
            if (math.abs(self.heady) < 0.05) then self.heady = 0 end
        end

        -- 4) BLUE-EYE AUTO-OFF (only for :FlashBlueEye) -----------------------
        if (self._blueeye_timer) then
            self._blueeye_timer = self._blueeye_timer - dt
            if (self._blueeye_timer <= 0) then
                self._blueeye_timer = nil
                if (self._blueeye_flash) then
                    self._blueeye_flash = false
                    self.facetype = 0
                    self.f_i = 0
                end
            end
        end

        -- 5) TORSO IDLE CYCLE --------------------------------------------------
        -- The original only drew the plain torso while no arm animation was
        -- playing (`movearm == 0`); the same flag pauses this cycle.
        if (math.floor(self.movearm or 0) == 0) then
            self.torso_time = self.torso_time + dt
            if (self.torso_time >= TORSO_INTERVAL) then
                self.torso_time = self.torso_time - TORSO_INTERVAL
                self.torsoframe = (self.torsoframe + 1) % TORSO_FRAMES
                self.body:Set(self.torso_frames[self.torsoframe + 1])
            end
        end

        -- 6) FACE / BLUE EYE / SWEAT ------------------------------------------
        Sans.UpdateFace(self, step)

        -- 7) PLACE EVERY PART --------------------------------------------------
        Sans.ApplyOffsets(self, xoff, yoff, shake_x)

        -- 8) DEATH -------------------------------------------------------------
        -- `self.dead` is set by Battle.Update once HP hit 0 and the enemy is
        -- killable. sans has no death sheet yet, so we just freeze the idle sway
        -- and let Destroy() play the dust effect. Add your own animation here.
        if (self.dead) then
            self.bounce = 0
        end
        -- <====================
    end
    ```

该代码较长，此处仅取 `bounce = 1` 时的待机左右摇摆动画：

!!! example "待机动画"

    ```lua
    self.siner = self.siner + step
    yoff = math.sin(self.siner / 3)
    xoff = math.cos(self.siner / 6)
    ```

三角函数产生周期性位移， `/3` 与 `/6` 对应两个不同的速度，头部与身体的移动轨迹呈 `∞` 形。