---
title: ShaderToy 转化库
---

[ShaderToy](https://www.shadertoy.com/) 上有大量现成的 GLSL 片元着色器。该库将它们的
`mainImage` 写法**自动改写**成 LÖVE 可编译的 Shader，无需手工搬运。

路径： `Scripts/Libraries/ShaderToy/`

| 文件 | 职责 |
|---|---|
| `init.lua` | 入口：创建 Shader、多 Pass 工程、每帧更新 uniform |
| `convert.lua` | 文本改写（检测 uniform、包裹 `mainImage` 、替换函数名） |
| `rules.lua` | 改写规则表，在此处扩展支持的写法 |

```lua
local shadertoy = ImportFile("ShaderToy")
```

!!! note "它不是渲染管线"
    该库只负责"把代码翻译成 LÖVE Shader"与"每帧更新 uniform"。
    绘制位置与尺寸仍由贴图的 `SetShaders` 或自定义的 `setCanvas` 决定。
    引擎常规的 Shader 用法见 **[着色器](./020_shaders.md)** 。

---

## 快速上手

引擎内置一份可直接运行的测试场景 `Scripts/Scenes/TEST/scene_shader.lua` ，
将 ShaderToy 的代码原样传入 `convert()` 即可：

```lua
local shadertoy = ImportFile("ShaderToy")
local s = shadertoy.convert([[
void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord/iResolution.xy;
    vec3 col = 0.5 + 0.5*cos(iTime+uv.xyx+vec3(0,2,4));
    fragColor = vec4(col,1.0);
}
]])

local bg = Sprites.CreateSprite("px.png", 0)
bg:Scale(640, 480)
bg:SetShaders({s.shader})

function scene.update(dt)
    s:update(dt)      -- 必须每帧调用，否则 iTime 不动
end
```

!!! warning "`s.shader` 为实际 Shader"
    `convert()` 返回的是包装对象，传给 `SetShaders` / `love.graphics.setShader` 时
    要用它的 `.shader` 字段。

---

## 改写的内容

`convert.lua` 对原代码做这几件事（规则都在 `rules.lua` 里）：

| 原写法 | 改成 | 原因 |
|---|---|---|
| `texture(tex, uv)` | `Texel(tex, uv)` | LÖVE 的采样函数名不同 |
| `gl_FragCoord` | `screen_coords` | LÖVE 没有 `gl_FragCoord` |
| `iChannelResolution[0]` | `iChannelResolution0` | GLSL ES 1.0 不支持数组 uniform 这样索引 |
| `precision ... float;` | 删除 | LÖVE 不需要，留着反而报错 |
| `void mainImage(...) {...}` | `vec4 effect(...) {...}` | 换成 LÖVE 的入口函数 |

同时在代码最前面**自动插入**它检测到的 uniform 声明，无需自行编写 `extern` ：

| 代码里出现了 | 自动插入 | 每帧自动赋值 |
|---|---|---|
| `iTime` | `extern number iTime;` | 累加 `dt` 的秒数 |
| `iResolution` | `extern vec3 iResolution;` | `{CANVAS_WIDTH, CANVAS_HEIGHT, 1}` |
| `iMouse` | `extern vec4 iMouse;` | `Keyboard.GetMousePosition()` 的 x、y |
| `iFrame` | `extern int iFrame;` | 帧数，每次 `update` 加 1 |
| `iChannel0` ~ `iChannel3` | `extern Image iChannelN;` | 见下节 |
| `iChannelResolution` | `extern vec3 iChannelResolutionN;` | 各通道贴图的宽高 |

未出现在代码中的 uniform **不会**插入声明，也不会赋值，因此删除无用变量可减少一部分每帧开销。

### fragCoord 是怎么算出来的

转换后的 `effect` 函数开头长这样：

```glsl
vec2 fragCoord = vec2(texture_coords.x * iResolution.x,
                      iResolution.y - texture_coords.y * iResolution.y);
```

!!! warning "fragCoord 来自被画图形的 UV，不是屏幕坐标"
    它是 `texture_coords`（贴图 UV）× `iResolution` 算出来的。
    **只有铺满全屏的图**才等于 ShaderToy 里的屏幕坐标。
    把它挂在一张 32×32 的小贴图上，整张 shader 会被压缩进该 32×32 的区域。

    结尾还有一句 `fragColor *= vec4(1.0,1.0,1.0, Texel(texture, texture_coords).a);` ：
    **结果会乘上贴图的 alpha**。使用 `px.png` （1×1 白色贴图）可避免该影响；贴图有透明区域时，
    那些地方的颜色会被乘成 0。

---

## 通道贴图

ShaderToy 的 `iChannel0~3` 默认是噪声图。这个库的做法：

- 转换时，凡是检测到代码里用了 `iChannelN` ，就生成一张 **256×256 随机噪声**贴图顶上
  （ `rules.DEFAULT_NOISE_SIZE` ），因此不做额外配置也能通过编译。
- 需要替换为指定贴图时，使用 `setChannel` 。

```lua
s:setChannel(0, myImage)      -- 第 0 通道用 myImage
```

### 音频通道

`setAudioChannel(id, filepath)` 会把音频变成一张 **512×2** 的贴图送进 shader：

| 行 | 内容 | 取值 |
|---|---|---|
| 第 0 行（y=0） | FFT 频谱 | RGB 都写同一个值 `v` |
| 第 1 行（y=1） | 波形 | R 通道写 `wave * 0.5 + 0.5` |

```lua
s:setAudioChannel(0, "Resources/Music/mus_battle.ogg")
```

!!! warning "FFT 是 O(N²) 的朴素实现"
    `simpleFFT` 对 512 个采样点做双重循环，每帧约 **26 万次**三角函数运算，
    而且是**每帧重算**。按上述运算量，该通道不适于在移动端长期启用。

---

## 单个 Shader 的方法

`convert(code)` 返回的对象（下文叫 `s`）：

| 方法 | 作用 |
|---|---|
| `s:update(dt)` | **每帧调用**。推 `iTime` / `iFrame` / `iMouse` / `iResolution` 并重发通道贴图 |
| `s:apply()` | `setShader(s.shader)` |
| `s:use()` | 同 `apply()` 的别名 |
| `s:clear()` | `setShader()` 取消 |
| `s:setChannel(id, texture)` | 给通道 `id` （0-3）指定贴图 |
| `s:setAudioChannel(id, filepath)` | 给通道 `id` 接音频，并循环播放 |
| `s:unload()` | `release()` 释放 GPU 资源 |
| `s:printCode(mode, savePath)` | 打印/保存转换后的代码，用于调试 |
| `s:generateNoiseTexture(size)` | 手动生成一张噪声贴图 |

字段： `s.shader` （真 Shader）、 `s.original` （原文）、 `s.code` （转换后）、
`s.externs` （插入的声明）、 `s.runtimeFlags` （检测到哪些 uniform）、 `s.time` / `s.frame` 。

!!! example "转换失败时的排查方式"
    ```lua
    s:printCode()                       -- 打印最终 GLSL
    s:printCode("original")             -- 打印原文
    s:printCode("extern")               -- 只打印插入的声明
    s:printCode("final", "out.glsl")    -- 保存到文件后查看
    ```
    多数编译失败可通过该输出定位：uniform 未被检测到，或括号导致 `mainImage` 匹配中断。

---

## 多 Pass 工程

ShaderToy 的 "Buffer A / Buffer B / Image" 在这里叫 **pass** ，前一个 pass 的输出
会自动作为后一个 pass 的 `iChannel` 输入（第 j 个 pass → `iChannel(j-1)` ）。

```lua
local proj = shadertoy.newProject()

proj:addPass("bufferA", codeA)
proj:addPass("image",   codeB)

-- 每帧
proj:update(dt)

-- 绘制（自己挑时机）
proj:draw()
```

| 方法 | 作用 |
|---|---|
| `newProject()` | 新建一个工程 |
| `proj:addPass(name, code)` | 加一个 pass，内部各建两张画布做乒乓 |
| `proj:update(dt)` | 累加工程时间/帧数，并逐个 pass 调 `update(dt)` |
| `proj:draw()` | 依次渲染所有 pass，并把最后一个的结果画到屏幕上 |
| `proj:unload()` | 释放所有画布与 shader |

!!! warning "多 pass 的画布数量与显存占用"
    每个 pass 建 **两张**全屏画布（ `CANVAS_WIDTH × CANVAS_HEIGHT` ）。
    3 个 pass 即 6 张全屏画布，移动端需要计入该占用。切换场景时调用 `unload()` 。

---

## 限制与注意事项

!!! danger "只认 GLSL ES 1.0"
    LÖVE 的 Shader 是 GLSL ES 1.0。ShaderToy 上用 `textureLod` 、 `textureSize` 、
    整数运算、 `switch` 、 `in` / `out` 变量、 `#version 300 es` 的着色器**一定编译失败**。
    选择标注为 "Sound" / "Buffer"、结构简单且不含 cubemap 的旧版着色器，可提高通过率。

!!! warning "不支持的 uniform 不会自动补"
    `iDate` 、 `iChannelTime` 、 `iSampleRate` 、 `iKeyboard` 之类**不在** `rules.UNIFORM_RULES` 里。
    代码里引用了它们，转换时不会插入声明 → 编译报"未定义变量"。
    如需支持，可在 `rules.lua` 中添加规则（加 `extern` 文本 + flag，再在 `init.lua` 的
    `update` 里补一段 `send` ）。

!!! warning "`mainImage` 之外的函数会原样保留"
    转换只替换 `mainImage` 这一块的正则匹配，其余函数照抄，因此辅助函数可正常使用。
    但如果原文里有**另一个**符合 `void mainImage(...)` 形状的函数（例如被注释掉的版本），
    会被一起改写，导致重复定义。

!!! danger "编译失败是 error，不是返回 nil"
    `convert()` 内部直接调 `SE.graphics.newShader` ，语法错会**抛错**。
    加载外部来源的着色器时用 `pcall` 包裹，否则整个场景无法初始化：

    ```lua
    local ok, s = pcall(shadertoy.convert, code)
    if (not ok) then
        print("着色器编译失败：" .. tostring(s))
        return
    end
    ```

!!! warning "iTime 是累加 dt，不受战斗暂停影响"
    `update(dt)` 里 `self._time = self._time + dt` 一直往上加。
    暂停菜单不调用 `update` 时该值停止累加，调用后继续累加。需要让动画跟随游戏节奏时，
    传入处理后的 `dt` 。

!!! warning "Y 轴是反的"
    屏幕坐标 y 向下为正，转换时已经做了一次翻转（见上文 `fragCoord` 公式）。
    但从 ShaderToy 抄来的数学如果本身依赖"y 向上"，视觉上会是上下颠倒的，改公式里的符号即可。
