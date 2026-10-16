---
title: ❕️ 资源预加载
---

把一整个目录的资源提前解码进缓存，让后续的 `Sprites.CreateSprite` 和 `Audio.PlaySound` / `PlayMusic` 第一次用到时**不再卡顿**。

当 `Game/Resources/` 下的资源变多之后，进入场景的瞬间会出现短暂停顿：每张图、每段音频在第一次被引用时才解码。`SE.Preload` 用于在合适的时机（比如场景切换时、加载界面里）一次性把它们解码好，之后调用就是直接命中缓存。

预加载只遍历 **Game 区**（ `Game/Resources/` ），不会去碰主 `Resources/` 。主资源目录里往往有几千个文件，全遍历一遍能卡几十秒，因此引擎不处理该目录。

---

## SE.Preload

```lua
SE.Preload("Sprites/Test")          -- Game/Resources/Sprites/Test/ 下全部图片
SE.Preload("Music", "Sounds/ui")    -- 一次预加载多个目录
SE.Preload("Sprites/")              -- 末尾斜杠可有可无
```

参数是可变个数的路径字符串，每个路径会被归一成一个 Game 区目录，然后**递归**遍历（包括所有子文件夹）。

| 路径写法 | 实际遍历的目录 |
|---|---|
| `"Music"` | `Game/Resources/Music/` 整树 |
| `"Sprites/Test"` | `Game/Resources/Sprites/Test/` 整树 |
| `"Sounds/ui/voice"` | `Game/Resources/Sounds/ui/voice/` 整树（多级子路径也行） |
| `"Game/Resources/Music"` | 等价于 `"Music"` |

返回值是**实际交给加载器的文件数**，可以拿来在加载界面显示进度。

### 路径里的类型名

路径的第一个段必须是引擎认识的资源类型：

| 类型名 | 加载到 | 对应基础篇 |
|---|---|---|
| `Sprites` | 贴图缓存（ `sprites.cache` ） | [贴图](../020_basic/020_sprites.md) |
| `Sounds` | 音效缓存（ `Audio.cache` ， static） | [音频](../020_basic/050_audio.md) |
| `Music` | 音乐缓存（ `Audio.cache` ， stream） | [音频](../020_basic/050_audio.md) |
| `Fonts` | 字体缓存 | 字体 |

类型名不匹配会打一条 WARNING 并跳过这个路径，不会中断执行。

### 扩展名分发

按文件后缀决定走哪个加载器，和文件夹类型不一致时**以扩展名为准**（一张 `.wav` 即使放在 `Sprites/` 下也当音频处理）：

- 图片： `png` / `jpg` / `jpeg` / `bmp` / `tga` / `hdr` / `dds`
- 音频： `wav` / `ogg` / `mp3` / `flac` / `aiff` / `it` / `xm` / `mod` / `s3m`
- 字体： `ttf` / `ttc` / `otf` / `fnt`

其它后缀（ `README.md` 、 `.txt` 之类）会被静默跳过。

---

## SE.PreloadAll

```lua
SE.PreloadAll()
```

把整个 `Game/Resources/` 一次性跑一遍。返回加载的文件数。

!!! warning "PreloadAll 的遍历开销"
    这会遍历 Game 区所有资源。Game 区里也有几百个文件时，进游戏前调用一次依然会有可感知的卡顿。
    另一种做法是按场景划分，只对所需的那几个子目录调用 `SE.Preload`。

---

## 调用时机

预加载本身是一次性的同步操作（遍历 + 解码），适合放在**没有渲染压力的瞬间**：

- 加载界面（如果有自定义 loading 场景）。
- 场景的初始化回调里，**在创建第一批 sprite / 播放第一批音频之前**。
- 切场景前的过渡帧。

不要每帧调用，也不要放在 `update` 里：预加载的作用是"提前执行一次"，重复调用不会重新解码，只刷新时间戳，仍会遍历目录。

---

## 和 CreateSprite / PlaySound 的关系

预加载做完之后，调用方**完全无感**：

- `Sprites.CreateSprite("foo.png")` 会照常按路径查 `sprites.cache` ，命中就直接用，不命中再解码——预加载只是把"命中"这件事提前发生。
- `Audio.PlaySound("foo.wav")` / `PlayMusic` 会从 `Audio.cache` 里**克隆**一个模板 Source 出来用，克隆共享底层解码 buffer（音效）或文件句柄（音乐），所以不会每次播放都重新解码。

也就是说：**调过 `SE.Preload` 之后，`CreateSprite` / `PlaySound` 的调用方式不变**，缓存复用由引擎自动完成。

---

## 设计要点

- **只走 Game 区**：主 `Resources/` 不在遍历范围内。把要预加载的资源放进 `Game/Resources/Sprites/<子目录>/` 之类的地方，再用 `SE.Preload("Sprites/<子目录>")` 就能精确预热。
- **幂等**：对同一个路径重复预加载不会重新解码，只刷新缓存时间戳。所以场景反复进出是安全的。
- **不创建实例**：`Sprites.PreloadFile` 只把图片和 ImageData 塞进缓存，不会真的画到屏幕上。是否显示、画在哪，仍由后续调用的 `CreateSprite` 决定。
- **LRU 仍然有效**：预加载进来的图片照样受 `OPT_LRU_SPRITES` 的 LRU 回收管，长时间没被任何 sprite 引用的会被清掉——和正常加载的图遵循同一套生命周期。
