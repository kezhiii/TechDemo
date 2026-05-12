# 环境配置指南

## 1. 安装前提

本教程使用 **Python 版 Orekit**，通过 JPype 调用 Java 底层库。

需要安装：
- **Conda** (Anaconda 或 Miniconda)
- **orekit** - 轨道力学核心库
- **numpy** - 数值计算库
- **matplotlib** - 绘图库（用于可视化）
- **orekit-data** - 外部数据文件

## 2. 创建 Conda 环境

```bash
# 创建新环境（推荐 Python 3.11）
conda create -n orekit_env python=3.11

# 激活环境
conda activate orekit_env
```

## 3. 安装 Orekit

```bash
# 从 conda-forge 安装 orekit（会自动安装 jpype1 依赖）
conda install -c conda-forge orekit=11.3.3
```

验证安装：
```python
import orekit
orekit.initVM()
print(f"Orekit 版本: {orekit.VERSION}")
```

## 4. 安装 NumPy

NumPy 用于数值计算（向量运算、矩阵运算等）。

```bash
# 方法1：通过 conda 安装（推荐）
conda install numpy

# 方法2：通过 pip 安装
pip install numpy
```

验证安装：
```python
import numpy as np
print(f"NumPy 版本: {np.__version__}")
```

## 5. 安装 Matplotlib

Matplotlib 用于绘制轨道轨迹、相对运动等图表。

```bash
# 方法1：通过 conda 安装（推荐）
conda install matplotlib

# 方法2：通过 pip 安装
pip install matplotlib
```

验证安装：
```python
import matplotlib.pyplot as plt
print(f"Matplotlib 版本: {plt.matplotlib.__version__}")
```

## 6. 一键安装所有依赖

如果希望一次性安装所有依赖，可以使用以下命令：

```bash
# conda 方式（推荐）
conda install -c conda-forge orekit numpy matplotlib

# 或者 pip 方式
pip install numpy matplotlib
# orekit 仍需通过 conda 安装
conda install -c conda-forge orekit
```

或者创建 `requirements.txt` 文件：

```
numpy
matplotlib
```

然后运行：
```bash
pip install -r requirements.txt
conda install -c conda-forge orekit
```

## 7. 下载 Orekit 数据文件

Orekit 需要外部数据文件才能工作（EOP、行星历表、重力场等）。

```bash
# 方法1：Git 克隆
git clone https://gitlab.orekit.org/orekit/orekit-data.git

# 方法2：下载 ZIP
# 访问 https://gitlab.orekit.org/orekit/orekit-data/-/archive/master/orekit-data-master.zip
```

解压后目录结构：
```
orekit-data-main/
├── DE-440-ephemerides/      # JPL 行星历表
├── Earth-Orientation-Parameters/  # 地球定向参数
├── Potential/               # 重力场模型
├── CSSI-Space-Weather-Data/ # 空间天气数据
├── tai-utc.dat              # UTC-TAI 跳秒表
└── ...
```

## 8. 配置数据路径

在 `orekit_init.py` 中修改数据路径：

```python
OREKIT_DATA_PATH = r"D:\orekit-data-main"  # 改为你的实际路径
```

## 9. 验证环境

运行初始化测试：

```bash
cd orekit_tutorial
python orekit_init.py
```

正常输出应包含：
```
[OK] 数据加载成功: D:\orekit-data-main
Orekit 版本: 11.3.3
[OK] 初始化测试通过！
```

## 10. 运行示例

```bash
# 激活环境
conda activate orekit_env

# 运行第一个示例
python examples/01_quick_start.py

# 运行带有绘图的示例
python examples/03_keplerian_propagation.py
```

## 依赖库汇总

| 库 | 版本 | 用途 | 安装命令 |
|----|------|------|---------|
| orekit | 11.3.3 | 轨道力学核心库 | `conda install -c conda-forge orekit` |
| jpype1 | 1.4.1 | Java-Python 桥接（orekit 自动安装） | 随 orekit 自动安装 |
| numpy | 1.26+ | 数值计算 | `conda install numpy` |
| matplotlib | 3.8+ | 绘图可视化 | `conda install matplotlib` |
| math | 内置 | 数学函数 | 无需安装 |
| os, sys | 内置 | 系统操作 | 无需安装 |

## 常见问题

### Q: `ModuleNotFoundError: No module named 'orekit'`
A: 确保在正确的 conda 环境中运行：
```bash
conda activate orekit_env
python -c "import orekit; print(orekit.VERSION)"
```

### Q: `ModuleNotFoundError: No module named 'numpy'`
A: 安装 numpy：
```bash
conda install numpy
# 或
pip install numpy
```

### Q: `ModuleNotFoundError: No module named 'matplotlib'`
A: 安装 matplotlib：
```bash
conda install matplotlib
# 或
pip install matplotlib
```

### Q: `no IERS UTC-TAI history data loaded`
A: Orekit 数据未加载。确保 `orekit-data-main` 目录存在且路径正确。

### Q: 中文乱码
A: 这是 Windows PowerShell 的编码问题，不影响功能。如需修复，可在 PowerShell 中执行：
```powershell
chcp 65001
```

### Q: 绘图时窗口卡住
A: 示例代码使用 `plt.close()` 自动关闭图形窗口。如果仍有问题，可以设置 matplotlib 为非交互模式：
```python
import matplotlib
matplotlib.use('Agg')  # 在 import pyplot 之前设置
```
