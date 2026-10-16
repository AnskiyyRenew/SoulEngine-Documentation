---
title: 商店
---

商店是**一个独立的场景**，不是叠在主世界上的页面。玩家走到商店门口时切场景进去，出来时切回 `DATA.room` 。

主体模块： `Scripts/Libraries/Overworld/shop.lua` ，用 `ImportFile("Overworld.shop")` 取用。<br>
场景： `Scripts/Scenes/Overworld/Shops/scene_shop_0.lua` ，场景名 `Overworld.Shops.scene_shop_0` 。

---

## 一个完整的商店场景

```lua
local scene = {}
local shop = ImportFile("Overworld.shop")

-- 进门时说的话，以及选"离开"时说的那句
shop.SetMainText("* 哇咔咔咔。\n* 补牙补牙补牙。")
shop.SetEndText("* 下次再来哦。")

-- 货架：填物品 id，会在 ITEMS 里查名字
shop.SetGoods({"CrabApple", "HotCat"})
shop.SetAmount("CrabApple", 4)              -- 不写（或传 nil）= 无限库存
shop.SetBuyPrice("CrabApple", 7)
shop.SetBuyPrice("HotCat", 18)

-- 右侧两栏：店主的评价 + 会滑上来的简介面板
shop.SetBuyOpinion("CrabApple", "I\nmade\nthis.")
shop.SetIntroduction("CrabApple", "+20 HP")

-- 卖价不写 = 买价的一半（HotCat 未设卖价 → 9G）
shop.SetSellPrice("CrabApple", 3)

-- 拒收台词：卖价为 0 的东西被选中时播这句，而不是成交
shop.SetCannotSellText("* 我这里废品已经够多了。")          -- 全店默认
shop.SetCannotSellText("Stick", "* 如果我的店里都是木棍和绷带，\n  那我也不用开商店了。")

-- 交谈话题：列表里一行一个
shop.AddTalk("天气", {"* 今天也一如既往。", "* 明天大概也一样。"})
shop.AddTalk("时间", "* 地下没有白天和黑夜。\n* 所以时间只是个概念。")
shop.SetQueue("天气", "时间")   -- 绑成一条队列，只显示其中一个

-- 背景
local bg = shop.GetBackground()
bg:Scale(2, 2)
bg:SetAnimation({
    "Scene/Waterfall/spr_starpattern_0.png",
    "Scene/Waterfall/spr_starpattern_1.png",
}, 0.1)

function scene.update(dt)
    shop.Update(dt)
end

function scene.draw()
end

function scene.clear()
    shop.Clear()
    Layers.clear()
end

return scene
```

!!! danger "`scene.clear` 两行都要写，而且顺序不能反"
    `shop.Clear()` 做两件事：先给主文本框和评价栏的 `_onComplete` 置 `nil` ，再 `ClearModuleTree("Scripts.Libraries.Overworld.shop")` 把模块从 require 缓存里卸掉。

    顺序是这样来的： `Layers.clear()` 内部会先调 `Typers.ClearAll()` ，把每个打字机 `Destroy()` 掉，而 `Destroy()` 会触发 `_onComplete` 。不先 `shop.Clear()` 的话，退出商店时那个回调会在半死的对象上重新进商店逻辑。

    模块也**必须**卸掉：离开时 `shop._leaving` 被置成 `true` ，而 `shop.Update` 的第一行就是 `if (shop._leaving) then return end` 。模块留在缓存里的话，**第二次进店会完全不响应输入**。

![OW-09](../img/040_overworld/ow_09_shop.png)

---

## 界面与状态机

商店有四个动作，由玩家用灵魂选择：

| 动作 | 说明 |
|---|---|
| `Buy` | 打开**货架**，确认键按 `SetBuyPrice` 的价格扣钱 |
| `Sell` | 打开**自己的背包**，确认键按 `SetSellPrice` 的价格加钱 |
| `Talk` | 打开**话题列表**，确认键读那一条话题 |
| `Exit` | 离开，说完 `SetEndText` 后淡出回 `DATA.room` |

!!! warning "`Talk` 显示的不是 `SetMainText`"
    `SetMainText` 是**待机时**（光标停在四个按钮上）显示在下方文本框里的问候语。<br>
    `Talk` 打开的是话题列表，选中的话题正文会**临时占用**同一个文本框显示。

