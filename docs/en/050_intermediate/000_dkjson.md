---
title: JSON Library
---

The engine ships with two JSON libraries: the low-level **dkjson** and **SafeJson**, which wraps around it.

| Library | Path | Purpose |
|---|---|---|
| dkjson | `Scripts/Libraries/Utils/dkjson.lua` | Pure encode/decode, fast, no restrictions, **use it for data you wrote yourself and trust** |
| SafeJson | `Scripts/Libraries/Utils/SafeJson.lua` | Adds three safety checks on top of dkjson, for **externally supplied, untrusted JSON** |

The engine itself uses them:

| Location | Which | What for |
|---|---|---|
| `Scripts/Libraries/Global.lua` | dkjson | Reading/writing the global save `global_save.json` |
| `Scripts/Libraries/Localize.lua` | dkjson | Reading the `Localization/*.json` translation tables |
| `Scripts/Libraries/GamejoltAPI.lua` | dkjson | Parsing network API return values |
| `Scripts/Libraries/Controller/VirtualKeyboard.lua` | SafeJson | Player-customized virtual keyboard layout files |

!!! warning "Import method"
    Both libraries live under the `Utils` subdirectory, so **you must include the prefix**, writing `ImportFile("Utils.dkjson")`.
    `ImportFile("dkjson")` will fail to find the file.

---

## dkjson

```lua
local json = ImportFile("Utils.dkjson")
```

### Decode

```lua
local data, pos, err = json.decode(str, startPos, nullValue)
```

- `str` JSON string.
- `startPos` which character to start parsing from, defaults to `1`. Almost never needs to be passed.
- `nullValue` what a JSON `null` should decode to, defaults to `nil`.
- The return value is **three** values: `data, pos, err`.

| Case | Return value |
|---|---|
| Success | `data` = table/number/string/boolean, `pos` = end position of parse, `err` = `nil` |
| Failure | `data` = `nil`, `pos` = error position, `err` = error description (includes line number) |

!!! warning "Always check the third return value"
    `local data = json.decode(str)` gives `data = nil` when the JSON is malformed but **does not raise an error**.
    It only blows up later when you do `data.xxx`, and the error site is far from the real cause. Just write it properly:

    ```lua
    local data, pos, err = json.decode(text)
    if (err) then
        print("JSON parse failed (around character " .. pos .. "): " .. err)
        return
    end
    ```

### Encode

```lua
local text = json.encode(value, options)
```

- `value` any Lua value, usually a table.
- `options` optional table; the two commonly used fields:

| Key | Effect |
|---|---|
| `indent` | When `true`, outputs a readable format with indentation and line breaks; if omitted, a single-line compact format |
| `keyorder` | Array of strings, specifies the output order of keys in the object |

!!! danger "encode throws on error instead of returning nil"
    dkjson internally writes `error(msg, 2)`. When it hits values that cannot be encoded — circular references, functions, userdata — `json.encode` will **abort the entire call stack directly**. Wrap saves in `pcall`:

    ```lua
    local ok, text = pcall(json.encode, myTable)
    if (not ok) then
        print("Encode failed: " .. tostring(text))
        return
    end
    ```

### How a table becomes an array or object

JSON cannot tell Lua "arrays" and "dictionaries" apart. dkjson's rule is:

| Your table | Encoded result | Note |
|---|---|---|
| `{1, 2, 3}` | `[1,2,3]` | Integer keys `1..n` contiguous → array |
| `{a = 1}` | `{"a":1}` | Has non-integer keys → object |
| `{[1] = "a", [3] = "c"}` | `["a",null,"c"]` | **A gap still counts as an array**, the missing slot is filled with `null` (not demoted to object) |
| `{}` | `{}` | Empty table is an object |
| `{1, 2, x = 3}` | `{"1":1,"2":2,"x":3}` | Mixed with non-integer keys → object |

The rule itself is `isarray(tbl)` (`dkjson.lua` line 81): **as long as every key is an integer `>= 1`, it is treated as an array**, then it loops from `1` to the **maximum key value** `max`, filling `nil` positions with `null`.

