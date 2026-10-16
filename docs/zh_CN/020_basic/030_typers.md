---
title: ❕️ 打字机
---

打字机位置： `Scripts/Libraries/Typers/` 文件夹。

打字机一共分为四种： `InstText` 只负责把整段文字直接画出来，剩下三种 `EText` / `NText` / `SText` 都可以正常逐个打字。

屏幕上所有文本均可通过打字机绘制，其他绘制方式见下一页。

---

## 创建打字机

三种**逐字打字**的打字机按标签的处理方式区分，分别是 `EText` 、 `NText` 和 `SText` 。

第四种 `InstText` 不带打字动画，用法和它们差别较大，单独放在本节最后。

---

### EText 打字机

`EText` 全称 `Easy Text` ，特点是样式写在文本中，类似于 `bbcode` 。

使用 `Typers.EText.New(text, position, layer, size, mode)` 来创建一个 `etext` 模式的打字机。

- `text` 要打的文本，可以使用字符串或表，若使用表则会将文本分开为可翻页类型。
- `position` 打字机第一个字符所处的位置。
- `layer` 打字机的图层。
- `size` 打字机有显示的对话框的大小。
- `mode` 打字机的模式： `manual` 手动切换到下一句、 `none` 无法手动干预，仅通过代码切换到下一句。若创建时没有给出参数，默认为 `manual` 模式。

!!! example "创建示例"

    ```lua
    local t = Typers.EText.New({"这是第一句话", "这是第二句话"}, {320, 240}, 0)
    ```

**修改样式：**

通过在句子中添加带方括号 `[]` 的标签来设置样式。

!!! example "使用案例"

    ```lua
    local t = Typers.EText.New({"[colorHEX:ff0000]这是一句红色的话。"}, {320, 240}, 0)
    ```

??? example "所有标签"
    - `[wait:x]` 让打字机等待 `x` 秒，只允许直接输入数字，不允许输入算式例如 `1 / 2` 。
        - 等待使用**独立的计时器**，后续出现的 `[speed:]` 不会覆盖这段暂停。
        - 玩家按取消键快进，或者这一句带 `[skip]` 时，等待会被直接跳过，剩下的字立刻打出来。
    - `[speed:x]` 将打字机的打字间隔设置为 `x` 秒，只允许直接输入数字，不允许输入算式。默认此值为 `1/15=0.0667` 秒。
    - `[size:x]` 把**后面**的文字字号改成 `x` ，只允许直接输入数字。已打出的字保持创建时的字号，屏幕上的文本不会改变字号。bondfont 不会因此关闭，每个字的缩放与字距依旧生效。
    - `[colorRGB:r, g, b]` 使用RGB格式设置字符颜色 `（0 ~ 255）` 。
    - `[colorHEX:rrggbb]` 使用十六进制设置字符颜色 `（00 ~ ff）` 。
    - `[font:x]` 将字体设置为 `x` 。路径从 `Resources/Fonts/` 开始算，但**会先查 `Game/Resources/Fonts/`** ，同名文件 Game 区优先。设置字体会关闭 bondfont，恢复需重新启用。
    - `[effect:name, int]` 设置字符的特效。
        - `name` 特效的名字： `shake` 原地颤动、 `rotate` 进行轻微旋转，其他名字等于没有特效。
        - `int` 特效强度，默认 `1` ，数字越大强度越大。
    - `[outline:r, g, b, a, t]` 设置文本的外边框。
        - `r, g, b, a` 边框的颜色与透明度。
        - `t` 边框的厚度。
    - `[voice:name]` 设置打字音效，文件在 `Resources/Sounds/Voices/` 里，写文件名即可。
    - `[portrait:frames|interval|mode]` 设置打字时同时播放的动画，一般为说话时有一个角色播放说话动画。
        - `frames` 帧图片，**用英文逗号分隔**，例如 `a.png, b.png` 。
        - `interval` 每帧多少秒，默认 `1/30` 。
        - `mode` 播放模式，默认 `looponce` （播完一轮回到第一帧）。
        - 三段之间都用 `|` 分隔，只有 `frames` 是必填的： `[portrait:a.png, b.png|0.05|looponce]` 。
    - `[portrait:remove]` 移除说话动画（写 `hide` / `clear` / `none` 效果一样）。
    - `[skip]` 本句话进行快进，不需要值。快进会跳过所有 `[wait:]` 等待。
    - `[noskip]` 禁止这一句被取消键快进，和 `[skip]` 正好相反。
    - `[next]` 这句打完立刻翻到下一句，不用等玩家按确认键， `manual` 模式下同样生效。
        - 气泡属于显示它的那一句，因此 `[next]` 会把气泡和文本一起清掉；下一句需要气泡时需重新使用 `[showbubble:]` 。
    - `[showbubble:dir, pos]` 显示气泡对话框。 `dir` 是尾巴朝向，可取 `left` / `right` / `up` / `down` （默认 `left` ）； `pos` 是尾巴沿着边框的位置 `0 ~ 1` ，默认 `0.5` 。
    - `[hidebubble]` 隐藏气泡对话框。
    - `[func:name]` 调用名为 `name` 的函数。**查表顺序**：先查本打字机的 `funcs` 注册表（用 `typer:SetFunc` 注册过），未命中再回退到 `_G[name]` 全局。local / 闭包 / upvalue 函数只要通过 `:SetFunc` 注册过，也能从文本中调用，无需挂到全局命名空间。
    - `[func:name|a, b, c]` 调用名为 `name` 的函数，并可以进行传参操作，使用英文逗号进行分割。查表顺序同上。
        - 数字字符串会自动 `tonumber` 转成数字；其他参数按字符串原样传入。
        - 函数执行报错会被 `pcall` 包住，只打印 `[EText] func callback error: ...` 不会中断打字。
        - 找不到时打印 `[EText] function not found in typer.funcs or _G: <name>` 并跳过。
    - `^` 可以使用此符号直接将所有样式重置到默认值。

