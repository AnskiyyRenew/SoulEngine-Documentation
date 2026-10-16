---
title: JSON 库
---

引擎自带两个 JSON 库：底层的 **dkjson** 和套在它外面的 **SafeJson**。

| 库 | 路径 | 用途 |
|---|---|---|
| dkjson | `Scripts/Libraries/Utils/dkjson.lua` | 纯编解码，无数量和深度限制，适用于自行生成、来源可信的数据 |
| SafeJson | `Scripts/Libraries/Utils/SafeJson.lua` | 在 dkjson 外面加了三层检查，适用于外部传入、来源不可信的 JSON |

引擎内置模块的调用情况如下：

| 位置 | 用哪个 | 用途 |
|---|---|---|
| `Scripts/Libraries/Global.lua` | dkjson | 全局存档 `global_save.json` 的读写 |
| `Scripts/Libraries/Localize.lua` | dkjson | 读取 `Localization/*.json` 翻译表 |
| `Scripts/Libraries/GamejoltAPI.lua` | dkjson | 解析网络接口返回值 |
| `Scripts/Libraries/Controller/VirtualKeyboard.lua` | SafeJson | 玩家自定义的虚拟键盘布局文件 |

!!! warning "导入方式"
    两个库都在 `Utils` 子目录下，**必须带前缀**，写成 `ImportFile("Utils.dkjson")` 。
    `ImportFile("dkjson")` 会找不到文件。

---

## dkjson

```lua
local json = ImportFile("Utils.dkjson")
```

### 解码

```lua
local data, pos, err = json.decode(str, startPos, nullValue)
```

- `str` JSON 字符串。
- `startPos` 从哪个字符开始解析，默认 `1` ，通常不需要传入。
- `nullValue` JSON 里的 `null` 要解码成什么，默认 `nil` 。
- 返回值是 **三个**： `data, pos, err` 。

| 情况 | 返回值 |
|---|---|
| 成功 | `data` = 表/数字/字符串/布尔， `pos` = 解析结束位置， `err` = `nil` |
| 失败 | `data` = `nil` ， `pos` = 出错位置， `err` = 错误描述（包含行号） |

!!! warning "一定要判第三个返回值"
    `local data = json.decode(str)` 在 JSON 写错时 `data` 为 `nil` 但**不报错**，
    之后直接访问 `data.xxx` 才会触发错误，且报错位置与真实原因相距较远。按以下写法处理：

    ```lua
    local data, pos, err = json.decode(text)
    if (err) then
        print("JSON 解析失败（第 " .. pos .. " 个字符附近）：" .. err)
        return
    end
    ```

### 编码

```lua
local text = json.encode(value, options)
```

- `value` 任意 Lua 值，通常是表。
- `options` 可选表，常用的两项：

| 键 | 效果 |
|---|---|
| `indent` | 为 `true` 时输出带缩进换行的可读格式；不写就是一行压缩格式 |
| `keyorder` | 字符串数组，指定对象里键的输出顺序 |

!!! danger "encode 出错是直接抛错，不是返回 nil"
    dkjson 内部写的是 `error(msg, 2)` 。遇到循环引用、函数、userdata 这类无法编码的值，
    `json.encode` 会**直接中断整个调用栈**。写存档时用 `pcall` 包裹：

    ```lua
    local ok, text = pcall(json.encode, myTable)
    if (not ok) then
        print("编码失败：" .. tostring(text))
        return
    end
    ```

### 表编码为数组或对象的判定

JSON 不区分 Lua 的数组与字典，dkjson 的判定规则如下：

| 输入的表 | 编码结果 | 说明 |
|---|---|---|
| `{1, 2, 3}` | `[1,2,3]` | 整数键 `1..n` 连续 → 数组 |
| `{a = 1}` | `{"a":1}` | 有非整数键 → 对象 |
| `{[1] = "a", [3] = "c"}` | `["a",null,"c"]` | **断档也算数组**，缺的那格补 `null` （不是退化成对象） |
| `{}` | `{}` | 空表是对象 |
| `{1, 2, x = 3}` | `{"1":1,"2":2,"x":3}` | 混了非整数键 → 对象 |

规则本身是 `isarray(tbl)` （ `dkjson.lua` 第 81 行）：**只要所有键都是 `>= 1` 的整数就当作数组**，然后按**最大键值** `max` 从头循环到 `max` ，`nil` 的位置补 `null` 。

