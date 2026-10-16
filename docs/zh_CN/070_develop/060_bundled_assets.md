---
title: ❕️ 内置资源一览
---

引擎根目录的 `Resources/` 同时扮演两个角色：一部分是**引擎自己会去读的默认资源**（字体、战斗 UI 骨架、约 20 段音效），另一部分是**给作者挑着用的素材库**（几千张贴图、几百段音效）。

这一页把"哪些正在被引擎用、用在哪"列清楚。想换皮、改名、清理目录，或者想知道某段音效是哪来的，先看这里。

---

## 总览

| 目录 | 文件数 | 被引擎引用 | 角色 |
|---|---:|---:|---|
| `Resources/Fonts/` | 21 | 8 | 字体。两套主力（拉丁 + CJK）撑起全部文字，另外 6 个是特化位置 |
| `Resources/Sounds/` | 271 | 约 20 | 音效。绝大多数是素材库，跑起来的集中在战斗 UI 与玩家反馈 |
| `Resources/Music/` | 9 | 3 | 音乐。只有开场、结局、GAME OVER 三处硬编码 |
| `Resources/Sprites/` | 5384 | 约 75 | 贴图。绝大部分是素材库，被引用的集中在 UI 骨架与主角色 |
| `Resources/Libs/` | 4 组 | 按需 | 原生库：`https.dll`、Discord RPC、密钥库 |

!!! note "统计口径"
    上表的"引用"是对 `Scripts/`、`Game/`、`Maps/` 以及根目录 `main.lua` / `conf.lua` 做的**字符串字面量扫描**。

    - 代码里动态拼出来的路径（动画帧号、地图数据里的音乐字段）扫不到，所以**实际用到的可能略多于表里的数字**。
    - 反过来，被引用也不等于一定会响：比如 `snd_pierce.wav` 本工程没随包发布，攻击命中帧会回退到另外两个文件。

---

## 覆盖：Game 区优先

`Game/Resources/` 是每游戏的资源根，同名文件**优先于**引擎目录：

| 引擎默认 | Game 区覆盖 |
|---|---|
| `Resources/Fonts/x.ttf` | `Game/Resources/Fonts/x.ttf` |
| `Resources/Sounds/x.wav` | `Game/Resources/Sounds/x.wav` |
| `Resources/Music/x.ogg` | `Game/Resources/Music/x.ogg` |
| `Resources/Sprites/...` | `Game/Resources/Sprites/...` |

也就是说：**想换掉引擎默认的字体或音效，不必动 `Resources/`**，往 `Game/Resources/` 放一份同名文件即可。解析规则见 [音频](../020_basic/050_audio.md) 与 [Game 区](../020_basic/110_game_area.md)。

!!! warning "别直接删 Resources/ 里的文件"
    这页列的是"当前没被引用"的素材，不等于"没人要"。它们是给作者取用的素材库；需要清理目录时，先确认工程没有在 `Game/` 里引用它们。

---

## Fonts：21 个字体，8 个在跑

!!! example "两套主力"
    - **拉丁**：`determination_mono.ttf`，size **27**（对话/标题）或 **13**（正文/调试面板）。
    - **CJK**：`simsun.ttc`，size **只 13**；要 27 号效果时用 `scale = 2` 放大。

    二者通过 InstText 的 bondfont 组合，按字节自动分流中英文，所以中英混排不需要手动切换字体。见 [打字机](../020_basic/030_typers.md) 与 [GUI](../020_basic/160_gui.md)。

### 正在使用

| 字体 | 用在哪 | 参数 | 引用位置 |
|---|---|---|---|
| `determination_mono.ttf` | Typers 四个实现（etext / ntext / stext / insttext）的默认英文字体；GUI 库；DevTool / Debugger 面板；命名、锁定、logo、缓动编辑器等场景 | 27 / 13 / 9 视位置而定 | `Scripts/Libraries/Typers/`、`Scripts/Libraries/GUI/primitives.lua`、`Scripts/Libraries/Engine/DevTool.lua`、`Scripts/Scenes/` 多个场景 |
| `simsun.ttc` | Typers 与战斗 UI 的 CJK 部分；虚拟键盘的中文键位 | 13（27 用 `scale = 2`） | 同上 + `Scripts/Libraries/Controller/VirtualKeyboard.lua` |
| `Mars Needs Cunnilingus.ttf` | 战斗底部状态栏的文字：名字、`LV`、HP 数值 | 24（等宽，1 字符 = 15 px） | `Scripts/Libraries/Battle/UI/init.lua` |
| `8bit-wonder.TTF` | 战斗底部状态栏里的 `HP` / `KR` 小标签 | 12 | `Scripts/Libraries/Battle/UI/init.lua` |
| `DAMAGEBACK.TTF` | 弹跳文字的**黑色描边底层**（伤害数字、MISS） | 32 | `Scripts/Libraries/Battle/UI/init.lua` |
| `Hachicro.ttf` | 弹跳文字的**彩色上层**（伤害=红，MISS=白）叠在黑底上形成描边 | 32 | `Scripts/Libraries/Battle/UI/init.lua` |
| `Crypt Of Tomorrow.ttf` | Overworld 商店的文本指针、状态页（STAT）文字 | 由调用处设定 | `Scripts/Libraries/Overworld/shop.lua`、`Scripts/Libraries/Overworld/stat.lua` |
| `Wingdings.ttf` | 只在示例对话与测试场景里以 `[font:Wingdings.ttf]` 标签出现 | 沿用当前字号 | `Scripts/Scenes/Overworld/scene_ow_main_0.lua`、`Scripts/Scenes/TEST/scene_wingdings.lua` |