!!! example "实例方法"
    - `typer:SetFunc(name, fn)` 注册函数 `fn` 到本打字机的 `funcs` 表里，使 `[func:name]` 可调用 local / 闭包 / upvalue 函数。
        - `name` 字符串名（与文本里 `[func:name]` 对应）；空串或非字符串直接返回。
        - `fn` 是 `function` 时注册；传 `nil` 时**清掉**该名字的条目。
        - 返回 typer 自身，支持链式： `t:SetFunc("shake", shake):SetFunc("heal", heal)`。
        - **注册时机**：必须在文本扫描到 `[func:]` 标签**之前**完成，通常在创建 typer 后立即注册。
        - 旧的全局函数写法仍兼容（`_G[name]` 兜底），既有文本无需修改。

!!! tip "多个标签可连续排列"
    例如 `[font:x][colorHEX:ffff00][effect:shake, 2]` ，效果依次叠加。

---

### NText 打字机

`NText` 全称 `Neutral Text` ，特点是样式写在样式表中，与文本分离，修改文本时不影响样式。

使用 `Typers.NText.New(text, position, layer, size, opts, mode)` 来创建一个 `ntext` 模式的打字机。

- `text` 要打的文本，可以使用字符串或表，若使用表则会将文本分开为可翻页类型。
- `position` 打字机第一个字符所处的位置。
- `layer` 打字机的图层。
- `size` 打字机有显示的对话框的大小。
- `opts` 样式表，内部放独立样式设置。
- `mode` 打字机的模式： `manual` 手动切换到下一句、 `none` 无法手动干预，仅通过代码切换到下一句。若创建时没有给出参数，默认为 `manual` 模式。

!!! example "使用案例"

    ```lua
    local text = Typers.NText("&* 这&是一句话^...", {320, 240}, 0, {0, 0}, {
        {
            color = {1, 0, 0},
            outline = {0, 1, 1, 1, 2},
        },
        {
            color = {0, 1, 0}
        }
    }, "manual")
    ```