选 `Buy` / `Sell` / `Talk` 之后，列表占左边一栏（每页 5 行，可滚动），光标是一颗红色灵魂。<br>
`Buy` / `Sell` 时右侧会同时显示店主的评价和会滑上来的简介面板； `Talk` 时右侧两栏清空。

三个动作在**没有可显示内容**时会被拦截，播放一句话后退回待机：

| 情况 | 触发条件 | 说的话（本地化键） |
|---|---|---|
| 本店不收东西 | `SetSellable(false)` | `Overworld.Shop.Text.NoSelling` |
| 背包是空的 | `DATA.player.items` 为空 | `Overworld.Shop.Text.NoItems` |
| 没有话题 | 一个 `AddTalk` 都没调 | `Overworld.Shop.Text.NoTalk` |

### 状态机

`IDLE → BUY / SELL / TALK` ，外加两个**瞬态**——它们把整个屏幕（和确认键）交给主文本框：

| 状态 | 说明 | 结束后去哪 |
|---|---|---|
| `IDLE` | 四个按钮，光标是一颗灵魂 | — |
| `BUY` / `SELL` / `TALK` | 列表状态 | 按取消键回 `IDLE` |
| `MESSAGE` | 一条阻塞性消息（金钱不够、物品栏已满、话题正文、拒收台词） | 回到进入该状态前的那个状态 |
| `EXITING` | 离开时的告别语 | 说完置 `_leaving` ，黑幕拉起切回 `DATA.room` |

!!! tip "该帧锁的作用"
    `Typers.Update` 跑在 `scene.update` **之前**，因此读完消息的那一次确认键在同一帧里还会被 `shop.Update` 再读到一次。<br>
    不加锁时，关闭消息的那一次按键会立即重新打开列表。代码中的 `input_lock` 用于避免该情况。

### 键位

| 键 | 待机 | 列表里 |
|---|---|---|
| `confirm` | 进入选中的动作 / 离开 | 成交、读话题、读拒收台词 |
| `cancel` | — | 退回待机 |
| `up` / `down` | 在四个按钮间移动 | 在列表里移动（到底部会滚动） |

---

## 方法一览

!!! example "文本"
    - `shop.SetMainText(text)` 设置待机时显示的那段话。字符串或字符串数组都行。
    - `shop.GetMainText()` 读回来（**永远是数组**，内部已经归一化）。
    - `shop.SetEndText(text)` 设置离开时说的话。
    - `shop.GetEndText()` 读回来。默认取本地化 `Overworld.Shop.Text.Leave` 。

!!! example "货架与库存"
    - `shop.SetGoods(list)` 整份替换货架。
        - `list` 物品 **id 字符串**数组，例如 `{"CrabApple", "HotCat"}` 。
        - id 在 `ITEMS` 里查不到会被跳过，并打印一句 `[Shop] Unknown item id: xxx` 。
        - 名称在**加入货架时**从 `ITEMS` 读取，之后修改 `ITEMS` 不影响已在架上的商品。
    - `shop.AddGoods(id)` 往货架末尾加一件。
    - `shop.RemoveGoods(index)` 按序号移除一件。
    - `shop.GetGoods()` 读回货架（ `{id, name}` 的数组）。
    - `shop.SetAmount(id, amount)` 设置库存。
        - `amount` 传 `nil` = **无限库存**（默认）；传数字会被夹到 `>= 0` 。
    - `shop.GetAmount(id)` 读库存，无限时返回 `math.huge` 。
    - `shop.IsSoldOut(id)` 库存是不是 `<= 0` 。
        - 售罄的商品留在货架上，但行尾会多一个 `Overworld.Shop.Text.SoldOut`（`已售罄`），选中它按确认只播放音效，不扣钱。

!!! example "价格"
    - `shop.SetBuyPrice(id, price)` 设置买入价。
    - `shop.GetBuyPrice(id)` 读买入价，没设过返回 `0` 。
    - `shop.SetSellPrice(id, price)` 设置卖出价。
    - `shop.GetSellPrice(id)` 读卖出价。**没设过时返回买入价的一半（向下取整）**，不是 `0` ：

    ```lua
    shop.SetBuyPrice("CrabApple", 7)   -- 没调 SetSellPrice
    print(shop.GetSellPrice("CrabApple"))   -- 3
    ```

!!! warning "卖价为 0 表示该物品不收购"
    选中卖价为 `0` 的物品按确认，不会成交，而是播放一句拒收台词（见下）。<br>
    将卖价设为 `0` 即可表示该物品不收购（不设置买价时，半价的计算结果同样为 `0` ）。<br>
    未调用过 `SetBuyPrice` 的商品，`GetSellPrice` 同样返回 `0` ，即未设置买价的商品无法卖出。

