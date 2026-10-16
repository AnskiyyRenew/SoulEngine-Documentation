---
title: 着色器
---

**着色器（Shader）** 是运行在显卡上的一段 GLSL 程序。画面提交给它之后，由它按所编写的规则**逐像素**决定每个点的最终颜色。

在 LÖVE 里，多数情况只需要一个 **片元着色器**（`effect` 函数）：对每个像素执行一次的滤镜。

本篇说明 **引擎里常规的 Shader 写法**。需要直接移植网上现成的效果时，见 [ShaderToy 转化库](./010_shadertoy.md) ；需要了解屏幕着色器"乒乓法"的绘制流程，见 [画布与屏幕](../020_basic/070_screen.md) ；底层的 LÖVE 绘图 API 清单见 [与LOVE开发 → 图像绘制](../060_with_love/000_graphics.md) 。

---

## 最小的一个 Shader

可运行的最小 Shader 如下：

```glsl
vec4 effect(vec4 color, Image tex, vec2 tex_coords, vec2 screen_coords) {
    vec4 pixel = Texel(tex, tex_coords);
    return pixel * color;
}
```

该 Shader 不改变任何结果：取出贴图原色、乘上绘制颜色、再返回。`effect` 的结构即由此构成。

### `effect` 的四个参数

| 参数 | 类型 | 含义 |
| --- | --- | --- |
| `color` | `vec4` | 当前的绘制颜色，来自 `setColor` 或贴图的 `color` / `alpha` |
| `tex` | `Image` | 正在被绘制的纹理，通常即为该贴图本身 |
| `tex_coords` | `vec2` | 纹理 UV，范围 `0~1` ，**按被绘制图形计算** |
| `screen_coords` | `vec2` | 屏幕坐标，单位是像素 |

它的 **返回值** 就是这个像素的最终颜色（包含 alpha），直接决定屏幕上看到的东西。

!!! warning "采样纹理必须用 Texel"
    LÖVE 里取纹理颜色的函数是 `Texel(tex, uv)` ，不是标准 GLSL 的 `texture()` 。写错了编译会直接失败。

!!! warning "`tex_coords` 是图形自己的 UV，不是屏幕坐标"
    只有贴图铺满全屏时，`tex_coords` 才等于屏幕坐标归一化后的值。
    把它挂在一张 32×32 的小图上，`tex_coords` 依然只在 `0~1` 之间取值，
    效果会被压缩进该 32×32 的区域，而不是铺满屏幕。
    这一点和 ShaderToy 的 `fragCoord` 存在区别（见 [ShaderToy 转化库](./010_shadertoy.md)）。

### 顶点着色器入口 `position`

需要改变的是形状而非颜色时，用 **顶点着色器** 入口 `position` ，它决定每个顶点画到哪：

```glsl
vec4 position(mat4 transform_projection, vec4 vertex_position) {
    return transform_projection * vertex_position;
}
```

顶点入口的使用频率低于 `effect` 。制作特效时通常只需改动 `effect` 。

---

## uniform：由 Lua 传入参数

着色器本身不含状态，由 **uniform** 从外部每帧传入参数。

GLSL 侧用 `extern` 声明：

```glsl
extern number time;        // LÖVE 里 number 等价于 float
extern vec2 amplitude;
extern Image mask;
```

Lua 侧用 `send` 赋值：

```lua
shader:send("time", 1.5)
shader:send("amplitude", {0.02, 0.05})
shader:send("mask", someImage)
```

### 类型对照

| GLSL 声明 | Lua 里 `send` 的值 |
| --- | --- |
| `extern number x;` | 一个数字 |
| `extern vec2 / vec3 / vec4 v;` | `{1, 2}` / `{1, 2, 3}` / `{1, 2, 3, 4}` |
| `extern Image img;` | 一张 Image / Canvas |
| `extern mat4 m;` | 矩阵（少见） |
| `extern bool b;` | `true` / `false` |

!!! tip "`number` 就是 `float`"
    LÖVE 里 `number` 是 `float` 的别名，引擎自带的着色器两种写法都在用。写成 `float` 也可以。

!!! example "先查再发，避免静默失败"
    `shader:hasUniform("time")` 可以判断某个 uniform 是否存在。
    名字拼错时 LÖVE 不一定报错，效果也不会变化，因此先用它自检：

    ```lua
    if shader:hasUniform("time") then
        shader:send("time", t)
    end
    ```

---

## 三种用法

| 用法 | 怎么写 | 适用场景 |
| --- | --- | --- |
| **贴图级** | `spr:SetShaders({shader})` | 给某一张图 / 某个 sprite 加特效 |
| **全局屏幕** | `Global.SetVariable("ScreenShaders", {shader})` | 整屏滤镜（做画面氛围） |
| **完全自定义** | `SE.graphics.setShader(shader)` + 自行 `setCanvas` | 需要完全控制绘制时机与目标 |