**修改样式：**

通过在句子中添加 `&` 和 `^` 符号来进行样式修改。

??? example "所有样式"
    - `font` 所用字体，在设置时会自动解除 `bondfont` 。
    - `size` 字号大小。
    - `color` 文本的颜色，使用 `{r, g, b}` 。
    - `alpha` 文本的透明度 `(0 ~ 1)` 。
    - `outline` 文本的外边框，使用 `{r, g, b, a, t}` 格式。
    - `scale` 文本的放大倍数，默认为 `1` 。中文之类的宽字符由 `bondfont` 自动处理，会以 `2` 倍绘制。
    - `autowrap` 是否自动换行。
    - `wait` 暂停多少秒再继续。与 `[wait:x]` 一样使用**独立计时器**，后续样式不会覆盖，快进时会被跳过。
    - `effect` 字符特效，格式 `{name = "shake", intensity = 3}` 。
    - `voice` 单个打字音效文件名，放在 `Resources/Sounds/Voices/` 下。
    - `voices` 打字音效列表，每个字符随机挑一个播。
    - `skip` 快进设置表，可填 `canskip` （能不能被取消键快进）、`skipping` （当前是否正在快进）、`skipcount` （一次快进几个字）、`absolute` 。
    - `portrait` 角色说话表情切换，支持三种写法：

    ```lua
    -- 1. 完整形式
    portrait = {
        files = {"a.png", "b.png"},
        interval = 0.02,        -- 每帧多少秒，默认 1/30
        mode = "looponce"       -- 默认 looponce：播完一轮回到第一帧
    }

    -- 2. 直接给一串图片路径（interval 与 mode 用默认值）
    portrait = {"a.png", "b.png"}

    -- 3. 移除说话动画
    portrait = "remove"         -- 写 "hide" / "clear" / "none" 效果一样
    ```

---

### SText 打字机

`SText` 全称 `Sequence Text` 序列打字机，特点是文本在打字过程中逐渐拼接，适用于 **存在多个检测条件** 的情况。

!!! example "使用案例"

    ```lua
    local hp = 5
    local text = Typers.SText.New(function (self)
        self:addText("你好")
        self:nextSentence()

        if (hp) then
            self:addText("现在血量有" .. hp .. "点。")
        else
            self:addText("我是盲人看不见血量。")
        end
    end, {80, 60}, 0, {200, 100})
    ```

下面是所有构建过程中可用的函数：

!!! example "构建函数"
    - `self:addText(text)` 给当前句子添加文本。
    - `self:addSkipText(text)` 添加需要被**瞬间打出**的文本（快进时立刻出现）。
    - `self:setFont(name)` 设置字体。设置字体会关闭 `bondfont` ，恢复需重新启用。
    - `self:setWaitTime(time)` 暂停多少秒再继续。使用**独立计时器**，后续的 `setSpeed` 不会覆盖，快进时会被跳过。
    - `self:setSpeed(interval)` 设置打字间隔时间（秒）。
    - `self:setEffect(name, intensity)` 设置字符特效， `name` 填 `shake` 或 `rotate` ， `intensity` 默认 `1` 。
    - `self:setColor(r, g, b)` 设置颜色，取值为 `0 ~ 1` 或 `0 ~ 255` ，引擎自动识别。
    - `self:setColorHEX(hex)` 以十六进制形式设置颜色，例如 `"ff0000"` 。
    - `self:setOutline(r, g, b, a, t)` 文本边框，会以 8 个方向的偏移副本画在字后面。
    - `self:setVoices(voices)` 设置打字音效，可以传一个文件名，也可以传一串。
    - `self:setPortrait(frames, interval, mode)` 设置角色说话动画。 `frames` 是图片路径串（也可以只给一个文件名）， `interval` 默认 `1/30` ， `mode` 默认 `looponce` 。
    - `self:removePortrait()` 移除说话动画。
    - `self:showBubble(visible, dir, pos)` 显示 / 隐藏气泡（ `visible` 为 `false` 时隐藏）。
    - `self:nextSentence()` 结束当前句并等待玩家确认；确认后清空文本，开始下一句。