!!! note "The only exception: too many holes demotes it to an object"
    At the end of `isarray` there is a line:

    ```lua
    if max > 10 and max > arraylen and max > n * 2 then
        return false -- don't create an array with too many holes
    end
    ```

    In plain terms: **only when the maximum key exceeds 10 AND the actual element count is less than half the max key** is it encoded as an object (keys become strings).
    For example `{[1]="a", [50]="b"}`: `max = 50`, `n = 2`, `50 > 2 * 2`, so it demotes to `{"1":"a","50":"b"}`.<br>
    But `{[1]="a",[3]="c"}` stays an array because `max = 3` does not exceed 10.

!!! warning "A round trip will deform it"
    Stored as `[1,2,3]`, read back as `{1,2,3}`;<br>
    but a **gapped array** stored as `["a",null,"c"]` reads back as `{1 = "a", 3 = "c"}` — the middle slot simply **does not exist** in Lua (`nil`), so `t[2]` returns `nil`;<br>
    only when it falls into the "too many holes" branch above and becomes an object do the read-back keys become **the string `"1"`**, which `t[1]` cannot retrieve — you need `tonumber(k)` as a fallback.

    Either keep lists in save files contiguous, or run every key through `tonumber` on read.

### Special values

| Value | Behavior |
|---|---|
| `nil` | Encoded as `null` |
| `math.huge` / `-math.huge` / `NaN` | Encoded as `null` (not an error, silently becomes null) |
| function / userdata | `error` on encode |
| Circular table | `error` on encode |

`json.null` is a special marker; writing it into a table encodes it as `null` (instead of disappearing as an empty table):

```lua
local t = {name = "Sans", nick = json.null}
print(json.encode(t))   -- {"name":"Sans","nick":null}
```

### Real examples in the engine

??? example "Global.lua save read/write (simplified)"
    ```lua
    local json = ImportFile("Utils.dkjson")
    local file_name = "global_save.json"

    -- read
    local contents = SE.filesystem.read(file_name)
    local decoded, _, err = json.decode(contents)
    if (not decoded) then
        print("Save corrupted: " .. tostring(err))
    end

    -- write
    local encoded = json.encode(global._saveData or {})
    SE.filesystem.write(file_name, encoded)
    ```

!!! note "Path is relative to the save directory"
    `SE.filesystem.read` / `write` go through LÖVE's **save directory** (on mobile, the app's private directory).
    Just pass a relative path; **do not** pass an absolute path like `C:\...`.

---

## SafeJson

```lua
local safejson = ImportFile("Utils.SafeJson")
```

It adds three layers of checks on the **parse direction**, to handle "JSON someone else gives you" (network responses, player-hand-edited saves, exported share codes).

### Parse

```lua
local data, err, errType = safejson.parse(jsonString, options)
```

- Success: `data` is the parsed value, `err` and `errType` are both `nil`.
    - Most of the time it is a **table**, but when the JSON top level is directly a number / string / boolean / `null`, `data` is that scalar (`null` decodes to `nil`). So do not unconditionally `#data`.
- Failure: `data` is `nil`, `err` is an English description, `errType` is the error type number.

| `errType` | Constant name | Meaning |
|---|---|---|
| `1` | `MALFORMED` | JSON syntax error (including BOM header) |
| `2` | `UNSAFE_KEY` | A key or value hit the blacklist; **debug hook detection also counts as this type** |
| `3` | `CIRCULAR` | Circular reference (**currently unreachable**, see below) |
| `4` | `OVER_LIMIT` | Exceeds count/depth/length limit |

!!! warning "`errType == 3` is an unreachable branch"
    In `SafeJson.lua`, `error_types.CIRCULAR = 3` is **defined but never returned anywhere**.<br>
    The reason is `parse` goes through dkjson's `decode` (text → table), and the decode stage cannot possibly produce circular references between tables; the encode side (`encode`) has no safety check at all.<br>
    So when writing `errType` checks, covering `1` / `2` / `4` is enough; `3` can never be hit.