`conf.lua` 还用 `determination_mono.ttf` 造了 LÖVE 自己的默认字体（13 / 20），也就是**报错画面和控制台**用的那套。

### 备用（当前未接线）

这些字体随包分发但没有被任何代码引用，可直接取用：

`Buttons.otf`、`Comic Sans.ttf`、`Determination.otf`、`MonsterFriend.otf`、`MonsterFriendFore.otf`、`Papyrus.ttf`、`speechbubble.ttf`、`undertale-wingdings.ttf`、`unifont_jp.otf`、`方正像素12.ttf`、`方正卡通简体.ttf`、`方正基础像素体.ttf`、`方正少儿简体.ttf`

!!! tip "替换字体的三种方式"
    三种方式的改动范围依次增大：

    1. 一句话内换：对话里写 `[font:你的字体.ttf]`（只对这一句之后生效）。
    2. 全局替换默认：往 `Game/Resources/Fonts/` 放同名文件覆盖 `determination_mono.ttf` / `simsun.ttc`。
    3. 代码里指定：`Fonts.New("名字.ttf", 字号, "mono")`，或给 InstText 配 `bondfont`。

---

## Sounds：271 段，约 20 段在跑

### 战斗菜单与 UI

| 文件 | 什么时候响 | 引用位置 |
|---|---|---|
| `snd_menu_0.wav` | 战斗按钮之间移动光标、菜单切换（用得最多的一段，二十多处） | `Battle/UI/buttons.lua`、`Battle/UI/stateinner.lua`、`Overworld/shop.lua` |
| `snd_menu_1.wav` | 战斗菜单的确认/返回一类动作、商店确认 | `Battle/UI/stateinner.lua`、`Overworld/shop.lua` |

### 玩家与灵魂

| 文件 | 什么时候响 | 引用位置 |
|---|---|---|
| `snd_ding.wav` | 切换灵魂、追加灵魂成功时（带 `use_sound` 参数） | `Battle/Player/init.lua` |
| `snd_heal.wav` | 回血（`Player.Heal` 正数、Overworld 的回血点） | `Battle/Player/init.lua`、`Overworld/init.lua` |
| `snd_phurt.wav` | 玩家受伤（`Player.Hurt` 正数）、蓝色灵魂受击 | `Battle/Player/init.lua`、`Battle/Player/Souls/blue.lua`、`Battle/UI/stateinner.lua` |
| `snd_slam.wav` | 蓝色灵魂砸地 | `Battle/Player/Souls/blue.lua`（`Game/Souls/blue.lua` 同样一份） |
| `snd_shoot.wav` | 黄色灵魂射击 | `Battle/Player/Souls/yellow.lua` |
| `snd_heartbreak_0.wav` | GAME OVER 心碎（第一段） | `Scripts/Scenes/scene_gameover.lua` |
| `snd_heartbreak_1.wav` | GAME OVER 心碎（第二段） | `Scripts/Scenes/scene_gameover.lua` |

### 玩家攻击

| 文件 | 什么时候响 | 引用位置 |
|---|---|---|
| `snd_slice.wav` | 挥砍起手 | `Battle/PlayerAttacks/stick.lua` |
| `snd_damage.wav` | 攻击命中敌人 | `Battle/PlayerAttacks/stick.lua` |

### 敌方攻击

| 文件 | 什么时候响 | 引用位置 |
|---|---|---|
| `snd_warning_0.wav` | 骨头攻击的预警闪烁（交替两声：红 / 黄） | `Attacks/Bones.lua` |
| `snd_warning_1.wav` | 同上，另一声 | `Attacks/Bones.lua` |
| `snd_spearappear.wav` | `snd_pierce.wav` 的替补（本工程没随包发 `snd_pierce.wav`，命中帧回退到这里） | `Attacks/Bones.lua` |
| `snd_lazer.wav` | 同上，替补名单里的第二个 | `Attacks/Bones.lua` |
| `Blaster/snd_intro.wav` | 加农炮出场 / 蓄力 | `Attacks/Blasters.lua`（路径由 `sounds_path` 解析） |
| `Blaster/snd_fire.wav` | 加农炮开火 | `Attacks/Blasters.lua` |

