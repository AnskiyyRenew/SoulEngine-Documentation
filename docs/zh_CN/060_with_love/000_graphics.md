---
title: 图像绘制
---

引擎没有自己造一套绘制 API，这一部分的原则只有一句话：

**开头写 `SE.graphics` ，后面和 `love.graphics` 一模一样。**

```lua
SE.graphics.setColor(1, 0, 0, 1)
SE.graphics.rectangle("fill", 100, 100, 40, 40)
```

之所以写 `SE.graphics` 而不是 `love.graphics` ，唯一的原因是跨平台适配（见 [本专题首页](./index.md) ），功能上没有任何区别，wiki 中 `love.graphics.*` 的说明可直接参照使用。

!!! warning "绘制前应确认是否使用 MAIN_CANVAS"
    引擎的整个游戏画面绘制在一张名为 `MAIN_CANVAS` 的画布上（尺寸 = `CANVAS_WIDTH x CANVAS_HEIGHT` ），再由引擎统一缩放、居中贴到窗口上。<br>
    因此**不应在 `love.draw` 中直接向窗口绘制**：窗口坐标与游戏内坐标不属于同一坐标系，窗口尺寸还会随玩家的屏幕变化。<br>
    场景内部的绘制可直接调用，引擎在进入场景前已完成画布、缩放、位移的设置，细节见 [屏幕与画布](../020_basic/070_screen.md) 。

## 函数一览

下面按用途分组，列出 `FuncProtector` 里全部 **101 个** `SE.graphics` 函数。所有函数的行为、参数、返回值都与同名 `love.graphics` 函数完全一致，这里只写一句话说明，细节见 wiki。

### 创建与加载

| 函数 | 作用 |
| --- | --- |
| `newImage` | 从文件或 `ImageData` 建贴图（引擎中通常使用 `Sprites.New` ） |
| `newFont` | 建字体（引擎中通常使用 `Fonts.New` ） |
| `newImageFont` | 用一张字符表图片建字体 |
| `newText` | 建文本对象，内容可以之后随时改（底层调的是 `love.graphics.newTextBatch` ） |
| `newCanvas` | 建离屏画布，也就是渲染目标 |
| `newQuad` | 从一张贴图里裁出矩形区域 |
| `newShader` | 编译着色器（可以直接给 GLSL 源码，也可以给文件路径） |
| `newMesh` | 建顶点网格 |
| `newSpriteBatch` | 建精灵批次，同一张贴图需要多次绘制时使用 |
| `newParticleSystem` | 建粒子系统 |
| `newVideo` | 建视频对象 |
| `newArrayImage` | 建数组贴图（多层，可用 `drawLayer` 指定层） |
| `newVolumeImage` | 建 3D 贴图 |
| `newCubeImage` | 建立方体贴图 |
| `getDefaultFilter` | 读新建贴图的默认采样过滤 |
| `setDefaultFilter` | 设新建贴图的默认采样过滤（ `"nearest"` 最近邻 / `"linear"` 线性） |

### 画布与呈现

| 函数 | 作用 |
| --- | --- |
| `setCanvas` | 把之后的绘制输出到指定画布；不传参数 = 输出到屏幕 |
| `getCanvas` | 读当前画布 |
| `present` | 把这一帧呈现出来（引擎在 `love.draw` 之后自动调用，无需手动调用） |
| `isActive` | 当前是否处于可绘制的状态 |
| `discard` | 丢弃画布 / 深度 / 模板的内容，用于性能优化 |

### 颜色与清屏

| 函数 | 作用 |
| --- | --- |
| `setColor` | 设当前绘制颜色，之后所有绘制都会乘上它 |
| `getColor` | 读当前颜色 |
| `setBackgroundColor` | 设背景色，窗口被清屏时用 |
| `getBackgroundColor` | 读背景色 |
| `setColorMask` | 屏蔽某些颜色通道的写入 |
| `getColorMask` | 读当前通道屏蔽状态 |
| `clear` | 用当前颜色（或指定颜色）清空当前画布 |
| `reset` | 把所有绘制状态恢复成默认值 |

### 字体与文字

