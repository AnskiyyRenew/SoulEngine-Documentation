---
title: ❕️ 密钥原生库
---

把 GameJolt private key 之类的秘密从 `.lua` 里搬进编译好的 `.dll` / `.so` ，再通过 LuaJIT FFI 取回。这样解压 `game.love` 的人翻不到明文。

密钥为什么会出现在包里，见 [网络开发 → GameJolt](../090_network/000_gamejolt.md) 。

---

## 先把边界说清楚

这层是**混淆，不是加密**。能挡住什么、挡不住什么都很明确：

| 攻击方式 | 能否挡住 | 说明 |
|---|---|---|
| 解压游戏包搜明文 | 能 | 密钥根本不在 Lua 里 |
| 对 dll / so 跑 strings | 能 | 字节经过 XOR，且不是连续 blob |
| 反汇编看 fill 函数 | 不能 | 单条赋值语句，读几行就还原 |
| hook 导出函数 | 不能 | 可在进程内拦截导出函数 |
| `print(Gamejolt.private_key)` | 不能 | 密钥最终仍在 Lua 内存里 |

最后一条是最根本的限制：**只要密钥参与客户端签名，它就等于公开**。GameJolt 官方也是这个立场。真正要守住 private key，只有让它待在服务端。

这套方案把获取密钥的成本从"解包后直接搜索明文"提高到"需要反汇编分析"。

!!! warning "使用要点"
    - **只藏真正需要藏的东西。** GameJolt 的 `game_id` 是公开信息，放这里没意义，只会平白增加维护负担。
    - **别指望它保护高价值资产。** 如果泄露密钥会导致实质损失，请走服务端代理。

---

## 快速开始

在 `Packager/Secrets/` 下操作：

```bash
# 1. 填密钥（这个文件已被 git 忽略）
cp secrets.local.example.json secrets.local.json
#    编辑它，只填 gamejolt_pk

# 2. 编译
python build.py
```

产物落在：

```
Resources/Libs/Secrets/secrets.dll                  Windows
Resources/Libs/Secrets/android/<abi>/libsecrets.so  Android
```

Windows 需要一个 **64 位** MinGW gcc —— LÖVE 的 Windows 版是 64 位进程，32 位工具链产出的 dll 会**静默**加载失败。脚本会自动探测 Dev-Cpp 自带的 `MinGW64/bin/gcc.exe` ，找不到就用 `--gcc` 指定。

Android 需要 NDK。没找到时会跳过并提示，不会让整个构建失败 —— Windows 产物才是日常开发要用的。装好 NDK 后：

```bash
python build.py --ndk D:/android-sdk/ndk/27.3.13750724
```

---

## 两个平台，两种落位

这是整个方案最容易出错的地方： `ffi.load` 走的是**操作系统加载器**（ `LoadLibrary` / `dlopen` ），**不是** LÖVE 的虚拟文件系统。 `Resources/Libs/...` 这种路径只对 `love.filesystem` 有意义，对操作系统毫无意义。

| 目标 | 库必须落在哪 | 谁负责 |
|---|---|---|
| Windows 源码模式 | `Resources/Libs/Secrets/` | `build.py` |
| fused exe | **exe 同目录**（fused 之后磁盘上没有源码树） | `build_tool.py: copy_secret_dll` |
| Android | love-android 模板的 `app/src/main/jniLibs/<abi>/` | `build_tool.py: copy_secret_sos` ，在 gradlew 之前跑 |
| Web / love.js | 不可能，没有原生库 | 自动回退 |

!!! danger "塞在 game.love 里的 .so 永远加载不了"
    `game.love` 是一个待在 `assets` 里的 zip，而 `dlopen` 只搜索应用解压出来的 native 库目录。所以它必须进 `jniLibs/<abi>/` ，由 Gradle 打进 `lib/<abi>/` 。

---

## Lua 侧接口