!!! example "评价与简介"
    - `shop.SetBuyOpinion(id, opinion)` 设置买入时右侧显示的评价。
    - `shop.GetBuyOpinion(id)` 读回来，没设过时取本地化 `Overworld.Shop.Opinion.Default`（`……`）。
    - `shop.SetSellOpinion(id, opinion)` 设置卖出时的评价。
    - `shop.GetSellOpinion(id)` 读回来，缺省同上。
    - `shop.GetOpinion(id)` 按**当前开着哪个列表**自动选：`SELL` 页读卖出那份、`TALK` 页读话题旁白那份，其余读买入那份。
    - `shop.SetIntroduction(id, text)` 设置会滑上来的简介面板里的短说明。
    - `shop.SetIntroductions(map)` 批量： `SetIntroductions({CrabApple = "+20 HP", HotCat = "+12 HP"})` 。
    - `shop.GetIntroduction(id)` 读回来，没设过返回空串 `""` 。

!!! warning "评价文字不要写成对白的格式"
    右栏的评价和简介面板都是**面板文字**，不是对白。以星号加空格开头的话， `EText` 会做两空格的悬挂缩进，正好把字挤出右栏。<br>
    主文本框里的话题正文、拒收台词仍然要带星号——那是真的对白。

!!! example "出售开关与拒收台词"
    - `shop.SetSellable(value)` 本店是否收购物品，默认 `true` 。设为 `false` 后选 `Sell` 只播放一句话，不打开列表。
    - `shop.IsSellable()` 读回来。
    - `shop.SetNoSellText(text)` 「本店什么都不收」那句话（ `SetSellable(false)` 时用）。
    - `shop.SetCannotSellText(id, text)` 设置**单件**物品被拒收时的台词。 `text` 写表就是多段，一次确认推进一段。
    - `shop.SetCannotSellText(text)` 只传一个参数 = 设置**全店默认**的拒收台词。
    - `shop.GetCannotSellText(id)` 解析后的结果。**表进表出**：设的是多段，读出来也是多段。
    - `shop.SetCannotSellTexts(map)` 批量： `SetCannotSellTexts({Stick = "...", Bandage = {"...", "..."}})` 。
    - `shop.GetCannotSellTexts()` 读回那张单件表。
    - `shop.ClearCannotSellTexts()` 清除所有单件台词（全店默认那句保留）。

    台词里的 `%s` 会替换成物品名：

    ```lua
    shop.SetCannotSellText("Bandage", {"* 我可不需要%s。", "* 拿走拿走。"})
    ```

    解析顺序是 **单件 → 全店默认 → 本地化** `Overworld.Shop.Text.CannotSell`（`* 这个我不收。`）。

!!! tip "台词中出现裸 `%` 的处理"
    文案为手写内容，`formatRefusal` 会将 `string.format` 包在 `pcall` 中。格式串无效时按原样显示，不影响商店运行。

!!! example "钱与杂项"
    - `shop.GetGold()` 读金币。
    - `shop.SetGold(value)` 写金币。
    - `shop.SetMaxItems(count)` 背包上限，默认 `8` 。买、卖和那个 `n/8` 读数**共用**这一个值。
    - `shop.GetMaxItems()` 读回来。
    - `shop.Refresh()` 重画金钱/背包读数；正开着列表的话连列表一起重建。
    - `shop.GetPlayer()` 返回商店里那颗红色灵魂贴图。
    - `shop.GetBackground()` 返回背景贴图对象，可对其调用 `Scale` / `SetAnimation` 。
    - `shop.Update(dt)` 每帧调用，处理输入与演出。
    - `shop.Clear()` 见上面那条 danger。

!!! example "文本框宽度"
    - `shop.SetMainTextWidth(width)` 主文本框宽度（问候语、拒收台词、话题正文）。默认 `560`（面板 `x=40..600`）。
    - `shop.SetOpinionWidth(width)` 右栏评价的宽度。默认 `170`（`x=460..630`）。
    - `shop.SetIntroWidth(width)` 简介面板的宽度。默认 `182`（`x=448..630`）。
    - `shop.SetTextWidths(main, opinion, intro)` 三个一起设，传 `nil` 的那项保持不变。
    - `shop.SetAutoWrap(enabled)` 自动换行总开关，默认**开**。关掉之后只认手写的 `\n` 。
    - `shop.IsAutoWrap()` 读回来。

    修改宽度后，引擎会重新排列三块面板—— `EText` 在打字过程中读取 `size` ， `InstText` 为预渲染，因此需要 `Rebuild()` 。

