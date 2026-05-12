# -*- coding: utf-8 -*-
"""
Orekit 公共初始化模块
====================
所有教程示例复用此模块，避免重复初始化代码。

使用方法：
    import sys
    sys.path.append('..')
    from orekit_init import *
"""

import os
import sys
import math
from datetime import datetime

# ============================================================
# 1. 启动 JVM 并加载 Orekit
# ============================================================
import orekit
orekit.initVM()

# ============================================================
# 2. 加载数据文件（必须在任何 Orekit 操作之前）
# ============================================================
from java.io import File
from org.orekit.data import DataContext, DirectoryCrawler

OREKIT_DATA_PATH = r"D:\orekit-data-main"

def load_orekit_data(data_path=OREKIT_DATA_PATH):
    """
    加载 Orekit 数据文件（EOP、行星历表、重力场模型等）

    参数:
        data_path: orekit-data 目录路径

    说明:
        Orekit 依赖外部数据文件才能正常工作，包括：
        - 地球定向参数 (EOP)
        - JPL 行星历表 (DE440)
        - UTC-TAI 跳秒表
        - 重力场模型 (Eigen-06S)
        - 潮汐模型 (FES2004)
    """
    dm = DataContext.getDefault().getDataProvidersManager()
    data_dir = File(data_path)
    if not data_dir.exists():
        print(f"[错误] 数据目录不存在: {data_path}")
        print("请下载 orekit-data:")
        print("  https://gitlab.orekit.org/orekit/orekit-data/-/archive/master/orekit-data-master.zip")
        return False
    dm.clearProviders()
    dm.clearLoadedDataNames()
    dm.resetFiltersToDefault()
    dm.addProvider(DirectoryCrawler(data_dir))
    print(f"[OK] 数据加载成功: {data_path}")
    return True

load_orekit_data()

# ============================================================
# 3. 常用类快捷导入
# ============================================================

# --- 时间系统 ---
from org.orekit.time import AbsoluteDate, TimeScalesFactory, DateComponents, TimeComponents

# --- 坐标系 ---
from org.orekit.frames import FramesFactory, Frame
from org.orekit.utils import IERSConventions

# --- 轨道 ---
from org.orekit.orbits import KeplerianOrbit, CircularOrbit, CartesianOrbit, OrbitType, Orbit, PositionAngle

# --- 航天器状态 ---
from org.orekit.propagation import SpacecraftState

# --- 常数 ---
from org.orekit.utils import Constants

# --- 向量与坐标 ---
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.utils import PVCoordinates

# --- 传播器 ---
from org.orekit.propagation.analytical import KeplerianPropagator
from org.orekit.propagation.numerical import NumericalPropagator
from org.hipparchus.ode.nonstiff import DormandPrince853Integrator

# --- 力学模型 ---
from org.orekit.forces.gravity import NewtonianAttraction
from org.orekit.forces.gravity.potential import GravityFieldFactory
from org.orekit.forces.gravity import HolmesFeatherstoneAttractionModel, ThirdBodyAttraction
from org.orekit.bodies import CelestialBodyFactory, OneAxisEllipsoid

# --- 大气阻力 ---
from org.orekit.models.earth.atmosphere import HarrisPriester
from org.orekit.forces.drag import DragForce, IsotropicDrag

# --- 太阳光压 ---
from org.orekit.forces.radiation import SolarRadiationPressure, IsotropicRadiationSingleCoefficient

# --- TLE ---
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator

# --- 坐标变换 ---
from org.orekit.frames import TopocentricFrame

# ============================================================
# 4. 常用便捷函数
# ============================================================

def create_date(year, month, day, hour=0, minute=0, second=0.0, scale="UTC"):
    """
    创建 Orekit AbsoluteDate 对象

    参数:
        year, month, day: 年月日
        hour, minute, second: 时分秒（默认 00:00:00）
        scale: 时间尺度，可选 "UTC", "TAI", "TT"（默认 UTC）

    返回:
        AbsoluteDate 对象
    """
    ts_map = {
        "UTC": TimeScalesFactory.getUTC(),
        "TAI": TimeScalesFactory.getTAI(),
        "TT":  TimeScalesFactory.getTT(),
    }
    ts = ts_map.get(scale.upper(), TimeScalesFactory.getUTC())
    date_comp = DateComponents(year, month, day)
    seconds_in_day = hour * 3600.0 + minute * 60.0 + second
    time_comp = TimeComponents(seconds_in_day)
    return AbsoluteDate(date_comp, time_comp, ts)


def print_orbit(orbit, label="轨道参数"):
    """打印轨道参数，格式化输出"""
    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}")
    print(f"  半长轴 a       = {orbit.getA()/1000:.3f} km")
    print(f"  离心率 e       = {orbit.getE():.6f}")
    print(f"  倾角 i         = {math.degrees(orbit.getI()):.4f} deg")

    # CircularOrbit 没有 getPerigeeArgument 等方法
    # 需要转换为 KeplerianOrbit 来获取完整参数
    try:
        kep = KeplerianOrbit(orbit)
        print(f"  近地点幅角 w   = {math.degrees(kep.getPerigeeArgument()):.4f} deg")
        print(f"  升交点赤经 R.A.A.N = {math.degrees(kep.getRightAscensionOfAscendingNode()):.4f} deg")
        print(f"  真近点角 v     = {math.degrees(kep.getTrueAnomaly()):.4f} deg")
        print(f"  平近点角 M     = {math.degrees(kep.getMeanAnomaly()):.4f} deg")
    except:
        pass
    print(f"  轨道周期       = {orbit.getKeplerianPeriod():.2f} s ({orbit.getKeplerianPeriod()/3600:.2f} h)")
    print(f"{'='*50}")


def print_state(state, label="航天器状态"):
    """打印航天器状态（轨道+时间+质量）"""
    utc = TimeScalesFactory.getUTC()
    print(f"\n  --- {label} ---")
    print(f"  时间 (UTC)  = {state.getDate().toString(utc)}")
    print(f"  质量        = {state.getMass():.2f} kg")
    print_orbit(state.getOrbit(), label="轨道参数")


# ============================================================
# 5. 测试初始化
# ============================================================
if __name__ == "__main__":
    print("="*50)
    print("  Orekit 初始化测试")
    print("="*50)
    print(f"  Orekit 版本: {orekit.VERSION}")

    # 测试创建时间
    date = create_date(2024, 1, 1, 12, 0, 0)
    utc = TimeScalesFactory.getUTC()
    print(f"  时间 (UTC): {date.toString(utc)}")

    # 测试创建轨道（国际空间站近似轨道）
    mu = Constants.EGM96_EARTH_MU
    orbit = KeplerianOrbit(
        6_778_000.0,            # 半长轴 (m)，约 400km 高度
        0.001,                  # 离心率（近圆）
        math.radians(51.6),     # 倾角 51.6 度
        0.0,                    # 近地点幅角 (rad)
        0.0,                    # 升交点赤经 (rad)
        0.0,                    # 真近点角 (rad)
        PositionAngle.TRUE,     # 角度类型：真近点角
        FramesFactory.getGCRF(),
        date,
        mu
    )
    print_orbit(orbit, "国际空间站（近似）")

    # 测试坐标系
    gcrf = FramesFactory.getGCRF()
    eme2000 = FramesFactory.getEME2000()
    print(f"\n  GCRF: {gcrf}")
    print(f"  EME2000: {eme2000}")

    print("\n[OK] 初始化测试通过！")