- 贴图级的方法清单（ `SetShaders` / `AddShader` / `InsertShader` / `RemoveShader` / `ClearShaders` ）见 [贴图 → 常用方法](../020_basic/020_sprites.md) 。
  挂多个着色器时，引擎会在两张和贴图同尺寸的临时画布之间 **乒乓** ，逐个叠加，所以效果会按列表顺序依次作用。
- 全局屏幕的 `ScreenShaders` 走的是主画布 ↔ 中间画布的乒乓流程，原理见 [画布与屏幕](../020_basic/070_screen.md) 。
- 最底层的 `newShader` / `setShader` / `validateShader` 全部包在 `SE.graphics` 下，清单见 [图像绘制](../060_with_love/000_graphics.md) 。

---

## 第一个案例

三步：创建 `.glsl` 文件、创建测试场景、将其设为启动场景。

### 第一步：新建 `Scripts/Shaders/MyWave.glsl`

```glsl
extern number time;
extern number amplitude;

vec4 effect(vec4 color, Image tex, vec2 tex_coords, vec2 screen_coords) {
    // 按 y 轴做正弦横向偏移：越往下，横向扭动越明显
    vec2 uv = tex_coords;
    uv.x += sin(uv.y * 12.0 + time * 3.0) * amplitude;

    vec4 pixel = Texel(tex, uv);
    return pixel * color;
}
```

### 第二步：新建测试场景 `Scripts/Scenes/TEST/scene_my_shader.lua`

```lua
local scene = {}

-- 编译一次并缓存。不要每帧调用 newShader，否则等同于每帧重新编译
local shader = SE.graphics.newShader("Scripts/Shaders/MyWave.glsl")

-- 一张铺满屏幕的白图，用来承载整屏特效
local bg = Sprites.CreateSprite("px.png", 0)
bg:Scale(CANVAS_WIDTH, CANVAS_HEIGHT)
bg:SetShaders({shader})

local t = 0

function scene.update(dt)
    t = t + dt
    shader:send("time", t)          -- 每帧更新时间参数
    shader:send("amplitude", 0.02)
end

function scene.draw() end

function scene.clear()
    Layers.clear()
end

return scene
```

### 第三步：让它一启动就跑

在 `conf_pure.lua` 里把 `FirstRoom` 指向它：

```lua
Global.SetVariable("FirstRoom", "TEST.scene_my_shader")
```

运行后可看到整个屏幕在轻微地左右摆动。将 `amplitude` 从 `0.02` 改成 `0.2` ，偏移幅度变为原来的十倍。

!!! tip "两种加载方式"
    - `SE.graphics.newShader("Scripts/Shaders/MyWave.glsl")` ：直接指定文件路径。
    - `ImportFile("MyWave", "shader")` ：只给名字，引擎会自动去 `Scripts/Shaders/` 找 `.glsl` ，并且 **编译失败时抛出带路径的明确报错**，便于定位。

    也可以直接把 GLSL 代码当字符串传进去，不需要额外文件（[ShaderToy 转化库](./010_shadertoy.md) 采用该方式）。

!!! warning "编译失败是抛错，不是返回 nil"
    Shader 语法错会让 `newShader` **直接抛错**。加载不确定来源的着色器时包一层 `pcall` ，
    否则整个场景无法初始化。需要在加载前单独检查语法时，用 `SE.graphics.validateShader(code)` 。

---

## 引擎自带的 7 个着色器

`Scripts/Shaders/` 下有 7 个可直接使用的着色器。练习时可从拆解修改这些文件开始。

| 文件 | 作用 | 关键 uniform |
| --- | --- | --- |
| `ColorFilter.glsl` | 灰度 + 染色（`mix` 控制灰度程度） | `grayscale` `tint_color` |
| `Gradiant.glsl` | 四角颜色渐变，可旋转角度 | `topLeftColor` 等四角 + `angle` |
| `WaveDistort.glsl` | 正弦波形扭曲，横竖两个方向 | `time` `amplitude` `frequency` `speed` `tex_size` |
| `Glow.glsl` | 采四周邻居算亮度差，边缘发光 | `glow_color` `glow_intensity` `threshold` `tex_size` |
| `Dust.glsl` | 扫描线溶解淡出（用了 `if` 分支与噪声） | `dt` `scan_y` 等 |
| `FourPoint.glsl` | 四点形变，用逆双线性插值解 UV，越界 `discard` | `p1` ~ `p4` |
| `PixelSmooth.glsl` | 用 `dFdx/dFdy` 做像素平滑，用于旋转产生的锯齿 | `texture_pixel_size` |

