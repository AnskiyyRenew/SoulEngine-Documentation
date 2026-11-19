---
title: ❕️ 开发者模式（回合跳转）
---

测试后期回合时，从第一个回合一路打过去代价很高。开发者模式提供一个**回合选择面板**，可以直接跳到任意回合脚本，或立刻结束当前敌人回合。

**仅开发版生效**： `_RELEASED = true` 时 `main.lua` 不加载该模块，发布包中不存在此功能。

---

## 解锁

在任意场景按顺序输入 `e` `n` `d` 三个字母（相邻两次间隔不超过 1.5 秒，期间不按住 Ctrl / Alt / Win）：

- 控制台打印 `[DevMode] developer mode ON`；
- 当前在战斗中时，选择面板立即打开；
- 再输入一次 `e` `n` `d` 关闭开发者模式并关闭面板。

!!! note "不会误触的场合"
    文本输入框获得焦点时（例如取名场景），按键序列不参与匹配；按住修饰键时同样不匹配。

---

## 面板操作

| 操作 | 键 |
|---|---|
| 打开 / 关闭面板 | `F10` |
| 关闭面板 | `Esc` |
| 上下移动光标 | `↑` `↓` ；翻页 `PageUp` `PageDown` ；`Home` `End` |
| 展开 / 收起文件夹 | `→` `←` ，或鼠标点击 |
| 跳到高亮的回合 | `Enter` 或 `Space` |
| 结束当前敌人回合 | `S` |
| 开关无敌 | `I` |
| 滚动列表 | 鼠标滚轮 |

鼠标点击整行即可选择。面板打开期间当前场景被暂停（ `scene.pausing` ），敌人回合不会在浏览列表时推进。

---

## 列表结构

面板按目录树列出引擎能够加载的回合脚本，顺序与解析顺序一致：

- `Game/Waves/` （Game 区，优先）
- `Scripts/Waves/` （引擎默认，兜底）

**文件夹即命名空间**。`Game/Waves/bones/wave1.lua` 对应的回合名是 `bones.wave1` ，也就是遭遇战脚本 `wave` 字段要填的字符串：

```lua
return {
    state = "ACTIONSELECT",
    wave  = "bones.wave1",   -- Game/Waves/bones/wave1.lua
}
```

因此项目里的文件夹布局就是面板里的层级，不需要额外的注册表或编号。文件名以 `_` 开头的脚本（如 `_template.lua` ）不会列出。

当前正在播放的回合以 `*` 标记并高亮；打开面板时，光标会先定位到该回合所在的文件夹并自动展开。

---

## 跳转做了什么

跳转不会直接改写 `Battle._wave` ，而是走与正常流程相同的状态迁移，避免留下半拆解的战斗状态：

```
当前在 DEFENDING
  ↓ Battle.ChangeState("ACTIONSELECT")
  ├─ 当前回合的 wave.EndWave()（销毁它创建的弹幕与对象）
  ├─ 清掉该回合的模块缓存
  ├─ Arenas.Clear()，主战斗框恢复 565x130
  ↓ clearWaveModule(目标回合)
  ↓ Battle.wave = 目标回合
  ↓ Battle.ChangeState("DEFENDING")
  └─ Battle.Defending()：LoadWave 重新执行目标回合文件的顶层代码
```

两个细节：

- **模块缓存会被清掉**，所以跳到已经播过的回合同样会重新执行它的顶层代码，闭包与状态不会沿用上一次。
- 共享的 `Battle.Waves` 表上的 `ENDED` 会被复位，否则 `ENDED = true` 会让下一个回合刚进入就结束。

`S` 结束当前回合走的是同一条路径：调用 `EndWave()` 后再切回 `ACTIONSELECT` 。

---

## 无敌

`I` 开关无敌。开启后 `Player.Hurt` 在入口直接返回，因此**致死伤害不会先扣血再被补回**（后者在致命一击时来不及生效）。`Player.AddKR` 未做拦截，KR 仍会累积，但不会归零 HP 。

---

## 脚本接口

面板背后是两个引擎方法，Hack 或测试场景可以直接调用：

!!! example "调试方法"
    - `Battle.DebugJumpWave(wave_name)` 加载指定回合并立即进入 `DEFENDING` 。返回 `ok, error_message` 。
    - `Battle.DebugEndWave()` 立即结束当前敌人回合，等价于回合自己调用 `EndWave()` 。返回布尔值。

两者在发布版中均返回 `false` ，不产生任何副作用。

---

## 战斗状态的判定

面板只在战斗中自动打开，跳转也只在对局内可用。判定分成两件独立的事。

**是否在对局中**，需要同时满足：

- `Battle.game` 与 `Battle.game.enemies` 存在，即遭遇战已经 `SetGame` ；
- 场景名包含 `battle` （不区分大小写），**或** `Battle.TIME_F` 在上一帧之后发生了变化。

第二个条件覆盖自定义命名的战斗场景。 `Battle.TIME_F` 只在 `Battle.Update` 内自增，而只有战斗场景会驱动该函数，因此它发生变化即表示对局正在运行。

`Battle` 是全局表，离开战斗后仍然存在并保留上一次的 `game` ，所以不能只凭该表是否存在来判断。

**调试入口是否可用**，单独检查 `Battle.DebugJumpWave` 与 `Battle.DebugEndWave` 是否为函数。两者分开判断的原因：前者是运行状态问题，后者是引擎版本问题，提示信息应指向不同的文件。

!!! note "面板打开期间"
    面板打开时场景暂停， `Battle.TIME_F` 不再自增，但上一帧的判定结果被保留，因此面板开着仍可跳转。

---

## 移植到其他项目

该功能由两个部分组成：

| 位置 | 作用 |
|---|---|
| `Scripts/Libraries/Engine/DevMode.lua` | 面板与按键序列 |
| `Scripts/Libraries/Battle/init.lua` 的 `DebugJumpWave` / `DebugEndWave` | 执行跳转与结束回合 |

`main.lua` 在 `_RELEASED = false` 分支中加载 `Engine.DevMode` ，并在 `update` / `draw` / `keypressed` / 鼠标 / 滚轮五处挂接。

只复制 `DevMode.lua` 而沿用旧版 `Battle` 时，面板仍能打开并列出目录树，跳转与结束回合会被拒绝，控制台与面板底部给出提示：

```
[DevMode] 此项目的 Battle 缺少 DebugJumpWave，需同步 Battle/init.lua
```

补齐目标项目 `Battle/init.lua` 中的两个方法即可。它们只依赖同文件内的 `clearWaveModule` 、 `ChangeState` 、 `narration_text` 、 `restoring_arena` 与 `waveModule` ，不需要其它改动。

---

## 已知限制

- **在 `ATTACKING` 状态下跳转**不会中止已经开始的攻击：攻击模式自己的 typer 仍留在内存里，下一次进入 `ATTACKING` 时会被重启覆盖。测试回合时通常在 `ACTIONSELECT` 或 `DEFENDING` 下操作，不会遇到该情况。
- **非战斗场景**可以打开面板查看目录树，但跳转与结束回合会被拒绝（控制台与面板底部给出提示）。
- 面板列出的是**文件**，不解算遭遇战实际引用了哪一个：一个回合是否会被正常流程走到，仍取决于遭遇战脚本的 `wave` 字段与场景里的赋值。
- 面板共用 `determination_mono.ttf` / `simsun.ttc` 13 px 字体，与战斗内小字一致；窗口缩放到很小时文字同样会很小。
