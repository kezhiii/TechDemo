# Orekit 轨道计算教程 - 环境配置指南

本指南面向**完全零基础**的同学，从安装开发工具开始，一步一步完成环境配置。

---

## 第一部分：安装开发工具

### 1.1 安装 VSCode（代码编辑器）

VSCode 是一款免费、轻量级的代码编辑器，本教程使用它来编写和运行代码。

**下载地址**：https://code.visualstudio.com/

**安装步骤**：

1. 打开下载链接，点击 **Windows** 按钮下载安装包
2. 双击下载的 `VSCodeUserSetup-x.xx.x.exe` 文件
3. 同意许可协议，点击 **下一步**
4. 选择安装位置（保持默认即可），点击 **下一步**
5. 勾选以下选项，点击 **下一步**：
   - ✅ 将"通过 Code 打开"操作添加到上下文菜单
   - ✅ 将 Code 注册为受支持文件类型的编辑器
   - ✑ 添加到 PATH（从命令行启动时使用）
6. 点击 **安装**，等待安装完成
7. 点击 **完成**，启动 VSCode

**首次启动设置**：

1. 启动后会看到欢迎页面，可以关闭
2. 点击左下角的 **齿轮图标** → **设置**
3. 搜索 `encoding`，将 **Files: Encoding** 改为 `UTF-8`

---

### 1.2 安装 Python 插件

VSCode 需要安装 Python 插件才能支持 Python 开发。

**安装步骤**：

1. 打开 VSCode
2. 点击左侧边栏的 **扩展图标**（或按 `Ctrl+Shift+X`）
3. 在搜索框中输入 `Python`
4. 找到 **Microsoft** 发布的 **Python** 插件（下载量最高的那个）
5. 点击 **安装** 按钮
6. 等待安装完成，会显示"已安装"

**可选插件**（推荐安装）：

| 插件名称 | 用途 |
|---------|------|
| Python | Python 语言支持（必装） |
| Pylance | Python 智能提示（推荐） |
| Code Runner | 一键运行代码（推荐） |

---

### 1.3 安装 Conda（Python 环境管理器）

Conda 用于管理 Python 环境和安装软件包，可以避免不同项目之间的依赖冲突。

**下载地址**：https://docs.conda.io/en/latest/miniconda.html

**安装步骤**：

1. 打开下载链接，找到 **Windows Installer**
2. 下载 `Miniconda3-latest-Windows-x86_64.exe`
3. 双击运行安装程序
4. 点击 **Next**，同意许可协议
5. 选择 **Just Me**（仅为当前用户安装），点击 **Next**
6. 选择安装路径（建议保持默认），点击 **Next**
7. **重要设置**：
   - ✅ Add Miniconda3 to my PATH environment variable
   - ✑ Register Miniconda3 as my default Python
8. 点击 **Install**，等待安装完成
9. 点击 **Finish**

**验证安装**：

1. 打开 **新的** Windows 终端（按 `Win+R`，输入 `cmd`，回车）
2. 输入以下命令：
```bash
conda --version
```
3. 如果显示版本号（如 `conda 24.x.x`），说明安装成功

---

## 第二部分：创建 Python 环境

### 2.1 创建独立的 Python 环境

为本教程创建一个独立的环境，避免与其他项目冲突。

**打开终端**：

1. 按 `Win+R`，输入 `cmd`，回车
2. 或者在 VSCode 中按 `` Ctrl+` `` 打开终端

**创建环境**：

```bash
# 创建名为 orekit_env 的环境，使用 Python 3.11
conda create -n orekit_env python=3.11

# 询问是否继续时，输入 y 并回车
```

**激活环境**：

```bash
# 激活环境
conda activate orekit_env

# 激活后，命令行前面会显示 (orekit_env)
# 例如：(orekit_env) C:\Users\你的用户名>
```

**验证环境**：

```bash
# 检查 Python 版本
python --version
# 应显示：Python 3.11.x