```lua
local Secrets = ImportFile("Utils.Secrets")
```

| 调用 | 返回 | 说明 |
|---|---|---|
| `Secrets.init()` | `boolean` | 原生库是否加载成功。可重复调用； `get()` 也会惰性触发 |
| `Secrets.available()` | `boolean` | 取值是否来自原生库 |
| `Secrets.source()` | `string` | `"native"` / `"fallback"` / `"none"` |
| `Secrets.status()` | `string` | 诊断：命中路径，或每条候选为什么失败 |
| `Secrets.get(slot)` | `string` 或 `nil` | 按 slot 序号取 |
| `Secrets.gamejoltPK()` | `string` 或 `nil` | 取 GameJolt 私钥的便捷写法 |
| `Secrets.setFallback(slot, value)` | — | 注册明文回退值（web 目标就是靠它） |

### 三级回退

```
原生库  ->  Secrets.fallback  ->  nil
```

`Secrets.fallback` 在初始化时从 `conf_pure.lua` 的 `GamejoltPK` 灌进来，所以没编译产物的开发机照样能跑。库缺失是**正常状态**，不是异常：这台机器没构建过，或者是根本没有原生库的 web 目标。调用方必须把 `nil` 当成"功能不可用"，静默降级。

!!! warning "引擎目前没有任何地方调用它"
    模块已经就位，但没有引擎代码去读它，连 `Gamejolt.init` 都没接。要在自己的入口处手动接线：

    ```lua
    local Secrets = ImportFile("Utils.Secrets")
    local pk = Secrets.gamejoltPK()

    if pk then
        Gamejolt.init(Global.GetVariable("GamejoltID"), pk)
    end
    -- 否则：静默禁用成就 / 排行榜，不要报错打断玩家
    ```

    失败路径必须是静默的。开发机上没编译产物、web 版没有原生库，都是正常情况，不是异常。

---

## 维护

**换密钥**：改 `secrets.local.json` ，重跑 `build.py` ，重新打包。旧的已发布版本会失效，这是必然的。

**加新密钥**：在 `gen_source.py` 的 `SLOT_ORDER` 末尾追加名字，在 `Secrets.lua` 里加一个对应的 `Secrets.SLOT_XXX` 常量。

!!! danger "slot 序号是二进制契约，只能追加"
    绝不能重排或删除。改动会让所有已发布的构建读到**错的**密钥。

**换机器**： `secrets.local.json` 不进 git，需要单独传递（密码管理器之类）。

---

## 故障排查

先看 `Secrets.status()` ，它会把每条候选路径和失败原因都打出来。

| 现象 | 原因 |
|---|---|
| 提示没有 gcc / 编译失败 | 传 `--gcc <path>` ，确认是 64 位 MinGW |
| Windows 加载失败 | dll 不在 exe 同目录（fused），或 32/64 位不匹配 |
| Android 加载失败 | `.so` 没进 `jniLibs/<abi>/` ，或 ABI 与设备不符 |
| 能加载但取值是 nil | 该 slot 在 `secrets.local.json` 里是空的 |
| probe 对不上 | 库版本和 `Secrets.lua` 的 `PROBE_MAGIC` 不一致，重新生成 |

---

## 混淆是怎么做的

生成器 `gen_source.py` 把每个字节 XOR 上一个随索引变化的掩码，然后**不用静态数组**，而是生成一条条赋值语句：

```c
static void se_fill_0(unsigned char *p)
{
    p[0] = 0x10;
    p[1] = 0x2E;
    ...
}
```

所以 `.rodata` 里不存在任何 blob， `strings` 扫不出来。编译加了 `-s` （strip）和 `-fvisibility=hidden` ，只导出两个符号。

导出函数名刻意起得很朴素（ `se_cfg` / `se_cfg_probe` ），不出现 `secret` 、 `key` 、 `gamejolt` 之类的字眼，目的是降低该库的可识别度。