| 函数 | 作用 |
| --- | --- |
| `setFont` | 设当前字体 |
| `getFont` | 读当前字体 |
| `setNewFont` | `newFont` + `setFont` 的二合一 |
| `print` | 画一行文字（左对齐，可旋转缩放） |
| `printf` | 在给定宽度内自动换行，可按 `"left"` / `"center"` / `"right"` / `"justify"` 对齐 |

!!! note "正式文本不要用 print"
    对话、菜单、商店那些文字引擎都走 [打字机](../020_basic/030_typers.md) ，自带换行、逐字、气泡宽度、星号悬挂缩进。<br>
    `print` / `printf` 一般只用于绘制调试信息和对齐要求简单的文字。

### 混合、线型、点与着色器

| 函数 | 作用 |
| --- | --- |
| `setBlendMode` | 设混合模式（ `"alpha"` 默认、 `"add"` 加色、 `"multiply"` 正片叠底等） |
| `getBlendMode` | 读混合模式 |
| `setLineWidth` | 线宽 |
| `getLineWidth` | 读线宽 |
| `setLineStyle` | 线样式（ `"smooth"` 默认 / `"rough"` 硬边，像素风用后者） |
| `getLineStyle` | 读线样式 |
| `setLineJoin` | 折线连接处的样式 |
| `getLineJoin` | 读折线连接处样式 |
| `setPointSize` | `points` 画出来的点的直径 |
| `getPointSize` | 读点直径 |
| `setWireframe` | 线框模式，调试网格时用 |
| `isWireframe` | 是否处于线框模式 |
| `setShader` | 设当前着色器； `setShader()` 不传参数 = 解除 |
| `getShader` | 读当前着色器 |
| `validateShader` | 只编译检查语法、不真正替换，用来提前发现着色器错误 |

### 图形绘制

| 函数 | 作用 |
| --- | --- |
| `draw` | 画贴图 / 画布 / 网格 / 文本对象（引擎里通常用 `Sprites` 的 `spr:Draw()` ） |
| `drawLayer` | 只画精灵批次 / 网格的某一层 |
| `drawInstanced` | 用同一份顶点数据实例化画很多次 |
| `flushBatch` | 立刻提交当前批次 |
| `points` | 画一组点 |
| `line` | 画折线（顶点坐标平铺着传） |
| `rectangle` | 画矩形（ `"fill"` 填充 / `"line"` 描边，可以给圆角半径） |
| `circle` | 画圆或扇形 |
| `ellipse` | 画椭圆 |
| `arc` | 画圆弧 |
| `polygon` | 画多边形 |

### 变换与栈

| 函数 | 作用 |
| --- | --- |
| `push` | 保存当前绘制状态（ `"transform"` 只存变换 / `"all"` 全存） |
| `pop` | 恢复上一次保存的状态 |
| `rotate` | 旋转当前坐标系，**参数是弧度** |
| `translate` | 平移当前坐标系 |
| `scale` | 缩放当前坐标系 |
| `shear` | 斜切当前坐标系 |
| `origin` | 把变换重置回原点 |
| `applyTransform` | 在当前变换上再叠一个 `Transform` 对象 |
| `replaceTransform` | 用 `Transform` 对象替换掉当前变换 |
| `transformPoint` | 世界坐标 → 本地坐标 |
| `inverseTransformPoint` | 本地坐标 → 世界坐标 |
| `getStackDepth` | 当前 `push` 了几层 |

!!! warning "变换是累加的，而且只影响之后的绘制"
    变换不是为某个对象设置属性，而是**修改当前坐标系**。因此常规写法为 `push` 、绘制、 `pop` 。<br>
    未调用 `pop` 会导致**后续所有**绘制发生偏移，且难以定位。

### 裁剪与模板

| 函数 | 作用 |
| --- | --- |
| `setScissor` | 设矩形裁剪区，画到框外的部分不显示 |
| `intersectScissor` | 设裁剪区，并与当前裁剪区求交集 |
| `getScissor` | 读当前裁剪区 |
| `stencil` | 用一段绘制结果当模板，之后的绘制只在（或只在不在）模板范围内生效 |
| `setStencilState` | 设模板比较规则 |
| `setStencilTest` | 开关模板测试 |
| `getStencilTest` | 读模板测试状态 |

