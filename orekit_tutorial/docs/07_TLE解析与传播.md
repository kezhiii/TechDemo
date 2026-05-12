# 第07章：TLE解析与传播

本章学习如何解析两行根数 (TLE) 并使用 SGP4/SDP4 传播器。

## 对应代码文件

| 文件 | 说明 |
|------|------|
| `07_tle_propagation.py` | TLE 解析、TLEPropagator 创建、多点传播、TLE传播与开普勒传播对比 |

## 7.1 什么是 TLE

TLE（Two-Line Element Set，两行根数）是描述人造卫星轨道的标准格式：

```
ISS (ZARYA)
1 25544U 98067A   24100.50000000  .00016717  00000-0  10270-3 0  9005
2 25544  51.6400 200.0000 0005000  50.0000 310.0000 15.49000000400000
```

- **第1行**：卫星编号、历元时间、大气阻力项
- **第2行**：倾角、升交点赤经、离心率、近地点幅角、平近点角、圈数

## 7.2 解析 TLE

```python
from orekit_init import *

# 从字符串创建 TLE
tle = TLE(
    "1 25544U 98067A   24100.50000000  .00016717  00000-0  10270-3 0  9005",
    "2 25544  51.6400 200.0000 0005000  50.0000 310.0000 15.49000000400000"
)

# 获取 TLE 参数
print(f"卫星编号: {tle.getSatelliteNumber()}")
print(f"历元时间: {tle.getDate()}")
print(f"平均运动: {tle.getMeanMotion()} rev/day")
```

## 7.3 创建 TLE 传播器

```python
from org.orekit.propagation.analytical.tle import TLEPropagator

# 创建传播器
propagator = TLEPropagator.selectExtrapolator(tle)

# 获取初始状态
initial_state = propagator.getInitialState()
print_orbit(initial_state.getOrbit(), "TLE 初始轨道")
```

## 7.4 传播 TLE

```python
# 传播到指定时间
target_date = create_date(2024, 4, 10, 12, 0, 0)
final_state = propagator.propagate(target_date)

# 获取传播后的轨道
orbit = KeplerianOrbit(final_state.getOrbit())
print_orbit(orbit, "传播后轨道")
```

## 7.5 TLE 参数

TLE 包含以下参数：

| 参数 | 方法 | 说明 |
|------|------|------|
| 卫星编号 | `getSatelliteNumber()` | 如 25544 (ISS) |
| 历元时间 | `getDate()` | TLE 对应的时间 |
| 平均运动 | `getMeanMotion()` | rev/day |
| 离心率 | `getE()` | 无量纲 |
| 倾角 | `getI()` | deg |
| 升交点赤经 | `getRaan()` | deg |
| 近地点幅角 | `getPerigeeArgument()` | deg |
| 平近点角 | `getMeanAnomaly()` | deg |
| B*阻力项 | `getBStar()` | 1/m |

## 7.6 从文件加载 TLE

```python
from org.orekit.propagation.analytical.tle import TLELoader

# 从文件加载
loader = TLELoader("tle_file.txt")
tle = loader.load()
```

## 7.7 批量处理 TLE

```python
# 读取多个 TLE
tle_list = []
with open("tles.txt", "r") as f:
    lines = f.readlines()
    for i in range(0, len(lines), 3):
        name = lines[i].strip()
        line1 = lines[i+1].strip()
        line2 = lines[i+2].strip()
        tle = TLE(line1, line2)
        tle_list.append(tle)

# 对每个 TLE 进行传播
for tle in tle_list:
    propagator = TLEPropagator.selectExtrapolator(tle)
    state = propagator.propagate(target_date)
    print(f"卫星 {tle.getSatelliteNumber()}: {state.getOrbit().getA()/1000:.1f} km")
```

## 7.8 注意事项

1. **TLE 精度**：TLE 是平均根数，精度约 1 km（LEO）到 10 km（GEO）
2. **传播时间**：建议传播时间不超过 30 天
3. **更新频率**：TLE 需要定期更新（通常每天或更频繁）
4. **SGP4 vs SDP4**：Orekit 自动选择（LEO 用 SGP4，高轨用 SDP4）

## 7.9 下一步

恭喜完成所有章节！你现在掌握了 Orekit 的核心功能：

- 轨道创建与表示
- 轨道传播（开普勒 + 数值）
- 力学模型组合
- 坐标系转换
- TLE 解析与传播

建议继续探索：
- [Orekit 官方文档](https://orekit.org)
- [Orekit Python 教程](https://gitlab.orekit.org/orekit-labs/python-tutorials)
