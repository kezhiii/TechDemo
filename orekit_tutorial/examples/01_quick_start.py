# -*- coding: utf-8 -*-
"""
第01章：快速开始
================
运行第一个 Orekit 程序，创建国际空间站的近似轨道。

本章学习目标：
    1. 理解 Orekit 的初始化流程
    2. 学会创建时间和轨道对象
    3. 获取轨道的笛卡尔坐标（位置和速度）

使用方法：
    python 01_quick_start.py
"""

import sys
import os
import math

# ============================================================
# 导入 Orekit 初始化模块
# ============================================================
# sys.path.append() 将父目录添加到 Python 搜索路径
# 这样才能找到并导入 orekit_init.py 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 从 orekit_init 导入所有常用类和函数
# 包括：Orekit 初始化、时间创建、轨道类、坐标系类等
from orekit_init import *

# ============================================================
# 主程序
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  第01章：快速开始 -- 创建第一个轨道")
    print("=" * 60)

    # ----------------------------------------------------------
    # 步骤1：创建时间
    # ----------------------------------------------------------
    # 使用自定义函数 create_date() 创建 Orekit 时间对象
    # 参数：年, 月, 日, 时, 分, 秒
    # 返回：AbsoluteDate 对象（Orekit 的标准时间表示）
    date = create_date(2024, 1, 1, 12, 0, 0)

    # 获取 UTC 时间尺度，用于格式化输出
    # TimeScalesFactory.getUTC() 返回 UTC 时间尺度对象
    utc = TimeScalesFactory.getUTC()

    # AbsoluteDate.toString(scale) 将时间转换为可读字符串
    print(f"\n  时间 (UTC): {date.toString(utc)}")

    # ----------------------------------------------------------
    # 步骤2：定义轨道参数
    # ----------------------------------------------------------
    # Constants.EGM96_EARTH_MU 是地球引力常数（单位：m^3/s^2）
    # 数值：398600.4415 km^3/s^2 = 398600441500000.0 m^3/s^2
    mu = Constants.EGM96_EARTH_MU
    print(f"  地球引力常数 mu = {mu} m^3/s^2")

    # 定义国际空间站 (ISS) 的近似轨道六要素
    # 注意：角度单位使用弧度 (rad)，180度 = pi 弧度

    a = 6_778_000.0          # 半长轴 a (单位：m)
                             # = 地球半径 6378km + 轨道高度 400km
                             # 决定轨道大小和周期

    e = 0.001                # 离心率 e (无量纲，0到1之间)
                             # 0 = 正圆，接近0 = 近圆轨道
                             # ISS 的轨道非常接近圆形

    i = math.radians(51.6)   # 倾角 i (单位：弧度)
                             # 51.6度是 ISS 的典型倾角
                             # math.radians() 将角度转换为弧度

    omega = 0.0              # 近地点幅角 omega (单位：弧度)
                             # 从升交点到近地点的角度
                             # 对于近圆轨道，这个值不太重要

    raan = 0.0               # 升交点赤经 RAAN (单位：弧度)
                             # 轨道面与赤道面交线的位置
                             # 决定轨道面在空间中的朝向

    anomaly = 0.0            # 真近点角 nu (单位：弧度)
                             # 卫星在轨道上相对于近地点的位置
                             # 0 = 在近地点

    print(f"\n  轨道参数输入:")
    print(f"    半长轴 a = {a/1000:.1f} km (地球半径 + 轨道高度)")
    print(f"    离心率 e = {e} (0=正圆, 0~1=椭圆)")
    print(f"    倾角 i   = {math.degrees(i):.1f} deg (轨道面与赤道面夹角)")

    # ----------------------------------------------------------
    # 步骤3：创建开普勒轨道对象
    # ----------------------------------------------------------
    # KeplerianOrbit() 是 Orekit 中最常用的轨道类
    # 构造函数参数说明：
    #   a           - 半长轴 (m)
    #   e           - 离心率
    #   i           - 倾角 (rad)
    #   omega       - 近地点幅角 (rad)
    #   raan        - 升交点赤经 (rad)
    #   anomaly     - 真近点角 (rad)
    #   PositionAngle.TRUE - 表示 anomaly 是真近点角
    #                        (也可以用 PositionAngle.ECCENTRIC 或 MEAN)
    #   FramesFactory.getGCRF() - 地心惯性参考系 (GCRF)
    #                             这是轨道根数所参考的坐标系
    #   date        - 历元时间（轨道参数对应的时间点）
    #   mu          - 中心天体的引力常数（这里是地球）
    orbit = KeplerianOrbit(
        a, e, i, omega, raan, anomaly,
        PositionAngle.TRUE,         # 使用真近点角
        FramesFactory.getGCRF(),    # 地心惯性系 (GCRF)
        date,
        mu
    )

    # ----------------------------------------------------------
    # 步骤4：打印轨道参数
    # ----------------------------------------------------------
    # print_orbit() 是 orekit_init.py 中定义的辅助函数
    # 它会格式化打印轨道的六个要素和周期
    print_orbit(orbit, "国际空间站（近似）轨道")

    # ----------------------------------------------------------
    # 步骤5：创建航天器状态
    # ----------------------------------------------------------
    # SpacecraftState 是 Orekit 中表示航天器完整状态的类
    # 包含：轨道 + 时间 + 质量
    # 参数：
    #   orbit - 轨道对象
    #   mass  - 航天器质量 (kg)
    mass = 420000.0  # ISS 质量约 420 吨
    state = SpacecraftState(orbit, mass)

    # ----------------------------------------------------------
    # 步骤6：打印状态信息
    # ----------------------------------------------------------
    # state.getDate() 获取状态对应的时间
    # state.getMass() 获取航天器质量
    print(f"\n  --- 航天器状态 ---")
    print(f"  时间 (UTC) = {state.getDate().toString(utc)}")
    print(f"  质量       = {state.getMass():.1f} kg")

    # ----------------------------------------------------------
    # 步骤7：获取笛卡尔坐标（位置和速度）
    # ----------------------------------------------------------
    # state.getPVCoordinates() 返回 PVCoordinates 对象
    # 这个方法将轨道根数转换为笛卡尔坐标
    # "PV" 代表 Position-Velocity（位置-速度）
    pv = state.getPVCoordinates()

    # pv.getPosition() 返回位置向量 (Vector3D 类型)
    # 单位：米 (m)
    pos = pv.getPosition()

    # pv.getVelocity() 返回速度向量 (Vector3D 类型)
    # 单位：米/秒 (m/s)
    vel = pv.getVelocity()

    # 打印笛卡尔坐标（转换为 km 和 km/s）
    print(f"\n  --- 笛卡尔坐标 (GCRF) ---")
    print(f"  位置 (km):")
    print(f"    X = {pos.getX()/1000:.3f}")  # getX() 获取 X 分量
    print(f"    Y = {pos.getY()/1000:.3f}")  # getY() 获取 Y 分量
    print(f"    Z = {pos.getZ()/1000:.3f}")  # getZ() 获取 Z 分量
    print(f"  速度 (km/s):")
    print(f"    Vx = {vel.getX()/1000:.3f}")
    print(f"    Vy = {vel.getY()/1000:.3f}")
    print(f"    Vz = {vel.getZ()/1000:.3f}")

    print("\n" + "=" * 60)
    print("  [OK] 第01章完成！")
    print("=" * 60)
