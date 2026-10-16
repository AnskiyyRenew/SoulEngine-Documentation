---
title: Step 每帧回调
---

`Step` 不是一个库函数，而是一个**约定字段**：把它挂在对象上，引擎每帧发现它存在，就调用一次。

引擎中有三处会调用它：贴图（ `Scripts/Libraries/Sprites.lua` ）、骨头（ `Scripts/Libraries/Attacks/Bones.lua` ）、蓝灵魂平台（ `Scripts/Libraries/Battle/Player/init.lua` ）。

| 宿主 | 签名 | 谁在调 | 时机 |
|---|---|---|---|
| 贴图 `sprite` | `function (self, dt)` | `Sprites.Update(dt)` ， `main.lua` 每帧自动调 | 速度结算之后、动画推进之前 |
| 骨头 `bone` | `function (self)` **没有 dt** | `bones.Update(dt)` ，波次里手动调 | 位移与三部件摆位算完之后 |
| 平台 `platform` | `function (self)` **没有 dt** | `Player.UpdatePlatforms(dt)` | 平台移动与 `Sync()` 之后、踩踏判定之前 |

!!! note "它和 Update 不是一回事"
    `Update` 是引擎自身的每帧流程，不可覆盖；`Step` 是引擎在 `Update` 中预留的一个插槽。<br>
    所以 `Step` 里不要再去调 `self:Update(dt)` 。

---

## 贴图上的 Step

### 用法

```lua
local spr = Sprites.CreateSprite("poseur.png", "Map")
spr.Step = function (self, dt)
    -- 每帧都会进到这里
end
```

摘掉钩子就是赋 `nil` ： `spr.Step = nil` 。

### 它在每帧的哪个位置

`main.lua` 的 `Sprites.Update(dt)` 会**倒序**遍历所有贴图，逐个调 `sprite:Update(dt)` 。`Update` 内部的顺序是：

1. 清零 `speed` / `is_moving`
2. 父级锚点（ `parent` 配合 `follow_mode` ）
3. 速度位移（ `velocity` × `move_speed` ）
4. **调用 `self:Step(dt)`**
5. 推进动画帧（ `animation` ）
6. 尘埃计时（ `_dust` ）、抖动偏移（ `_shake` ）
7. 把碰撞体同步到当前坐标（ `_solid` ）

!!! example "由此得到两条结论"
    - 在 `Step` 里改 `x` / `y` / `rotation` **会生效**，后续步骤不会再覆盖坐标。
    - 在 `Step` 里 `self:Set(...)` 换贴图同样安全： `Set` 会清空正在播放的动画序列（见 `Sprites.lua` 的 `Set` ），不会被下一帧的动画覆盖。

### 示例：放大淡出后自毁

```lua
local shadow = Sprites.CreateSprite(Player.sprite.path, Player.sprite.layer)
shadow:MoveTo(Player.sprite:GetPosition())
shadow.Step = function (self)
    self:MoveTo(Player.sprite:GetPosition())
    self:Scale(
        self.xscale + (2 - self.xscale) / 8,
        self.yscale + (2 - self.yscale) / 8
    )
    self.alpha = self.alpha - 0.05

    if (self.alpha <= 0) then
        self:Destroy()
    end
end
```

该段代码即 `Player.AddParticle()` 的实现（ `Battle/Player/init.lua` ），用于生成灵魂切换时的残影。

### 示例：用 dt 做帧率无关的平滑

```lua
shadow.Step = function (self, dt)
    self:MoveTo(st.source:GetPosition())          -- 跟着源头跑

    local factor = math.min(1, (dt or 0) * 8)     -- dt 安全的指数逼近
    self:Scale(
        self.xscale + (2 - self.xscale) * factor,
        self.yscale + (2 - self.yscale) * factor
    )

    st.time = st.time - (dt or 0)
    if (st.time <= 0) then
        self:Destroy()
    else
        self.alpha = st.base_alpha * (st.time / st.duration)
    end
end
```

该段代码即 `Sprites.ShadowSprite()` 的实现（ `Sprites.lua` ）。使用 `dt` 时应采用上述写法，固定步长（每帧 +1）会使速度随帧率变化。

---

## 骨头上的 Step

```lua
local bone = bones.New2D("sans", 60, {320, 240}, 0, {2, 0})
bone.Step = function (self)
    -- 注意：没有 dt
    self.rotation = self.rotation + 1
end
```

- **调用点**： `bones.Update(dt)` 里，骨头的位移、旋转、长度、头/身/尾三部件摆位**全部算完之后**。所以在 `Step` 里改 `self.x` / `self.rotation` / `self.length` ，要**下一帧**才反映到贴图上（引擎注释里写明这是刻意的，与原版一致）。
- **`bones.Update(dt)` 需在波次中每帧调用**（见 [弹幕库 → 骨头](../030_battle_system/060_bullets.md) ）。不调用时，骨头不移动、不判定，`Step` 也不会执行。
- 只有组合体骨头会调用 `Step` ，即由 `New2D` / `New3D` 创建的骨头（内部 `concat = true` ）。

!!! warning "骨头拿不到 dt"
    骨头的 `Step` **不传任何参数**。要做时间相关的逻辑，在波次里自己累加：

    ```lua
    local time = 0
    function wave.Update(dt)
        time = time + dt
        bones.Update(dt)
    end
    ```

    需要延时 / 补间时使用 `Timer` 或 `Tween` ， `Step` 不提供时间参数。

---

## 平台上的 Step

```lua
local p = Player.BluePlatform(320, 320, 60, {speed = {x = 1, y = 0}})
p.Step = function (self)
    -- 平台已经动完、高亮线也同步过了，还没做踩踏判定
    if (self.image.x > 500) then
        self.speed.x = -1
    end
end
```

`Player.UpdatePlatforms(dt)` 的顺序是：按 `platform.speed` 移动 → `Sync()` 同步高亮线 → `platform:Step()` → 灵魂踩踏判定。需要在平台移动完成后补充逻辑（到达边界掉头、周期性消失等）时，写在 `Step` 中。该钩子同样**不传入 dt**。

---

## 常见写法

| 想做的事 | 写法 |
|---|---|
| 只跑一次 | 函数末尾 `self.Step = nil` |
| 到点自毁 | 条件满足时 `self:Destroy()` |
| 计时 | `self._t = (self._t or 0) + dt` |
| 帧率无关平滑 | 用 `dt` 做插值，不要写死步长 |
| 临时摘钩子 | `obj.Step = nil` |

---

## 注意

- **Step 跑在 `scene.update` 之前。** `main.lua` 的顺序是 `Tween` → `Sprites` → `Typers` → 其余各库 → `scene.update` 。所以 `Step` 里读到的输入是**上一帧**的，场景这一帧还没算。
- **暂停不会停止 Step。** `main.lua` 只将 `scene_.update` 置于 `pausing` 判断之后，`Sprites.Update(dt)` 仍会执行。暂停时需要停止 `Step` ，需在 `Step` 内自行判断。
- **贴图遍历为倒序**（ `#sprites.images → 1` ），因此在 `Step` 中调用 `self:Destroy()` 是安全的，引擎的残影也采用该方式销毁。
- `Destroy()` 之后对象从列表中移除， `Step` 不再被调用。
- **避免在 Step 中执行耗时操作。** `Step` 对每个对象每帧执行一次；大量骨头各挂一个耗时的 `Step` 会占用帧预算。可在波次 / 场景层统一处理的逻辑不放在单个对象上。
