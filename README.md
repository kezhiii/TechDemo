# Orekit 轨道计算 Python 教程

面向零基础同学的 Orekit 轨道力学计算入门教程。

## 适用对象

- 对航天轨道力学感兴趣的同学
- 需要用 Orekit 进行轨道计算的研究生
- 零基础也可入门

## 环境要求

- Python 3.11+
- Orekit 11.x（通过 conda-forge 安装）
- orekit-data 数据文件

详细配置请参考 [环境配置指南](orekit_tutorial/setup.md)

## 教程目录

| 章节 | 文档 | 代码示例 | 内容 |
|------|------|---------|------|
| **01** | [快速开始](orekit_tutorial/docs/01_快速开始.md) | [01_quick_start.py](orekit_tutorial/examples/01_quick_start.py) | Orekit 初始化、创建第一个轨道 |
| **02** | [核心概念](orekit_tutorial/docs/02_核心概念.md) | — | 时间系统、坐标系、轨道六要素 |
| **03** | [轨道创建与表示](orekit_tutorial/docs/03_轨道创建与表示.md) | [03_orbit_creation.py](orekit_tutorial/examples/03_orbit_creation.py) | KeplerianOrbit/CircularOrbit/CartesianOrbit 与互转 |
| **04** | [数值传播与力学模型](orekit_tutorial/docs/04_数值传播与力学模型.md) | [04_keplerian_propagation.py](orekit_tutorial/examples/04_keplerian_propagation.py) [04_numerical_propagation.py](orekit_tutorial/examples/04_numerical_propagation.py) | 开普勒传播、数值传播、多种力学模型对比 |
| **05** | [力学模型详解](orekit_tutorial/docs/05_力学模型.md) | — | 力学模型详解（参考第04章代码） |
| **06** | [坐标系转换](orekit_tutorial/docs/06_坐标系转换.md) | [06_frame_transform.py](orekit_tutorial/examples/06_frame_transform.py) | GCRF/ITRF/ENU 坐标系转换 |
| **07** | [TLE解析与传播](orekit_tutorial/docs/07_TLE解析与传播.md) | [07_tle_propagation.py](orekit_tutorial/examples/07_tle_propagation.py) | TLE 解析、SGP4/SDP4 传播 |
| **08** | [卫星相对运动](orekit_tutorial/docs/08_卫星相对运动.md) | [08_relative_motion.py](orekit_tutorial/examples/08_relative_motion.py) | Hill 坐标系、相对状态计算 |

## 快速开始

```bash
# 1. 激活环境
conda activate orekit_env

# 2. 运行第一个示例
cd orekit_tutorial
python examples/01_quick_start.py
```

## 文件结构

```
tech_demo/
├── README.md                          # 本文件
└── orekit_tutorial/
    ├── setup.md                       # 环境配置指南
    ├── orekit_init.py                 # 公共初始化模块（所有示例复用）
    ├── requirements.txt               # 依赖库列表
    ├── docs/                          # Markdown 教程文档
    │   ├── 01_快速开始.md
    │   ├── 02_核心概念.md
    │   ├── 03_轨道创建与表示.md
    │   ├── 04_数值传播与力学模型.md
    │   ├── 05_力学模型.md
    │   ├── 06_坐标系转换.md
    │   ├── 07_TLE解析与传播.md
    │   └── 08_卫星相对运动.md
    └── examples/                      # 可运行的 Python 示例
        ├── 01_quick_start.py
        ├── 03_orbit_creation.py
        ├── 04_keplerian_propagation.py
        ├── 04_numerical_propagation.py
        ├── 06_frame_transform.py
        ├── 07_tle_propagation.py
        ├── 08_relative_motion.py
        └── Result/                    # 运行结果输出
            ├── 04_keplerian_propagation/
            ├── 04_numerical_propagation/
            ├── 06_frame_transform/
            ├── 07_tle_propagation/
            └── 08_relative_motion/
```

## 学习建议

1. **按顺序学习**：建议从第01章开始，循序渐进
2. **动手运行**：每个示例都可以直接运行，修改参数观察结果变化
3. **理解输出**：示例代码会打印关键参数，帮助理解计算过程
4. **查看可视化**：运行示例后，结果会保存到 `examples/Result/` 目录
5. **查阅 Orekit 文档**：[https://orekit.org](https://orekit.org)

## 参考资料

- [Orekit 官网](https://orekit.org)
- [Orekit Python 教程](https://gitlab.orekit.org/orekit-labs/python-tutorials)
- [Orekit API 文档](https://orekit.org/orekit-11.3.3/apidocs/)
- [轨道力学基础](https://en.wikipedia.org/wiki/Orbital_mechanics)

## 许可证

本教程基于 Orekit 库，采用 Apache License 2.0 许可证。