### What the three checks are

| Order | Check | Note |
|---|---|---|
| ① | `check_bom` | Rejects files with a UTF-8 BOM header outright |
| ② | `precheck_json` + blacklist scan | Before **parsing**, lowercases the entire text and searches the blacklist substrings one by one |
| ③ | `check_object_safety` | After **parsing**, recursively checks every key and value |

Default limits for `③`:

| Limit | Default |
|---|---|
| `max_depth` | 100 levels |
| `max_items` | 12000 |
| `max_string_length` | `1e6` characters |

To change them, override in the second parameter (internally `setmetatable(options, {__index = default config})`, so unspecified fields fall back automatically):

```lua
local data, err, t = safejson.parse(text, {max_items = 100, max_depth = 10})
```

Setting `enable_precheck` to `false` skips only step ②'s whole-string scan (step ③ still checks key names).

### What is in the blacklist

`safejson.config.badwords` is a `{["word"] = true}` table covering two categories:

- **Lua side**: `__index`, `getmetatable`, `require`, `os.execute`, `io.popen`, `function`, `coroutine` …
- **Web side**: `__proto__`, `constructor`, `prototype`, `eval`, `fetch`, `XMLHttpRequest`, `localStorage`, `javascript:`, `onload`, `iframe` …

These checks are designed for the case where "JSON will be fed into another parser or written into a web page".

### Encode

```lua
local text = safejson.encode(value)
```

!!! warning "The encode direction has no safety check"
    It is just a forward to `safejson.json.encode(value)`, equivalent to dkjson's `encode`, and will also `error`. SafeJson's "safe" only applies to `parse`.

---

## Pitfalls

!!! danger "The blacklist is substring matching and will falsely reject normal content"
    `check_object_safety` uses `lower_v:find(word, 1, true)` — **plain substring search, no word boundaries**.
    That means:

    - Key `global_volume` contains `global` → rejected
    - Key `functions` contains `function` → rejected
    - Value `"The process of..."` contains `process` → rejected
    - Value `"Import complete"` contains `import` → rejected

    It does not affect your own Chinese content much, but English text easily trips it.
    **Conclusion: always use dkjson for JSON you generate and trust yourself; only use `safejson.parse` when the source is untrusted.**

!!! warning "parse lowercases \\uXXXX escapes"
    `normalize_unicode` first replaces every `\uXXXX` in the text with the corresponding character and calls `:lower()`, then hands it to dkjson. So `"\u0041BC"` becomes `"abc"` — **the case information is lost**.
    Chinese generally does not use `\u` escapes and is unaffected; but be careful with ASCII strings containing uppercase letters.

!!! warning "parse fails while a debugger is attached"
    `anti_tamper_check` checks `debug.gethook()`. As long as a debug hook is currently set (breakpoint debugging, some profiling tools), it returns `"Debug hook detected"`. If `parse` mysteriously fails during debugging, detach the debugger first and try again.

!!! warning "Rejects parsing when global memory exceeds 100MB"
    `check_resource_limits` uses `collectgarbage("count")`. If it exceeds 100MB it returns an error directly.
    In large projects this function may "work sometimes, fail sometimes", depending on whether GC just ran at the moment of the call.

!!! warning "precheck only scans the first max_string_length characters"
    Default `1e6`, basically the whole text, but if you shrink it for performance, the part beyond it **will not be scanned**.

---

## Complete examples

!!! example "Write a readable config file yourself"
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

!!! example "Read an external JSON that may have been edited by someone"
    ```lua
    local safejson = ImportFile("Utils.SafeJson")

    local text = SE.filesystem.read("download/layout.json")
    if (not text) then return end

    local data, err, errType = safejson.parse(text)
    if (not data) then
        -- errType: 1=syntax error 2=dangerous content/debug hook 4=over limit (3 currently unreachable)
        print("Rejected load (type " .. tostring(errType) .. "): " .. tostring(err))
        return
    end

    print("Load succeeded, control count: " .. #(data.controls or {}))
    ```