# 检查 conda 环境
conda info --envs
# 应显示 orekit_env 环境
```

---

### 2.2 安装 Orekit

**安装命令**：

```bash
# 确保已激活环境
conda activate orekit_env

# 安装 Orekit 11.3.3（指定版本，与教程兼容）
conda install -c conda-forge orekit=11.3.3
```

**等待安装完成**：

安装过程可能需要几分钟，会自动下载并安装以下依赖：
- orekit（轨道力学库）
- openjdk（Java 运行环境）
- jpype1（Java-Python 桥接）

**验证安装**：

```bash
python -c "import orekit; orekit.initVM(); print(f'Orekit {orekit.VERSION} 安装成功')"
```

如果显示 `Orekit 11.3.3 安装成功`，说明安装完成。

---

### 2.3 安装其他依赖库

```bash
# 安装 numpy（数值计算）
conda install numpy

# 安装 matplotlib（绘图）
conda install matplotlib
```

**一键安装所有依赖**：

```bash
conda install -c conda-forge orekit=11.3.3 numpy matplotlib
```

**验证所有依赖**：

```bash
python -c "
import orekit
orekit.initVM()
print(f'Orekit: {orekit.VERSION}')

import numpy as np
print(f'NumPy: {np.__version__}')

import matplotlib.pyplot as plt
print(f'Matplotlib: {plt.matplotlib.__version__}')

print('所有依赖安装成功！')
"
```

---

## 第三部分：配置 Orekit 数据

### 3.1 下载数据文件

Orekit 需要外部数据文件才能正常工作（地球定向参数、行星历表、重力场模型等）。

**方法1：使用 Git 下载（推荐）**

如果你已安装 Git，打开终端执行：

```bash
# 进入教程目录（根据你的实际位置调整）
cd E:\project_code\tech_demo\orekit_tutorial

# 克隆数据文件
git clone https://gitlab.orekit.org/orekit/orekit-data.git
```

**方法2：手动下载 ZIP**

1. 打开浏览器，访问：https://gitlab.orekit.org/orekit/orekit-data/-/archive/master/orekit-data-master.zip
2. 下载 ZIP 文件
3. 解压到教程目录 `orekit_tutorial` 下
4. 将解压后的文件夹重命名为 `orekit-data`

**验证下载**：

```bash
# 检查数据目录是否存在
dir orekit-data

# 应显示以下子目录：
# DE-440-ephemerides
# Earth-Orientation-Parameters
# Potential
# ...
```

---

### 3.2 配置数据路径

打开 `orekit_init.py` 文件，修改数据路径：

```python
# 找到这一行（约第30行）
OREKIT_DATA_PATH = r"D:\orekit-data-main"

# 修改为你的实际路径，例如：
OREKIT_DATA_PATH = r"E:\project_code\tech_demo\orekit_tutorial\orekit-data"
```

**路径格式说明**：
- 使用 `r"..."` 表示原始字符串（避免转义问题）
- Windows 路径使用反斜杠 `\` 或双反斜杠 `\\`
- 确保路径指向 `orekit-data` 文件夹（不是上级目录）

---

### 3.3 验证数据加载

```bash
# 确保已激活环境
conda activate orekit_env

# 进入教程目录
cd E:\project_code\tech_demo\orekit_tutorial

# 运行初始化测试
python orekit_init.py
```

**正常输出**：

```
[OK] 数据加载成功: E:\project_code\tech_demo\orekit_tutorial\orekit-data
==================================================
  Orekit 初始化测试
==================================================
  Orekit 版本: 11.3.3
  时间 (UTC): 2024-01-01T12:00:00.000Z
  国际空间站（近似）轨道
  ...