!!! note "唯一的例外：洞太多才退化成对象"
    `isarray` 最后有一句：

    ```lua
    if max > 10 and max > arraylen and max > n * 2 then
        return false -- don't create an array with too many holes
    end
    ```

    该条件表示：只有当最大键超过 10、且实际元素数不足最大键的一半时，才按对象编码（键会变成字符串）。
    比如 `{[1]="a", [50]="b"}` ： `max = 50` 、 `n = 2` 、 `50 > 2 * 2` ，于是退化成 `{"1":"a","50":"b"}` 。<br>
    而 `{[1]="a",[3]="c"}` 因为 `max = 3` 不超过 10，**仍然是数组**。

!!! warning "往返转换后的形态差异"
    存进去是 `[1,2,3]` ，读出来还是 `{1,2,3}` ；<br>
    但**断档数组**存进去是 `["a",null,"c"]` ，读出来是 `{1 = "a", 3 = "c"}` —— 中间那格在 Lua 里就是**不存在**（ `nil` ）， `t[2]` 取到 `nil` ；<br>
    只有落到上面那个"洞太多"分支对象化的，读回来键才是**字符串 `"1"`** ， `t[1]` 取不到，需要用 `tonumber(k)` 转换后再访问。

    存档里的列表要么保证连续，要么读取时对每个键做一次 `tonumber` 。

### 特殊值

| 值 | 行为 |
|---|---|
| `nil` | 编码为 `null` |
| `math.huge` / `-math.huge` / `NaN` | 编码为 `null` （不是报错，是静默变 null） |
| 函数 / userdata | 编码时 `error` |
| 循环引用的表 | 编码时 `error` |

`json.null` 是一个特殊标记，写进表里会被编码成 `null` （而不是被当成空表消失）：

```lua
local t = {name = "Sans", nick = json.null}
print(json.encode(t))   -- {"name":"Sans","nick":null}
```

### 引擎里的真实例子

??? example "Global.lua 的存档读写（简化）"
    ```lua
    local json = ImportFile("Utils.dkjson")
    local file_name = "global_save.json"

    -- 读
    local contents = SE.filesystem.read(file_name)
    local decoded, _, err = json.decode(contents)
    if (not decoded) then
        print("存档损坏：" .. tostring(err))
    end

    -- 写
    local encoded = json.encode(global._saveData or {})
    SE.filesystem.write(file_name, encoded)
    ```

!!! note "路径是相对存档目录"
    `SE.filesystem.read` / `write` 走的是 LÖVE 的**存档目录**（手机上是应用私有目录），
    传相对路径即可，**不要**传 `C:\...` 这种绝对路径。

---

## SafeJson

```lua
local safejson = ImportFile("Utils.SafeJson")
```

它对**解析方向**加了三层检查，用于处理来源不可信的 JSON（网络返回、玩家修改过的存档、导出的分享码）。

### 解析

```lua
local data, err, errType = safejson.parse(jsonString, options)
```

- 成功： `data` 是解析出来的值， `err` 和 `errType` 都是 `nil` 。
    - 大多数情况是**表**，但 JSON 顶层直接是一个数字 / 字符串 / 布尔 / `null` 时， `data` 就是那个标量（ `null` 会解成 `nil` ）。因此不要无条件使用 `#data` 。
- 失败： `data` 是 `nil` ， `err` 是英文描述， `errType` 是错误类型编号。

| `errType` | 常量名 | 含义 |
|---|---|---|
| `1` | `MALFORMED` | JSON 本身语法错误（含 BOM 头） |
| `2` | `UNSAFE_KEY` | 键名或值命中黑名单；**调试钩子检测也算这一类** |
| `3` | `CIRCULAR` | 循环引用（**目前不会出现**，见下） |
| `4` | `OVER_LIMIT` | 超过数量/深度/长度限制 |

!!! warning "`errType == 3` 为不可达取值"
    `SafeJson.lua` 里 `error_types.CIRCULAR = 3` **只有定义，没有任何地方返回它**。<br>
    原因是 `parse` 走的是 dkjson 的 `decode`（纯文本 → 表），解码阶段不会产生表之间的循环引用；而编码一侧（ `encode` ）没有对应检查。<br>
    因此判断 `errType` 时只需处理 `1` / `2` / `4` ， `3` 不会出现。

### 三道检查分别是什么

| 顺序 | 检查 | 说明 |
|---|---|---|
| ① | `check_bom` | 文件带 UTF-8 BOM 头直接拒 |
| ② | `precheck_json` + 黑名单扫描 | 在**解析之前**把整段文本转小写，逐条搜黑名单子串 |
| ③ | `check_object_safety` | 解析**之后**递归检查每个键和值 |

