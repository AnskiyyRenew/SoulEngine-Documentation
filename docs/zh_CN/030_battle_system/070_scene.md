---
title: 战斗场景与回调
---

战斗的**流程**由引擎负责，战斗的**内容**由遭遇文件负责，介于两者之间的这一层——这一场战斗的具体表现（如使用物品回复的血量、逃跑时播放的内容）——写在战斗场景里。

路径： `Scripts/Scenes/Battle/` 。引擎自带 `scene_battle.lua` 、 `scene_battle_init.lua` 、 `scene_battle_template.lua` 、 `scene_battle_ow.lua` 四份，可参照其中一份实现。

---

## 场景骨架

```lua
local scene = {}

-- 1) 导入战斗模块
Battle = ImportFile("Battle")
Battle.SetEndRoom("scene_end")

-- 2) 载入遭遇文件
Game = Battle.SetGame("Poseur")
Game:AddItem({id = "STABLE", _color = {0.5, 0, 0}, name = "ImNotFood"})

-- 3) 初始化每个敌人的动画（有几个敌人就写几行）
--    位置就是实例上的普通字段，动画操作也直接写在实例上（点号、不传 self）
Game:InitAnimation(1, {320, 140})

-- 例：拿到实例后改表情 / 挪位置
-- local boss = Game.enemies[1].animation
-- boss.SetFace(3)
-- boss.cpos[1] = 260

-- 4) 写回调
local function HandleItems(item)
    Player.Heal(99, true)
    Battle.BattleDialogue({"* You ate " .. item.name .. "."}, "ACTIONSELECT")
end

Battle.HandleItems = HandleItems

-- 5) 背景
local background = Sprites.CreateSprite("px.png", "Background")
background:Scale(640, 480)

function scene.update(dt)
    Battle.Update(dt)
end

function scene.clear()
    Layers.clear()
    Battle.Clear()
end

return scene
```

!!! danger "`scene.clear` 里两行都不能少"
    `Battle.Clear()` 负责清掉遭遇、动画、波次、灵魂、攻击模式这一整套缓存；<br>
    `Layers.clear()` 负责清图层。少写前者，第二次进战斗会拿到上一场残留的状态（敌人还带着上次的血条、灵魂沿用上次的颜色），而且**不会报错**，问题难以定位。

---

## 回调一览

这些回调都是 `Battle` 上的字段，引擎在固定时机调用它们。**在场景里覆盖即可**，不写就用引擎里的空实现。

!!! example "流程回调"
    - `Battle.HandleActions(enemy, action)` 玩家在 `ACTMENU` 里确认了某个行动。
        - `enemy` 被行动的敌人表。
        - `action` 被选中的行动表，含 `id` 与 `name` 。
    - `Battle.HandleItems(item)` 玩家使用了某个物品。
        - `item` 被使用的物品表。物品是否销毁由引擎处理（ `_cantdestroy` 为 `true` 时保留）。
    - `Battle.HandleSpare()` 玩家在 `MERCYMENU` 里选了 `饶恕` ，**而且场上还有敌人没被饶恕掉**。
        - 可选饶恕的敌人这时候已经被移除，并把 `gold` 结算进了 `Battle.GOLD` 。
        - 一个敌人都不剩时引擎直接 `Battle.Win()` ，**不会**走到这里；该回调只在部分敌人可饶恕的场面触发。
    - `Battle.HandleFlee()` 玩家在 `MERCYMENU` 里选了 `逃跑` 并判定成功。
    - `Battle.FleeUpdate(dt)` 处于 `FLEEING` 状态时每帧调用。
    - `Battle.DefenseEnding()` 敌人回合结束、回到玩家回合的瞬间调用。
    - `Battle.OnHit(bullet)` 玩家的灵魂碰到了某颗弹幕。
        - `bullet` 撞到的贴图对象，读它的 `HurtMode` 来决定要不要扣血。
    - `Battle.EnteringState(old, new)` 状态发生切换时调用。**覆盖时必须先调用默认实现**：
        ```lua
        local function EnteringState(oldstate, newstate)
            Battle.defaultEnteringState(oldstate, newstate)
            -- 你自己的逻辑
        end
        ```
    - `Battle.Win(extra_texts, on_complete)` 战斗胜利。同样需调用 `Battle.defaultWin`：
        ```lua
        local function Win()
            Battle.defaultWin({"* Your LOVE increased!"})
        end
        Battle.Win = Win
        ```

!!! warning "`HandleSpare` 在引擎中为空函数，需在场景中接管"
    引擎中只有一句 `function battle.HandleSpare() end` 。<br>
    而按确认选饶恕的同一帧，引擎已经 `destroy_elements()` 把饶恕菜单的选项（ `state.typers` ）清空了。
    未接管该回调且状态仍停留在 `MERCYMENU` 时，下一帧会读取已被清空的表，直接报 `attempt to index a nil value` 。

    因此只要战斗中存在"一部分敌人能饶恕、另一部分不能"的情况，就必须在场景中接管该回调。可直接推进到敌人回合：

    ```lua
    local function HandleSpare()
        Battle.BattleDialogue({"* 剩下的敌人可没打算放过你。"}, "DEFENDING")
    end

    Battle.HandleSpare = HandleSpare
    ```

    自带的两只 Poseur 都是 `canspare = true` ，一次饶恕即清空敌人、直接走 `Win()` ，因此演示场景不会触发该回调。

