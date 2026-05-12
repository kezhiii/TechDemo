# -*- coding: utf-8 -*-
"""
第03章：轨道创建与表示
======================
学习创建不同类型的轨道，以及它们之间的相互转换。

本章学习目标：
    1. 理解三种轨道类型的区别
    2. 学会创建 KeplerianOrbit、CircularOrbit、CartesianOrbit
    3. 掌握轨道类型之间的转换方法

使用方法：
    python 02_orbit_creation.py
"""

import sys
import os
import math

# 导入 Orekit 初始化模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orekit_init import *

if __name__ == "__main__":
    print("=" * 60)
    print("  第03章：轨道创建与表示")
    print("=" * 60)

    # 创建公共时间对象（所有示例共用）
    # create_date() 是 orekit_init.py 中的辅助函数
    date = create_date(2024, 1, 1, 12, 0, 0)

    # 地球引力常数（单位：m^3/s^2）
    mu = Constants.EGM96_EARTH_MU

    # 获取地心惯性参考系 (GCRF)
    # GCRF 是 Orekit 中最常用的惯性坐标系
    gcrf = FramesFactory.getGCRF()

    # ============================================================
    # 示例1：创建开普勒轨道（太阳同步轨道）
    # ============================================================
    print("\n--- 示例1：开普勒轨道（太阳同步轨道）---")

    # KeplerianOrbit 使用经典的六个开普勒要素描述轨道
    # 太阳同步轨道特点：倾角约 98 度，轨道面每天进动约 0.985 度
    orbit_kep = KeplerianOrbit(
        7_000_000.0,            # 半长轴 a = 7000 km（高度约 620 km）
        0.001,                  # 离心率 e（近圆）
        math.radians(98.0),     # 倾角 i = 98.0 deg（太阳同步）
        math.radians(90.0),     # 近地点幅角 omega
        math.radians(0.0),      # 升交点赤经 RAAN
        math.radians(0.0),      # 真近点角
        PositionAngle.TRUE,     # 第7个参数：表示角度类型为真近点角
        gcrf,                   # 第8个参数：参考坐标系
        date,                   # 第9个参数：历元时间
        mu                      # 第10个参数：引力常数
    )

    # print_orbit() 打印轨道的六个要素和周期
    print_orbit(orbit_kep, "太阳同步轨道 (KeplerianOrbit)")

    # ============================================================
    # 示例2：创建圆轨道（地球同步轨道 GEO）
    # ============================================================
    print("\n--- 示例2：圆轨道（GEO）---")

    # CircularOrbit 专门用于近圆轨道
    # 它使用偏心率分量 (ex, ey) 代替 e 和 omega
    # 这样可以避免当 e≈0 时 omega 退化的问题
    #
    # ex = e * cos(omega + RAAN)
    # ey = e * sin(omega + RAAN)
    #
    # 对于完美圆形轨道：ex = 0, ey = 0
    orbit_circ = CircularOrbit(
        42_164_000.0,           # 半长轴 a = 42164 km（GEO 轨道）
        0.0,                    # ex 分量（e * cos(omega + RAAN)）
        0.0,                    # ey 分量（e * sin(omega + RAAN)）
        math.radians(0.01),     # 倾角 i（近赤道）
        math.radians(0.0),      # 升交点赤经 RAAN
        0.0,                    # 纬度幅角 (omega + nu)
        PositionAngle.TRUE,     # 角度类型
        gcrf,                   # 参考坐标系
        date,                   # 历元时间
        mu                      # 引力常数
    )

    print_orbit(orbit_circ, "地球同步轨道 (CircularOrbit)")

    # ============================================================
    # 示例3：创建笛卡尔轨道
    # ============================================================
    print("\n--- 示例3：笛卡尔轨道 ---")

    # CartesianOrbit 直接使用位置和速度向量
    # 这是最直接的表示方式，但不如开普勒轨道直观

    # 导入向量和坐标类
    # Vector3D 是 Hipparchus 库中的三维向量类
    from org.hipparchus.geometry.euclidean.threed import Vector3D
    # PVCoordinates 包含位置向量和速度向量
    from org.orekit.utils import PVCoordinates

    # 位置向量 (单位：m)
    # GEO 轨道：卫星在赤道面上，距离地心约 42164 km
    pos = Vector3D(42_164_000.0, 0.0, 0.0)

    # 速度向量 (单位：m/s)
    # GEO 轨道速度约 3.07 km/s，方向沿 Y 轴（垂直于位置向量）
    vel = Vector3D(0.0, 3_070.0, 0.0)

    # PVCoordinates(pos, vel) 将位置和速度组合为一个对象
    pv = PVCoordinates(pos, vel)

    # CartesianOrbit(pv, frame, date, mu) 创建笛卡尔轨道
    orbit_cart = CartesianOrbit(pv, gcrf, date, mu)

    print_orbit(orbit_cart, "笛卡尔轨道表示")

    # ============================================================
    # 示例4：轨道类型转换
    # ============================================================
    print("\n--- 示例4：轨道类型转换 ---")

    # 从开普勒轨道转换为笛卡尔坐标
    # orbit.getPVCoordinates() 将轨道根数转换为位置和速度向量
    print("  开普勒轨道 -> 笛卡尔坐标:")
    pv = orbit_kep.getPVCoordinates()
    pos = pv.getPosition()   # 获取位置向量
    vel = pv.getVelocity()   # 获取速度向量
    print(f"    位置 (km): X={pos.getX()/1000:.3f}, Y={pos.getY()/1000:.3f}, Z={pos.getZ()/1000:.3f}")
    print(f"    速度 (km/s): Vx={vel.getX()/1000:.3f}, Vy={vel.getY()/1000:.3f}, Vz={vel.getZ()/1000:.3f}")

    # 从笛卡尔轨道转换为开普勒要素
    # CartesianOrbit(pv, frame, date, mu) 创建笛卡尔轨道
    # 然后可以通过 getA(), getE(), getI() 等方法获取开普勒要素
    print("\n  笛卡尔轨道 -> 开普勒要素:")
    orbit_from_cart = CartesianOrbit(pv, gcrf, date, mu)
    print(f"    半长轴 a = {orbit_from_cart.getA()/1000:.3f} km")
    print(f"    离心率 e = {orbit_from_cart.getE():.6f}")
    print(f"    倾角 i   = {math.degrees(orbit_from_cart.getI()):.4f} deg")

    # ============================================================
    # 示例5：不同轨道高度对比
    # ============================================================
    print("\n--- 示例5：不同轨道高度对比 ---")
    print(f"  {'轨道类型':<15} {'高度(km)':<12} {'半长轴(km)':<15} {'周期(min)':<12}")
    print(f"  {'-'*55}")

    Re = 6378.0  # 地球平均半径 (km)

    # 定义不同轨道类型的高度
    orbits_info = [
        ("LEO", 400),      # 低地球轨道
        ("SSO", 620),      # 太阳同步轨道
        ("MEO", 20200),    # 中地球轨道（GPS 卫星）
        ("GEO", 35786),    # 地球同步轨道
    ]

    for name, alt in orbits_info:
        # 计算半长轴 = 地球半径 + 轨道高度
        a = (Re + alt) * 1000  # 转换为米

        # 创建轨道对象
        orbit = KeplerianOrbit(
            a, 0.001, math.radians(51.6), 0.0, 0.0, 0.0,
            PositionAngle.TRUE, gcrf, date, mu
        )

        # getKeplerianPeriod() 返回轨道周期（单位：秒）
        period = orbit.getKeplerianPeriod() / 60  # 转换为分钟

        print(f"  {name:<15} {alt:<12} {a/1000:<15.1f} {period:<12.1f}")

    print("\n" + "=" * 60)
    print("  [OK] 第03章完成！")
    print("=" * 60)