### Overworld 与场景

| 文件 | 什么时候响 | 引用位置 |
|---|---|---|
| `snd_encounter.wav` | 触发遇敌 | `Overworld/init.lua` |
| `snd_encounter_fall.wav` | 遇敌转场的下坠 | `Overworld/init.lua` |
| `snd_tong.wav` | 遇敌转场的一声 | `Overworld/init.lua` |
| `snd_save.wav` | 存档成功 | `Overworld/Pages/save.lua` |
| `snd_buyitem.wav` | 商店购买 | `Overworld/shop.lua` |
| `snd_flee.wav` | 逃跑 / 战斗收尾（三个战斗场景模板都用了） | `Scripts/Scenes/Battle/` 的 init / ow / template |
| `snd_dust.wav` | sprite 生成尘土粒子时 | `Sprites.lua` |
| `snd_intro.ogg` | 启动 logo 场景 | `Scripts/Scenes/scene_logo.lua` |

### 打字机语音

| 文件 | 什么时候响 | 引用位置 |
|---|---|---|
| `Voices/v_monster.wav` | 打字机的**默认**语音：每敲一个字符随机取一次 | `Typers/etext.lua`、`Typers/ntext.lua`、`Typers/stext.lua` |

`Voices/` 下其余 40 个（`v_sans.wav`、`v_papyrus.wav`、`v_flowey.wav`……）都能用，只是**没有默认值指向它们**：用 `[voice:xxx]` 标签或 `setVoices({...})` 指定即可。

### 子目录说明

| 目录 | 内容 | 状态 |
|---|---|---|
| `Sounds/Blaster/` | 加农炮专用 3 段。Blasters 库先试 `Blaster/<流派名>/snd_intro.wav`，找不到就用扁平布局 `Blaster/` | 2 段在用，`snd_intro_2.wav` 闲置 |
| `Sounds/Soul Library Sounds/` | 5 段，其中 3 段与根目录同名（`snd_ding` / `snd_fire` / `snd_intro`） | 路径解析走根目录的副本，这里没被直接引用 |
| `Sounds/Voices/` | 41 段打字音 | 只有 `v_monster.wav` 是默认值 |
| `Sounds/Beats/` | 节拍器 2 段 | 未接线（`Beat.lua` 是独立库，需要自己加载并每帧驱动） |
| `Sounds/Weather/` | 雨声 2 段 | 未接线 |

### 未启用

其余约 250 段（`snd_attack_*`、`snd_hurt_*`、`snd_monster_hurt_*`、`snd_mtt*`、各种 `mus_*` 短音……）当前没有任何代码引用，纯粹是素材库。

---

## Music：9 首，3 首在跑

| 文件 | 用在哪 | 引用位置 |
|---|---|---|
| `Start.ogg` | Overworld 默认 BGM（`ow.SetMusic`） | `Scripts/Scenes/Overworld/scene_ow_main_0.lua`、`scene_sol.lua` |
| `End.ogg` | 结局场景 | `Scripts/Scenes/scene_end.lua` |
| `mus_gameover.ogg` | GAME OVER | `Scripts/Scenes/scene_gameover.lua` |

未启用：`mus_house1.ogg`、`mus_mysteriousroom2.ogg`、`mus_options_fall.ogg`、`mus_options_summer.ogg`、`mus_options_winter.ogg`、`Weather/mus_rain.ogg`。地图自带的 BGM 由地图数据指定，不在这份硬编码清单里。

---

## Sprites：5384 张，约 75 张在跑

| 目录 | 被引用 | 总数 | 被引用的部分 |
|---|---:|---:|---|
| `UI/` | 22 | 230 | 战斗按钮（FIGHT / ACT / ITEM / MERCY）、目标准星、挥砍特效、心碎碎片、GAME OVER 背景 |
| `Overworld/` | 14 | 1344 | 主角四向行走帧、感叹号提示 |
| `Scene/` | 13 | 1550 | 存档点、宝箱、告示牌、真实验室显示器、瀑布星纹 |
| `Characters/` | 7 | 1576 | Loox、Migosp 的待机与受伤帧（示例敌人） |
| `Soul Library Sprites/` | 7 | 33 | 默认心形、心碎、子弹形态、蓝色平台 |
| `Attacks/` | 4 | 589 | Papyrus / Sans 的骨头弹幕贴图 |
| `Bubble/` | 2 | 2 | 对话框气泡的圆角与尾巴 |
| `Shapes/` | 1 | 3 | 圆形（绘制用） |
| 根目录散图 | 5 | 8 | `px.png`（1×1 像素，血条/矩形全靠它）、`bullet.png`、`heart.png`、`poseur.png`、`Logo.png` |
| 其余目录 | 0 | 约 700 | `Background/`、`Border/`、`Cutscene/`、`Mascots/` 等，纯素材 |