阅读顺序建议：`ColorFilter` → `WaveDistort` → `Glow` → `FourPoint` 。
前三个分别是修改颜色、修改 UV、采样邻域，覆盖日常的多数需求；`FourPoint` 属于几何层面的插值计算。

---

## 练习路径

Shader 的学习顺序为：**先参照现有着色器，再修改参数，最后自行编写公式**。

### 阶段一：修改常数

把现成着色器的 uniform 推到极端值，观察现象：

- 把 `ColorFilter` 的 `grayscale` 从 `0` 调到 `1` ，画面逐渐变为灰度。
- 把 `Glow` 的 `threshold` 调高 / 调低，发光区域随之变化。
- 把 `WaveDistort` 的 `amplitude` 从 `0` 拉到 `0.5` ，画面扭曲程度随之变化。

### 阶段二：改公式（开始碰数学）

- 把 `sin(...)` 换成 `cos(...)` 、`abs(sin(...))` 、`sqrt(...)` ，波形随之改变。
- 把 `WaveDistort` 里两条轴的 `sin` 频率改成不同的数，做出水波与抖动两种效果的差别。
- 把 `uv.x +=` 改成 `uv.y +=` ，理解横向扭曲和纵向扭曲的对称性。

### 阶段三：从零写小效果

每个效果只实现 **一项功能**，挂在全屏白图上运行：

| 目标 | 思路提示 |
| --- | --- |
| 染色 | `pixel.rgb * vec3(1.0, 0.5, 0.5)` |
| 灰度 | `dot(pixel.rgb, vec3(0.299, 0.587, 0.114))` |
| 反色 | `1.0 - pixel.rgb` |
| 亮度 / 对比度 | `(pixel.rgb - 0.5) * contrast + 0.5 + brightness` |
| 扫描线 | 用 `tex_coords.y` 配合 `sin` 或 `step` 做条纹 |
| 径向暗角 | 用 `distance(tex_coords, vec2(0.5))` 做中心亮、四周暗 |
| 波纹 | 用 `sin(distance(uv, center) * k - time)` 做同心圆 |

### 阶段四：组合与进阶

- 用 `SetShaders` 一次挂多个着色器，观察它们 **按顺序叠加** 的效果。
- 开始接触 **采样邻域**（像 `Glow` 那样取上下左右的像素）和 **多次采样**（模糊、描边）。
- 需要更复杂的整体效果时，见 [ShaderToy 转化库](./010_shadertoy.md) ，引入社区现成的代码后再拆解。

### 参考资源

- **《The Book of Shaders》** （ `thebookofshaders.com` ）—— 免费的 GLSL 概念教程，重点看"颜色 / 形状 / 随机 / 噪声"几章。注意它的示例是 WebGL 写法，搬到 LÖVE 时要换成 `effect` + `Texel` 。
- **[ShaderToy](https://www.shadertoy.com/)** —— 大量现成效果，配合引擎的转化库可以直接使用。
- **引擎自带的 7 个着色器** —— 可作为本地范本，其写法即本项目长期维护的风格。

---

## 性能与注意事项

!!! danger "每帧创建着色器的开销"
    `newShader` 会触发 **GPU 编译**，开销较高。正确做法是在场景加载时编译一次、在模块顶层缓存，
    每帧只 `send` uniform。`send` 的开销较低，可以每帧调用。

!!! warning "画完记得还原"
    `SE.graphics.setShader(shader)` 会一直生效到下一次 `setShader()` 为止。
    用完立刻还原，否则会污染后面所有绘制：

    ```lua
    SE.graphics.setShader(shader)
    -- ... 绘制内容 ...
    SE.graphics.setShader()      -- 还原
    ```

!!! warning "全屏与邻域采样的开销"
    `effect` 是 **每个像素都要执行一遍** 的。`Glow` 这种一次采 5 个点的着色器，
    在整屏像素上就是 5 倍采样量；再叠几个 pass 就是乘法级增长。
    移动端需要计入这部分开销 —— 这也是引擎给 `PixelSmooth` 做了缓存优化、而不是每帧 `setFilter` 的原因。

!!! danger "只认 GLSL ES 1.0"
    没有 `switch` 、没有 `#version 300 es` 、不能动态索引数组 uniform。
    引用网上代码时先确认版本，具体限制与"哪些写法一定编译失败"列在 [ShaderToy 转化库](./010_shadertoy.md) 的限制一节。

!!! note "关于 Y 轴"
    屏幕坐标 y 向下为正。写"从下往上"的数学时方向相反，可将公式里的符号取反，或先画一条参考线确认方向。

!!! tip "用 validateShader 提前查错"
    改完 GLSL 不必每次都进游戏运行才能发现错误：`SE.graphics.validateShader(code)` 只做编译检查、
    不真正替换当前着色器，适合在工具或启动时先执行一次。