!!! example "OnHit 的标准写法"
    引擎将弹幕的 `HurtMode` 原样传入，其解释方式由场景决定：

    ```lua
    local function OnHit(bullet)
        local damage = 1
        local mode = (bullet["HurtMode"] or "normal"):lower()

        if (mode == "normal") then
            Player.Hurt(damage)
        elseif (mode == "blue" or mode == "cyan") then
            -- 蓝色：动了才受伤
            if (Controller.GetState("arrows") > 0) then
                Player.Hurt(damage)
            end
        elseif (mode == "orange") then
            -- 橙色：不动才受伤
            if (Controller.GetState("arrows") <= 0) then
                Player.Hurt(damage)
            end
        end
    end
    ```

---

## 对话

战斗中的文本通过打字机输出，引擎提供两个封装函数：

!!! example "对话方法"
    - `Battle.BattleDialogue(texts, final_state)` 播一段旁白，播完后切到指定状态。
        - `texts` 文本数组（**不能用中文**，除非字体支持）。
        - `final_state` 播完切到哪个状态，默认 `"ACTIONSELECT"` 。
    - `Battle.FullDialogue(texts, call)` 播一段旁白，播完后执行一个函数。
        - `call` 播完要做的事，例如 `function () Battle._end = true end` 。
    - `Battle.narration_text` 战斗框里那行常驻旁白的打字机对象。

!!! note "战斗文本里的等待与快进"
    `texts` 里可以混写打字机标签，战斗对话最常见的两个是：

    - `[wait:x]` 停 `x` **秒**再继续。它使用打字机**自身的** `waittime` 计时器，与逐字间隔**互不干扰**：写 `[wait:0.5]` 之后再写 `[speed:0.01]` ，该停顿不会被加速跳过。
    - `[speed:x]` 改逐字间隔（每字 `x` 秒），改完一直生效到下一次 `[speed:]` 。默认 `1/15 ≈ 0.0667` 秒。

    玩家按住**取消键**（默认是 `X` ）时，引擎会**直接清掉当前的 `waittime`** 并立即输出剩余文本，不会逐段等待。带 `[noskip]` 的文本不响应快进。

    完整标签表见 [基础开发 → 打字机](../020_basic/030_typers.md) 。

---

## 状态与流程控制

!!! example "状态方法"
    - `Battle.ChangeState(new_state)` 切换状态。该函数是唯一的切换入口，会保证 `EnteringState` 恰好被调用一次。
    - `Battle.state` 当前状态。可用值见 [UI → 状态流程](./010_ui.md) 。
    - `Battle.game` 当前遭遇表。
    - `Battle.EXP` / `Battle.GOLD` 本场战斗累计的EXP与金钱，敌人死亡时自动累加。
    - `Battle._end` 置为 `true` 后画面开始淡出，淡出完成就切到 `Battle.room_end` 。
    - `Battle.SetEndRoom(room)` 设置战斗结束后去哪个场景，默认 `"scene_end"` 。
    - `Battle.room_end` 当前设置的结束场景名。

!!! example "选中项"
    - `Battle.selected_enemy_index` 玩家当前选中的是第几个敌人。
    - `Battle.selected_action_index` 玩家当前选中的是第几个行动。
    - `Battle.selected_index` 玩家当前选中的是第几个物品。

这三个值在 `EnteringState` 中用于判断具体操作，例如判断玩家是否对 1 号敌人使用了 Check。

---

## 其它可用方法

!!! example "通用方法"
    - `Battle.Update(dt)` 每帧调用，推进玩家、战斗框、UI 与所有敌人动画。
    - `Battle.UpdateRestore(dt)` 敌人回合结束后战斗框回弹期间调用，引擎已自动接好。
    - `Battle.Clear()` 清掉整棵战斗模块树与 Game 区的战斗内容缓存。
    - `Battle.SetGame(file)` 载入遭遇文件，返回遭遇表（不返回时说明没找到）。
    - `Battle.SetAttackPattern(name)` 切换攻击模式，详见 [攻击模式](./040_attack.md) 。
    - `Battle.Defending()` 手动进入敌人回合（通常由状态机自动进入）。

---

## 与 Overworld 衔接

从主世界撞进来的战斗用的是 `scene_battle_ow.lua` ，它比普通战斗场景多了两件事：

1. **进场**：把 `DATA.player` 的存档数据推进 `Player` ，战斗用的是真实血量而不是遭遇文件里的模板值。
2. **出场**： `scene.clear` 时把 EXP / GOLD / 剩余血量写回 `DATA` ，并按 `DATA.lv_data` 结算升级。

修改升级规则（如将等级上限由 20 级扩展到 30 级、调整每级的 HP 曲线）时，修改 `Game/Logics/init.lua` 中的 `lv_data` 表，详见 **[游戏逻辑与世界规则](../020_basic/120_game_logics.md)** ；<br>
修改战斗奖励时，调整遭遇文件中敌人的 `exp` 与 `gold` 。

---

## 调试排查

- 敌人动画未出现：检查终端是否输出 `[Game - Animation] WARNING: Enemy #x has no animation.` ，原因为 `InitAnimation` 的下标错误。
- 波次未生效：检查是否输出 `exists but failed to load` ，详见 [战斗初始化](./000_init.md) 。
- 第二次进战斗状态异常：检查 `scene.clear` 中的 `Battle.Clear()` 。
- 战斗结束未切换场景：检查 `Battle.SetEndRoom` 设置的场景名是否存在。
- **判定与表现不符**（未接触却扣血 / 已接触却不扣血）：按 `F7` 打开判定框覆盖层，也可在代码中调用 `Battle.ToggleHitboxes(true)` 。开启完美像素碰撞时显示的是真实像素轮廓而非矩形，详见 [基础开发 → 精灵 → 完美像素碰撞](../020_basic/020_sprites.md) 。