### 3D、深度与面剔除

| 函数 | 作用 |
| --- | --- |
| `setDepthMode` | 设深度测试与写入 |
| `getDepthMode` | 读深度模式 |
| `setMeshCullMode` | 设背面剔除 |
| `getMeshCullMode` | 读背面剔除 |
| `setFrontFaceWinding` | 设哪一面算正面 |
| `getFrontFaceWinding` | 读正面判定 |

该组函数用于 3D 或自绘网格，2D 游戏通常不使用。

### 信息与统计

| 函数 | 作用 |
| --- | --- |
| `getWidth` / `getHeight` | 当前渲染目标的宽 / 高（画布模式下返回画布尺寸） |
| `getDimensions` | 一次拿到宽和高 |
| `getPixelWidth` / `getPixelHeight` | 实际像素尺寸（考虑 DPI） |
| `getPixelDimensions` | 一次拿到实际像素宽高 |
| `getDPIScale` | 当前 DPI 缩放 |
| `getRendererInfo` | 渲染器、显卡名、驱动版本 |
| `getSupported` | 当前设备支持哪些特性（压缩格式、模板、GLSL 版本等） |
| `getSystemLimits` | 硬性上限（最大贴图尺寸、纹理单元数等） |
| `getTextureTypes` | 支持的贴图类型 |
| `getStats` | 绘制统计：drawcall 数、贴图切换次数、显存占用等 |
| `isGammaCorrect` | 当前是否开了 sRGB 修正 |
| `captureScreenshot` | 把当前画面存成文件 |
| `getCanvasFormats` | 支持的画布像素格式 |
| `getImageFormats` | 支持的贴图像素格式 |

## 一个完整的绘制例子

```lua
function MyScene:draw()
    SE.graphics.push()

    -- 红色实心圆
    SE.graphics.setColor(1, 0, 0, 1)
    SE.graphics.circle("fill", 320, 240, 40)

    -- 白色描边（描边前要先改回白色）
    SE.graphics.setColor(1, 1, 1, 1)
    SE.graphics.setLineWidth(2)
    SE.graphics.circle("line", 320, 240, 40)

    -- 居中文字
    SE.graphics.printf("Hello LOVE", 0, 300, 640, "center")

    SE.graphics.pop()
end
```

!!! tip "使用 push 与 pop 管理绘制状态"
    颜色、字体、线宽、变换都属于**全局状态**。 `push` 一次、绘制完成后 `pop` 一次，其中的修改不会影响外部。

## 常见问题

!!! danger "未还原颜色是常见的绘制问题"
    `setColor` 是**全局状态**，会一直保留到下次修改。典型情况为绘制红色文本后未改回白色，之后所有贴图均变为红色。<br>
    引擎中多处绘制函数在末尾专门写了一行 `setColor(1, 1, 1, 1)` 以避免该问题。自行编写时同样处理：**绘制后还原颜色，或使用 `push` / `pop` 。**

!!! warning "rotate 的参数是弧度，不是角度"
    `SE.graphics.rotate(math.pi / 2)` 对应旋转 90° 。<br>
    引擎其余位置（灵魂朝向、骨头旋转、矩阵计算等）使用的都是**角度**，两套单位不可混用，传入前使用 `math.rad(角度)` 转换。

!!! warning "setCanvas 之后坐标系和尺寸都发生变化"
    `setCanvas(c)` 之后 `getWidth()` / `getHeight()` 返回的是**画布**的尺寸， `clear()` 清空的也是画布。恢复时需调用 `setCanvas()` （不传参数）。

!!! warning "captureScreenshot 是异步的"
    该函数不会立即返回图片，需等待 LÖVE 完成一次绘制周期将画面读回，结果通过回调返回。

---

## 相关

- [本专题首页](./index.md)：`SE` 这一层的作用、引擎自制函数
- [屏幕与画布](../020_basic/070_screen.md)：`MAIN_CANVAS` 、缩放与居中
- [贴图](../020_basic/020_sprites.md)：多数绘制走 `Sprites`
- [打字机](../020_basic/030_typers.md)：正式文本的绘制