---

## 交谈话题与队列

话题**永远是一条可浏览的列表**，选中按确认就读。正文可以是一句话，也可以是数组（一次确认推进一段）：

```lua
shop.AddTalk("天气", "* 今天也一如既往。")
shop.AddTalk("时间", {"* 地下没有白天。", "* 所以时间只是个概念。"})
```

!!! example "话题方法"
    - `shop.AddTalk(topic, text)` 加一条，返回新的条数。
        - 也可以只传一个表： `AddTalk({"时间", "* 地下没有白天。"})` 或 `AddTalk({topic = "时间", texts = {...}})` 。
    - `shop.SetTalks(list)` 整份替换。传数组（每条是一个 entry）或 `话题名 = 正文` 的映射表都行。
    - `shop.RemoveTalk(index)` 按序号删。
    - `shop.ClearTalks()` 全删。
    - `shop.GetTalks()` 读回原始表（**没有**折叠队列，顺序就是 `AddTalk` 的顺序）。

### 队列：把几个话题合并为一行

`SetQueue` 把几个话题绑成一条队列，**同时只显示其中一个**——对话走到哪儿就显示哪个。读完当前的，揭示下一个；全读完了再绕回第一个。

```lua
shop.SetQueue("天气", "时间")        -- 两者只显示其中一个
shop.SetQueue({"天气", "时间"})      -- 同上
shop.SetQueue(1, 2)                  -- 也可以给 AddTalk 的顺序号
```

成员用**话题名**或 **1-based 序号**指定，且为**惰性解析**——`SetQueue` 写在 `AddTalk` 之前或之后均可。每调用一次添加一条队列，因此一家商店可以有多条互不相关的队列；**不属于任何队列的话题始终显示**。

!!! example "队列方法"
    - `shop.SetQueue(...)` 加一条队列，返回新的条数。
    - `shop.SetQueues(list)` 整份替换： `SetQueues({{"天气", "时间"}, {"出口", "秘密"}})` 。
    - `shop.ClearQueues()` 清空。
    - `shop.GetQueues()` 读回原始表。
    - `shop.GetVisibleTalks()` 读**此刻列表上真实显示的行**，队列已经折叠过了：

    ```lua
    -- {{topic = "天气", texts = {...}, seen = 0, is_new = false}, ...}
    ```

### 「（新）」的出现条件

这里有两个**容易混淆**的判断，代码中对应两个不同的函数：

| 谓词 | 内部字段 | 含义 |
|---|---|---|
| 未读 | `seen <= 0` | 决定队列**当前显示哪个**成员 |
| 带标记 | `fresh == true` | 决定行尾加不加「（新）」 |

关键是：**「（新）」表示队列刚翻页显示出的成员，不表示未读**。

- **进店时所有话题都不带标记**——即使从未读过。
- 只有队列**前移**、揭示出一个**还没读过**的成员时，才把那个成员标上「（新）」。
- 一旦读完，标记立刻清除。所以队列走完一轮之后，就不会再有「（新）」了。
- **不在任何队列里的话题永远不会自己带上标记**，要手动调 `SetTalkNew` 。

标记的样子是行尾加一句本地化 `Overworld.Shop.Text.New`（`（新）`），整行染成 `new_color`（默认 UNDERTALE 黄）。

!!! example "进度与标记方法"
    - `shop.IsTalkNew(index)` 当前带不带「（新）」。
    - `shop.SetTalkNew(index, value)` 手动开关「（新）」。话题在队列外时用这个。
    - `shop.IsTalkUnread(index)` 是否从未读过。
    - `shop.SetTalkSeen(index, seen)` 标记为已读（`true`）/ 未读（`false`），同时清除「（新）」。
        - 置为未读会让该成员**移到队列最前面**，该行为用于从存档恢复对话进度。
    - `shop.ResetTalkProgress()` 全部话题回到未读，每条队列的指针也回到第一个。
    - `shop.SetNewColor(r, g, b)` 改「（新）」的颜色。

    上面这些方法的 `index` 都接受**话题名**或 **1-based 序号**。

### 右栏的话题旁白