[OK] 初始化测试通过！
```

---

## 第四部分：运行教程代码

### 4.1 打开教程文件夹

1. 启动 VSCode
2. 点击 **文件** → **打开文件夹**
3. 选择 `E:\project_code\tech_demo\orekit_tutorial`
4. 点击 **选择文件夹**

### 4.2 选择 Python 解释器

1. 按 `Ctrl+Shift+P` 打开命令面板
2. 输入 `Python: Select Interpreter`
3. 选择 `orekit_env` 环境对应的 Python
   - 路径类似：`C:\Users\你的用户名\miniconda3\envs\orekit_env\python.exe`

### 4.3 运行第一个示例

**方法1：命令行运行**

```bash
# 打开终端，激活环境
conda activate orekit_env

# 运行示例
python examples\01_quick_start.py
```

**方法2：VSCode 运行**

1. 打开 `examples\01_quick_start.py`
2. 点击右上角的 **运行按钮**（▶️）
3. 查看下方终端的输出

**预期输出**：

```
============================================================
  第01章：快速开始 -- 创建第一个轨道
============================================================
  时间 (UTC): 2024-01-01T12:00:00.000Z
  ...
[OK] 第01章完成！
============================================================
```

### 4.4 运行绘图示例

```bash
# 运行轨道传播示例（会生成图片）
python examples\04_keplerian_propagation.py

# 图片保存在 Result 目录
dir examples\Result\04_keplerian_propagation\
```

---

## 第五部分：常见问题解答

### Q1: `ModuleNotFoundError: No module named 'orekit'`

**原因**：没有在正确的 conda 环境中运行

**解决**：
```bash
# 激活环境
conda activate orekit_env

# 验证环境
python -c "import orekit; print('OK')"
```

### Q2: `no IERS UTC-TAI history data loaded`

**原因**：Orekit 数据文件未加载或路径错误

**解决**：
1. 确认 `orekit-data` 目录存在
2. 检查 `orekit_init.py` 中的路径是否正确
3. 路径格式示例：`r"E:\project_code\tech_demo\orekit_tutorial\orekit-data"`

### Q3: `ValueError: jvm.dll could not be found`

**原因**：Java 环境配置问题

**解决**：
```bash
# 重新安装 openjdk
conda install -c conda-forge openjdk=17 --force-reinstall
```

### Q4: 中文乱码

**原因**：Windows 终端编码问题

**解决**：
```powershell
# 在 PowerShell 中执行
chcp 65001
```

### Q5: 如何更新 Orekit 版本？

```bash
conda install -c conda-forge orekit=新版本号
```

### Q6: 如何卸载并重新安装？

```bash
# 删除环境
conda env remove -n orekit_env

# 重新创建环境
conda create -n orekit_env python=3.11
conda activate orekit_env
conda install -c conda-forge orekit=11.3.3 numpy matplotlib
```

---

## 依赖库汇总

| 库 | 版本 | 用途 | 安装命令 |
|----|------|------|---------|
| orekit | 11.3.3 | 轨道力学核心库 | `conda install -c conda-forge orekit=11.3.3` |
| openjdk | 17+ | Java 运行环境（orekit 自动安装） | 随 orekit 自动安装 |
| jpype1 | 1.4.1 | Java-Python 桥接（orekit 自动安装） | 随 orekit 自动安装 |
| numpy | 1.26+ | 数值计算 | `conda install numpy` |
| matplotlib | 3.8+ | 绘图可视化 | `conda install matplotlib` |

---

## 快速参考卡片

### 常用命令

```bash
# 激活环境
conda activate orekit_env

# 退出环境
conda deactivate

# 查看已安装的包
conda list

# 查看环境列表
conda info --envs

# 运行 Python 脚本
python script_name.py
```

### 文件路径参考

```
orekit_tutorial/
├── orekit_init.py         # 初始化模块（需要修改数据路径）
├── setup.md               # 本文件
├── README.md              # 教程说明
├── orekit-data/           # 数据文件（需要下载）
├── docs/                  # 教程文档
└── examples/              # 示例代码
    ├── 01_quick_start.py  # 第一个示例
    └── ...
```

---

## 下一步

环境配置完成后，请阅读 [README.md](README.md) 了解教程结构，然后从 [01_quick_start.py](examples/01_quick_start.py) 开始学习！