??? note "完整清单（75 项）"
    ```text
    Logo.png  bullet.png  heart.png  poseur.png  px.png

    Attacks/Papyrus/spr_bonebottom_0.png      Attacks/Papyrus/spr_bonetop_0.png
    Attacks/Sans/spr_s_bonebul_bottom_0.png   Attacks/Sans/spr_s_bonebul_top_0.png

    Bubble/spr_bubblecorner.png               Bubble/spr_bubbletail.png

    Characters/Ruins/spr_loox_0..2.png        Characters/Ruins/spr_looxhurt_0.png
    Characters/Ruins/spr_migosp_0..1.png      Characters/Ruins/spr_migosphurt_0.png

    Overworld/spr_exc.png                     Overworld/spr_exc_f.png
    Overworld/Frisk/spr_f_maincharad_0..3.png
    Overworld/Frisk/spr_f_maincharal_0..1.png
    Overworld/Frisk/spr_f_maincharar_0..1.png
    Overworld/Frisk/spr_f_maincharau_0..3.png

    Scene/Everywhere/spr_chestbox_0.png       Scene/Everywhere/spr_savepoint_0..1.png
    Scene/Everywhere/spr_sign.png
    Scene/True Lab/spr_monitor_dark_0.png     Scene/True Lab/spr_monitor_lit_0..3.png
    Scene/Waterfall/spr_starpattern_0..3.png

    Shapes/circle.png

    Soul Library Sprites/platform.png         Soul Library Sprites/platformline.png
    Soul Library Sprites/spr_default_heart.png
    Soul Library Sprites/spr_heartbreak_0.png
    Soul Library Sprites/spr_heartbullet_1.png
    Soul Library Sprites/spr_heartgtfo_0..1.png

    UI/Battle Screen/spr_actbt_center_0..1.png     UI/Battle Screen/spr_fightbt_0..1.png
    UI/Battle Screen/spr_itembt_0..1.png           UI/Battle Screen/spr_sparebt_0..1.png
    UI/Battle Screen/spr_target_0.png              UI/Battle Screen/spr_gameoverbg_0.png
    UI/Battle Screen/Player Attack/spr_slice_o_0..5.png
    UI/Battle Screen/Player Attack/spr_targetchoice_0..1.png
    UI/Battle Screen/Shards/spr_heartshards_0..3.png
    ```

!!! tip "换皮的入口在 Game 区"
    敌人立绘、背景、弹幕贴图这类内容资源放在 `Game/Resources/Sprites/` ，用 `Sprites.CreateSprite` 按路径取，不改动 `Resources/Sprites/` 。只有需要整体替换引擎默认外观（比如战斗按钮）时才用同名覆盖。

---

## Libs：原生库

| 路径 | 谁在用 | 说明 |
|---|---|---|
| `Resources/Libs/https.dll` | `GamejoltAPI.lua`（`require("https")`） | lua-https，GameJolt 联网必需；缺失时联网功能会给出明确报错而非崩溃 |
| `Resources/Libs/DiscordRPC/discord-rpc-x64.dll`、`-x86.dll` | `DiscordRPC.lua` | Discord 富文本状态 |
| `Resources/Libs/DiscordGameSDK/x64/`、`x86/` | 未被加载 | 旧版 Game SDK 的备选，源码里有注释解释为什么改用上面的 RPC |
| `Resources/Libs/Secrets/secrets.dll` | `Utils/Secrets.lua` | 密钥库，见 [密钥原生库](./050_secrets.md) |

!!! warning "Android 上的 .so"
    原生库**不能**塞在 `game.love` 里加载，Android 需要放进 `app/src/main/jniLibs/<abi>/`。细节见 [密钥原生库](./050_secrets.md) 与 [导出](../100_export/index.md)。

---

## 想自己核一遍

上面所有数字都来自静态扫描，代码改动后统计结果会变化。两条命令可以在自己的工程里重跑：

```bash
# 某个资源被谁引用
grep -rn "determination_mono" Scripts Game

# 列出所有硬编码音效，按出现次数排序
grep -rn "PlaySound(" Scripts | grep -o '"[^"]*"' | sort | uniq -c | sort -rn
```

`SE.Preload` 只遍历 `Game/Resources/`，不碰主 `Resources/` —— 因为主目录里几千个文件全跑一遍会卡几十秒。想在加载界面预热自己的资源，见 [资源预加载](./040_preload.md)。