打开话题列表时，右侧那一栏显示的不是话题列表，而是**店主对当前光标所在话题的评价**。

它有一条三级解析链：**单话题 → 全店默认 → 本地化** `Overworld.Shop.TalkOpinion.Default` 。

```lua
shop.SetTalkOpinion("想聊点什么？")          -- 只给一个参数 = 全店默认
shop.SetTalkOpinion("天气", "又聊天气？")     -- 给两个参数 = 单独设置某个话题
```

!!! example "话题旁白方法"
    - `shop.SetTalkOpinion(topic, opinion)` 只给一个参数时设置**全店默认**；给两个时设置某个话题的。
    - `shop.GetTalkOpinion(topic)` 读解析后的结果。 `topic` 传 `nil` 就是走全店默认那一层。
    - `shop.SetTalkOpinions(map)` 批量： `SetTalkOpinions({天气 = "又聊天气？", 时间 = "……"})` 。
    - `shop.GetTalkOpinions()` 读回单话题那张表（不含全店默认）。
    - `shop.ClearTalkOpinions()` 清掉所有单话题旁白，全店默认那句留着。

!!! warning "让某个话题回到默认值时不能传 `nil`"
    `SetTalkOpinion("天气", nil)` 不会被当作清除该话题的旁白——参数少一个时会走**一个参数**的分支，
    把**全店默认**设为字符串 `"天气"` 。清除单个话题只能使用 `ClearTalkOpinions()` 全部清除。

!!! tip "旁白里的 `%s` 会替换为话题名"
    与拒收台词相同，由 `fillName` 处理：文案中的 `%s` 替换为当前话题名，且 `string.format` 被 `pcall` 包裹，
    因此文案中出现裸 `%` 时按原样显示，不影响商店运行。

!!! warning "旁白不要写成对白的格式"
    它是**面板文字**，不要以 `* ` 开头—— `EText` 会对星号做悬挂缩进，正好把字挤出右栏。<br>
    主文本框里的话题正文仍然要带星号，那是真的对白。

!!! note "话题正文播放时右栏会被收走"
    选中话题、正文开始打字之后，`hideElements()` 会把右栏一起清掉；回到列表时旁白才按光标位置重新出现。

!!! tip "队列指针的选取规则"
    一条队列的当前成员按以下顺序选取：**先取第一个未读的**；不存在未读成员时，才按 `cursor` 轮转。因此中途向队列插入一个新话题后，该话题会立即显示。

!!! warning "队列不支持模式开关"
    交谈只支持**列表**这一种形态，队列只决定哪些行显示。<br>
    将菜单第三项改为话题名属于另一套交互，与队列无关。

---

## 钱与背包

商店直接读写 `DATA.player.gold` 与 `DATA.player.items` ，所以：

- 背包上限是 `shop.max_items`（默认 8），满了买不进去（界面上会显示 `n/8` ）。
- 钱不够时买不了，会弹一句 `Overworld.Shop.Text.NoGold` 。
- 交易结果**立刻写进 `DATA`** ，存档时会一起带走。

成交时的附带操作：买 → `snd_buyitem.wav` ，库存减一；卖 → `snd_buyitem.wav` ，从 `items` 里 `table.remove` 。<br>
买/卖完成后，右栏会换成一句结算文案（ `Overworld.Shop.Text.Bought` / `Text.Sold` ，都带 `%s` 占位）。

---

## 进入商店

商店只是一个普通场景，从主世界调 `Overworld.ChangeScene` 切进去即可：

```lua
if (ow.getInteractResult("warp", 1)) then
    ow.ChangeScene("Overworld.Shops.scene_shop_0")
end
```

`ChangeScene(scene, mark, direction)` 的另外两个参数都有默认值（`mark = 1` 、 `direction = "down"`）。它会**先检查 `Char.controlling`** ，玩家不受控时直接 return，然后记下 `DATA.room = Scenes.name_current` 。<br>
离开时商店自己会 `Scenes.switchTo(DATA.room)` 回原场景，不需要额外处理。

!!! tip "替换整家商店无需修改引擎代码"
    场景名 `Overworld.Shops.scene_shop_0` 会依次到 `Game.Scenes.` 和 `Scripts.Scenes.` 两个根查找，**Game 区优先**。<br>
    修改自带商店时，将 `scene_shop_0.lua` 复制一份到 `Game/Scenes/Overworld/Shops/` 并修改即可，引擎自带的文件保持不变。