`③` 的限制默认值：

| 限制 | 默认值 |
|---|---|
| `max_depth` | 100 层 |
| `max_items` | 12000 个 |
| `max_string_length` | `1e6` 字符 |

需要修改时在第二个参数里覆盖（内部用 `setmetatable(options, {__index = 默认配置})` ，未指定的字段自动回落）：

```lua
local data, err, t = safejson.parse(text, {max_items = 100, max_depth = 10})
```

把 `enable_precheck` 设为 `false` 可以只跳过第 ② 步的整串扫描（第 ③ 步仍会检查键名）。

### 黑名单里有什么

`safejson.config.badwords` 是一张 `{["词"] = true}` 的表，涵盖两类：

- **Lua 侧**： `__index` 、 `getmetatable` 、 `require` 、 `os.execute` 、 `io.popen` 、 `function` 、 `coroutine` ……
- **Web 侧**： `__proto__` 、 `constructor` 、 `prototype` 、 `eval` 、 `fetch` 、 `XMLHttpRequest` 、 `localStorage` 、 `javascript:` 、 `onload` 、 `iframe` ……

这些检查针对的是 JSON 会被传入其他解析器或写入网页的场景。

### 编码

```lua
local text = safejson.encode(value)
```

!!! warning "encode 方向没有任何安全检查"
    它只是 `safejson.json.encode(value)` 的转发，等价于 dkjson 的 `encode` ，
    同样会 `error` 。 `SafeJson` 的"safe"只作用在 `parse` 上。

---

## 已知问题

!!! danger "黑名单是子串匹配，会误伤正常内容"
    `check_object_safety` 用的是 `lower_v:find(word, 1, true)` —— **纯文本子串查找，没有词边界**。
    也就是说：

    - 键名 `global_volume` 含 `global` → 拒绝
    - 键名 `functions` 含 `function` → 拒绝
    - 值 `"The process of..." ` 含 `process` → 拒绝
    - 值 `"Import complete"` 含 `import` → 拒绝

    自行编写的中文内容很少命中上述子串，英文文案命中的概率较高。
    **结论：自行生成的、可信的 JSON 一律用 dkjson**，只有来源不可信时才用 `safejson.parse` 。

!!! warning "parse 会把 \\uXXXX 转义转成小写"
    `normalize_unicode` 会先把文本里所有 `\uXXXX` 替换成对应字符并 `:lower()` ，
    再交给 dkjson。所以 `"\u0041BC"` 会变成 `"abc"` —— **大小写信息丢失**。
    中文一般不用 `\u` 转义，不受影响；但含大写字母的 ASCII 字符串要注意。

!!! warning "开着调试器时 parse 会失败"
    `anti_tamper_check` 检查 `debug.gethook()` ，只要当前挂了调试钩子（断点调试、某些性能分析工具）
    就返回 `"Debug hook detected"` 。调试期间如果 `parse` 莫名失败，先把调试器摘掉再试。

!!! warning "全局内存超过 100MB 会拒绝解析"
    `check_resource_limits` 用 `collectgarbage("count")` 判断，超过 100MB 直接返回错误。
    因此同一份数据在大型工程中可能得到不同的返回结果。

!!! warning "precheck 只扫前 max_string_length 个字符"
    默认值 `1e6` 通常覆盖整段文本。若出于性能考虑将其调小，超出部分**不会被扫**到。

---

## 完整例子

!!! example "自己写一份可读的配置文件"
    ```lua
    local json = ImportFile("Utils.dkjson")

    local config = {
        version = 3,
        player = {name = "Frisk", lv = 1, hp = 20},
        flags = {met_sans = true, spare = false}
    }

    local text = json.encode(config, {
        indent = true,
        keyorder = {"version", "player", "flags"}
    })

    SE.filesystem.write("my_config.json", text)
    ```

!!! example "读一份可能被人改过的外部 JSON"
    ```lua
    local safejson = ImportFile("Utils.SafeJson")

    local text = SE.filesystem.read("download/layout.json")
    if (not text) then return end

    local data, err, errType = safejson.parse(text)
    if (not data) then
        -- errType: 1=语法错 2=危险内容/调试钩子 4=超限（3 目前不会出现）
        print("拒绝加载（类型 " .. tostring(errType) .. "）：" .. tostring(err))
        return
    end

    print("加载成功，控件数量：" .. #(data.controls or {}))
    ```
