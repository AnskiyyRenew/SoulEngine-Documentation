---
title: 攻击模式
---

按下 `战斗` 按钮、选完敌人、再按确认之后，屏幕中间出现的那条**来回滑动的校准条**，由攻击模式（ `PlayerAttack` ）实现。

攻击模式负责三件事：绘制校准条、判定按下确认键的时机、将伤害结算给敌人。

路径： `Game/Attacks/` （Game 区，优先）、 `Scripts/Libraries/Battle/PlayerAttacks/` （引擎默认，兜底）。

![BA-04](../img/030_battle_system/ba_04_attack_bar.png)

---

## 切换攻击模式

默认使用 `stick` （木棍，原版的基础武器）。更换为其他武器（如真刀、手套）时，编写一份攻击模式文件并切换：

!!! example "切换方法"
    - `Battle.SetAttackPattern(name)` 按名字加载并切换攻击模式。
        - `name` 攻击模式文件的名字（不带 `.lua` ）。
    - `Battle.attack` 当前生效的攻击模式对象。
    - `Battle.attack_paths` 已经加载过的攻击模式模块名列表， `Battle.Clear()` 会按它清理缓存。

如果指定的名字找不到，引擎会打印警告并**自动退回 `stick`** ，保证战斗不至于卡死：

```
[Battle - PlayerAttack] WARNING: attack pattern 'real_knife' not found. Searched, in order:
    Game.Attacks.real_knife  (Game/Attacks/real_knife.lua)
    Scripts.Libraries.Battle.PlayerAttacks.real_knife  (Scripts/Libraries/Battle/PlayerAttacks/real_knife.lua)
[Battle - PlayerAttack] Falling back to the default pattern (stick).
```

---

## 攻击模式要提供什么

一个攻击模式文件就是一个 Lua 表，引擎会在固定的时机调用它下面这几个函数：

!!! example "必须实现的接口"
    - `Restart(enemy)` 攻击开始，引擎把目标敌人传进来。这里要创建校准条等所有贴图。
    - `Update(dt)` 每帧调用，推进校准条、读取确认键、结算伤害。
    - `Destroy()` 收尾：销毁贴图，并把 `_end` 置为 `true` 。

!!! example "可选接口"
    - `SetMaxDamage(dmg)` 强制本次伤害为一个固定值（跳过公式计算），用于必定打出满伤的演出。
    - `Hurt()` 通知目标敌人的动画受到攻击。
    - `Attack(data)` 通知目标敌人的动画攻击已发动（尚未结算）， `data` 中包含：
        - `data.enemy` 目标敌人表。
        - `data.damage` 本次计划造成的伤害。
        - `data.perfect` 是否落在完美区间。
        - `data.offset` 距完美区间的距离， `0` 即完美。
        - `data.position` 敌人的屏幕坐标 `{x, y}` 。
        - `data.attack` 攻击模式对象本身。

!!! example "引擎会读取的字段"
    - `_end` 攻击是否结束。引擎看到它变成 `true` 才会把状态推进到下一个敌人回合。
    - `_missed` 这一刀是否打空了。
    - `_attacked` 是否已经按下过确认键。

---

## 内置 stick 的伤害计算

`stick` 的判定逻辑可直接复用：

- 校准条从屏幕一侧滑向另一侧，速度 `6` 像素/帧。
- 游标与目标标记的距离 `offset` 决定伤害：
    - `offset <= 12` → **完美**，伤害 = `maxdamage + random(0, dmg_float)` 。
    - 否则 → 伤害 = `max(maxdamage * 0.2, ceil(0.9 * maxdamage * (280 - offset) / 280))` 。
- 游标冲出边界 → 判定为 MISS，不加伤害，并在敌人位置弹出 `MISS` 文本。

调用 `SetMaxDamage(dmg)` 时，上述公式会被整体跳过，直接使用传入的值。该函数内部通过 `_max` 标记实现，**每次结算后自动复位**，不影响下一次攻击。

时间轴（按帧计数）：

| 帧 | 发生什么 |
|---|---|
| 按下确认 | 停住游标、播放挥砍音效与刀光、调用 `Attack(data)` |
| 第 70 帧 | 结算伤害：血条动画、 `Hurt()` 、弹出伤害数字、真正扣血 |
| 第 130 帧 | `Destroy()` |

MISS 分支流程更短：第 1 帧弹出 MISS 文本，第 30 帧结束。

!!! tip "伤害公式中两个数值的来源"
    `maxdamage` 和 `dmg_float` 都写在遭遇文件里，是每个敌人自己的属性，详见 [战斗初始化 → 遭遇文件](./000_init.md) 。<br>
    攻击模式只是读它们，不负责定义。

---

## 写一个自己的攻击模式

可将 `Scripts/Libraries/Battle/PlayerAttacks/stick.lua` 复制到 `Game/Attacks/` 下，重命名后再修改。

下面是一份最小骨架：

```lua
local atk = {_end = false}
local enemy = nil
local attacked = false

function atk.Restart(_enemy)
    atk._end = false
    enemy = _enemy
    attacked = false

    -- 在这里创建校准条贴图
end

function atk.Destroy()
    -- 销毁贴图
    atk._end = true
end

function atk.Update(dt)
    if (not attacked) then
        if (Controller.GetState("confirm") == 1) then
            attacked = true
            -- 计算伤害、播音效、通知动画
        end
    else
        -- 播放收尾演出，结束后调用 atk.Destroy()
    end
end

return atk
```

!!! warning "`_end` 一定要置为 true"
    引擎通过轮询 `_end` 判断本次攻击是否结束。未置位时战斗会**永久停在这一刀**，且没有任何报错提示。

---

## 与敌人动画的配合

攻击模式**不应该**直接操作某个怪物的贴图——它只管结算，表现交给动画。

两个通知函数就是为此存在的：

- `Attack(data)` 在按下确认的瞬间调用，敌人可以在 `OnAttack` 里做闪避、格挡、预备动作。
- `Hurt()` 在伤害真正生效时调用，敌人可以在 `Hurt` 里做受击抖动。

这样同一套攻击模式可以套在任意怪物身上，换怪不用改攻击模式。

!!! note "通知传递到动画的方式"
    两个函数都只做一件事：从 `enemy.animation` 取到目标动画实例，然后调它的同名方法。

    ```lua
    local anim = enemy.animation
    if (type(anim) == "table" and anim._bound and anim.Hurt) then
        anim.Hurt()
    end
    ```

    也就是说，**怪物动画要自己实现 `Hurt()` / `OnAttack(data)` 才有反应**，而且在 `New(pos)` 末尾必须调过 `Battle.BindAnimation(self, 本模块)` 拿到 `_bound` ，否则这次通知会被静默跳过（不报错）。动画侧的写法见 [战斗初始化 → 敌人动画](./000_init.md) 。
