# -*- coding: utf-8 -*-
"""
第06章：坐标系转换
==================
学习不同坐标系之间的位置和速度转换。

本章学习目标：
    1. 理解 Orekit 中的坐标系树结构
    2. 学会 GCRF、EME2000、ITRF 之间的转换
    3. 计算卫星的地面轨迹（经纬度）

使用方法：
    python 06_frame_transform.py
"""

import sys
import os
import math

# 导入 Orekit 初始化模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orekit_init import *

if __name__ == "__main__":
    print("=" * 60)
    print("  第06章：坐标系转换")
    print("=" * 60)

    # 创建公共时间对象
    date = create_date(2024, 1, 1, 12, 0, 0)

    # 地球引力常数
    mu = Constants.EGM96_EARTH_MU

    # ============================================================
    # 示例1：惯性系之间的转换
    # ============================================================
    print("\n--- 示例1：GCRF -> EME2000 ---")

    # FramesFactory.getGCRF() 获取地心惯性参考系
    # GCRF 是最常用的惯性系，Orekit 的根坐标系
    gcrf = FramesFactory.getGCRF()

    # FramesFactory.getEME2000() 获取 J2000 平赤道面坐标系
    # EME2000 与 GCRF 非常接近，差异很小
    eme2000 = FramesFactory.getEME2000()

    # 创建轨道并获取 GCRF 位置
    orbit = KeplerianOrbit(
        6_778_000.0, 0.001,
        math.radians(51.6), 0.0, 0.0, 0.0,
        PositionAngle.TRUE, gcrf, date, mu
    )

    # getPVCoordinates() 将轨道根数转换为位置和速度向量
    pv_gcrf = orbit.getPVCoordinates()

    # getPosition() 获取位置向量 (Vector3D 类型)
    pos_gcrf = pv_gcrf.getPosition()

    # getVelocity() 获取速度向量 (Vector3D 类型)
    vel_gcrf = pv_gcrf.getVelocity()

    print(f"\n  GCRF 位置 (km):")
    print(f"    X = {pos_gcrf.getX()/1000:.3f}")
    print(f"    Y = {pos_gcrf.getY()/1000:.3f}")
    print(f"    Z = {pos_gcrf.getZ()/1000:.3f}")

    # getTransformTo(target_frame, date) 获取坐标系转换对象
    # 参数：目标坐标系，转换时间
    transform = gcrf.getTransformTo(eme2000, date)

    # transformPVCoordinates(pv) 转换位置和速度
    pv_eme = transform.transformPVCoordinates(pv_gcrf)
    pos_eme = pv_eme.getPosition()

    print(f"\n  EME2000 位置 (km):")
    print(f"    X = {pos_eme.getX()/1000:.3f}")
    print(f"    Y = {pos_eme.getY()/1000:.3f}")
    print(f"    Z = {pos_eme.getZ()/1000:.3f}")

    # ============================================================
    # 示例2：惯性系到地固系
    # ============================================================
    print("\n--- 示例2：GCRF -> ITRF ---")

    from org.orekit.utils import IERSConventions

    # FramesFactory.getITRF() 创建国际地球参考系
    # 参数：
    #   IERSConventions.IERS_2010 - IERS 2010 约定
    #   True - 考虑季节变化
    itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)

    # GCRF -> ITRF 转换
    # 这个转换包含地球自转、章动、岁差等
    transform = gcrf.getTransformTo(itrf, date)
    pv_itrf = transform.transformPVCoordinates(pv_gcrf)
    pos_itrf = pv_itrf.getPosition()

    print(f"\n  ITRF 位置 (km):")
    print(f"    X = {pos_itrf.getX()/1000:.3f}")
    print(f"    Y = {pos_itrf.getY()/1000:.3f}")
    print(f"    Z = {pos_itrf.getZ()/1000:.3f}")

    # ============================================================
    # 示例3：计算地面轨迹（经纬度）
    # ============================================================
    print("\n--- 示例3：计算地面轨迹 ---")

    from org.orekit.bodies import OneAxisEllipsoid

    # OneAxisEllipsoid 创建地球椭球体模型
    # 参数：
    #   WGS84_EARTH_EQUATORIAL_RADIUS - 赤道半径 (m)
    #   WGS84_EARTH_FLATTENING - 扁率
    #   itrf - 地固系坐标系
    earth = OneAxisEllipsoid(
        Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
        Constants.WGS84_EARTH_FLATTENING,
        itrf
    )

    # earth.transform(position, frame, date) 将笛卡尔坐标转换为经纬度
    # 返回：GeodeticPoint 对象，包含纬度、经度、高度
    point = earth.transform(pos_itrf, itrf, date)

    # getLatitude() 返回纬度（弧度）
    lat_deg = math.degrees(point.getLatitude())
    # getLongitude() 返回经度（弧度）
    lon_deg = math.degrees(point.getLongitude())
    # getAltitude() 返回高度（米）
    alt = point.getAltitude()

    print(f"\n  地面轨迹:")
    print(f"    纬度 = {lat_deg:.4f} deg")
    print(f"    经度 = {lon_deg:.4f} deg")
    print(f"    高度 = {alt/1000:.3f} km")

    # ============================================================
    # 示例4：传播并计算多点地面轨迹
    # ============================================================
    print("\n--- 示例4：传播并计算多点地面轨迹 ---")

    # 创建开普勒传播器
    propagator = KeplerianPropagator(orbit)
    period = orbit.getKeplerianPeriod()

    print(f"\n  {'时间(min)':<12} {'纬度(deg)':<12} {'经度(deg)':<12} {'高度(km)':<12}")
    print(f"  {'-'*50}")

    # 传播一个周期，计算 10 个点的地面轨迹
    for i in range(10):
        t = i * period / 9

        # 传播到当前时间
        state = propagator.propagate(date.shiftedBy(t))

        # 获取位置
        pv = state.getPVCoordinates()
        pos = pv.getPosition()

        # 转换到 ITRF
        # 注意：每个时间点都需要重新计算变换矩阵
        transform = gcrf.getTransformTo(itrf, state.getDate())
        pv_itrf = transform.transformPVCoordinates(pv)
        pos_itrf = pv_itrf.getPosition()

        # 转换到经纬度
        point = earth.transform(pos_itrf, itrf, state.getDate())
        lat = math.degrees(point.getLatitude())
        lon = math.degrees(point.getLongitude())
        alt = point.getAltitude() / 1000

        print(f"  {t/60:<12.1f} {lat:<12.4f} {lon:<12.4f} {alt:<12.3f}")

    print("\n" + "=" * 60)
    print("  [OK] 第06章完成！")
    print("=" * 60)

    # ============================================================
    # 可视化：绘制地面轨迹
    # ============================================================
    try:
        import matplotlib.pyplot as plt

        print("\n--- 绘制地面轨迹 ---")

        # 收集一个周期的地面轨迹数据
        n_plot = 500
        lats, lons = [], []

        for i in range(n_plot + 1):
            t = i * period / n_plot
            state = propagator.propagate(date.shiftedBy(t))
            pv = state.getPVCoordinates()
            pos = pv.getPosition()

            # 转换到 ITRF
            transform = gcrf.getTransformTo(itrf, state.getDate())
            pv_itrf = transform.transformPVCoordinates(pv)
            pos_itrf = pv_itrf.getPosition()

            # 转换到经纬度
            point = earth.transform(pos_itrf, itrf, state.getDate())
            lats.append(math.degrees(point.getLatitude()))
            lons.append(math.degrees(point.getLongitude()))

        # 创建图形
        fig, ax = plt.subplots(figsize=(12, 6))

        # 绘制地面轨迹
        ax.plot(lons, lats, 'b-', linewidth=1, label='Ground Track')

        # 标记起点
        ax.scatter([lons[0]], [lats[0]], c='green', s=100, label='Start', zorder=5)

        # 设置坐标轴
        ax.set_xlabel('Longitude (deg)')
        ax.set_ylabel('Latitude (deg)')
        ax.set_title('Satellite Ground Track (1 Period)')
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        ax.grid(True, alpha=0.3)
        ax.legend()

        # 添加赤道和本初子午线
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)

        plt.tight_layout()
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Result', '06_frame_transform')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, 'ground_track.png')
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  图像已保存: {save_path}")
        plt.close()

    except ImportError as e:
        print(f"\n  绘图需要安装 matplotlib: {e}")