---

### InstText 打字机

`InstText` 全称 `Instant Text` ，特点是**没有打字动画**：创建的一瞬间整段文字就已经画在屏幕上了。

适用于**长期存在且不需要逐字出现**的文字，例如战斗菜单按钮、商店金钱读数、状态栏。每个字符预先渲染为一张贴图并**跨实例缓存**，显示时长不产生额外的渲染开销，无需每帧调用 `printf` 。

使用 `Typers.InstText.New(text, position, layer, size)` 创建。

- `text` 要显示的文本。传表只会取**第 `1` 项**；想换行得自己写 `\n` （或者打开自动换行）。
- `position` 文本**左上角**的位置。
- `layer` 图层。
- `size` `{宽, 0}` ，第一项是**自动换行的盒子宽度**，默认 `{640, 0}` ；第二项目前没有用处。

!!! example "创建示例"

    ```lua
    local label = Typers.InstText.New(
        "* " .. Localize.localizeText("Battle.Spare"),
        {90, 270},
        "UponArena"
    )
    label:SetAlign("center")
    label.fontsize = 24
    ```

!!! example "实例方法"

    - `SetText(new_text)` 换文字。会重新预渲染，**不会**动颜色。
    - `SetAlign(mode)` 对齐方式， `"left"` （默认） / `"center"` / `"right"` 。对齐是按整行宽度相对 `position` 算的。
    - `Rebuild()` 强制重排一次。手动改了 `size` 或 `auto_wrap` 之后要自己调它。
    - `SetColor(r, g, b)` 改颜色， `0 ~ 1` 或 `0 ~ 255` 均可。
    - `UseBondFont(config)` 换一套中英字体配置，结构同 `EText` 的 bondfont。
    - `Destroy()` / `Remove()` 销毁。会把字符从缓存里减一次引用，**可以重复调用**。
    - `t.font` / `t.fontsize` 这两个属性可直接赋值，赋值后会自动重排，无需调用 `Rebuild()` 。

!!! warning "颜色预渲染在字符中：先改色，再改字"
    `InstText` 把每个字符预先渲染成贴图，绘制时不再重新上色。所以顺序必须是
    `SetColor` → `SetText` （或 `SetColor` → `Rebuild()` ）。
    反过来先换字再改色，屏幕上不会有任何变化。

!!! example "自动换行"

    ```lua
    local t = Typers.InstText.New("一段很长很长、肯定放不下的文字……", {320, 60}, 0, {200, 0})
    t.auto_wrap = true
    t:Rebuild()          -- ← 改完 auto_wrap / size 必须自己重排
    ```

    - 默认**关闭**。关闭时只排一行，引擎内已有的调用不受影响。
    - 打开后按 `size[1]` 折行，规则与 `EText` / `NText` 一致：英文**按单词**折（整个单词推到下一行，不会切一半），中文等宽字符**逐字**折；单个词本身比盒子还宽时才会硬断。
    - 它和 `EText` 一样**不解析方括号标签**， `[wait:]` 之类会原样画成文字。

!!! note "无需每帧更新"
    `InstText` 把自己注册进图层，由 `Layers` 直接绘制，**不走 `Typers.Update`**，
    因此 `love.update` 中无需处理；修改内容后会自动重绘。

!!! warning "需要手动销毁"
    `Layers.clear()` / `Typers.ClearAll()` 会把它一起清掉，主动调用 `Destroy()` 可确保实例被释放。
    反复创建而不销毁时，缓存中的字符贴图数量会持续增长。
    `Typers.InstText.ClearCache()` 会清空全部字符缓存，正在绘制的实例也会被一并释放。

---