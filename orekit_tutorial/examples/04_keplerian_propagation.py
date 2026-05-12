# -*- coding: utf-8 -*-
"""
第04章：开普勒传播
==================
使用开普勒传播器进行两体问题轨道传播。

本章学习目标：
    1. 理解什么是轨道传播
    2. 学会使用 KeplerianPropagator
    3. 传播到指定时间并获取轨道状态

使用方法：
    python 03_keplerian_propagation.py
"""

import sys
import os
import math
import numpy as np

# 导入 Orekit 初始化模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orekit_init import *

if __name__ == "__main__":
    print("=" * 60)
    print("  第04章：开普勒传播")
    print("=" * 60)

    # 创建公共时间对象
    date = create_date(2024, 1, 1, 12, 0, 0)

    # 地球引力常数
    mu = Constants.EGM96_EARTH_MU

    # 获取地心惯性参考系
    gcrf = FramesFactory.getGCRF()

    # ============================================================
    # 示例1：创建开普勒传播器
    # ============================================================
    print("\n--- 示例1：创建开普勒传播器 ---")

    # 创建初始轨道（太阳同步轨道）
    orbit = KeplerianOrbit(
        7_000_000.0,            # 半长轴 7000 km
        0.001,                  # 离心率
        math.radians(98.0),     # 倾角 98 deg (太阳同步)
        math.radians(90.0),     # 近地点幅角
        0.0,                    # 升交点赤经
        0.0,                    # 真近点角
        PositionAngle.TRUE,     # 角度类型：真近点角
        gcrf,                   # 参考坐标系：GCRF
        date,                   # 历元时间
        mu                      # 引力常数
    )

    # 打印初始轨道参数
    print_orbit(orbit, "初始轨道")

    # KeplerianPropagator 是最简单的传播器
    # 它只考虑两体问题（中心天体引力），不考虑摄动
    # 构造函数参数：初始轨道
    propagator = KeplerianPropagator(orbit)

    # ============================================================
    # 示例2：传播到指定时间
    # ============================================================
    print("\n--- 示例2：传播 45 分钟 ---")

    # AbsoluteDate.shiftedBy(seconds) 创建一个偏移后的时间
    # 参数：偏移的秒数（正数=未来，负数=过去）
    target_date = date.shiftedBy(2700.0)  # 45 分钟 = 2700 秒

    # propagator.propagate(target_date) 执行传播
    # 返回：SpacecraftState 对象，包含目标时间的完整状态
    final_state = propagator.propagate(target_date)

    # 获取 UTC 时间尺度用于输出
    utc = TimeScalesFactory.getUTC()
    print(f"  初始时间: {date.toString(utc)}")
    print(f"  目标时间: {target_date.toString(utc)}")

    # final_state.getOrbit() 获取传播后的轨道对象
    print_orbit(final_state.getOrbit(), "传播 45 分钟后")

    # ============================================================
    # 示例3：传播多个时间点，观察轨道变化
    # ============================================================
    print("\n--- 示例3：传播一个完整周期 ---")

    # orbit.getKeplerianPeriod() 返回轨道周期（单位：秒）
    period = orbit.getKeplerianPeriod()
    print(f"  轨道周期: {period:.2f} s ({period/3600:.2f} h)")

    # 传播 10 个时间点，观察轨道变化
    n_points = 10
    for i in range(n_points + 1):
        # 计算当前时间点
        t = i * period / n_points

        # 传播到该时间点
        state = propagator.propagate(date.shiftedBy(t))

        # 获取轨道对象（需要转换为 KeplerianOrbit 才能获取完整参数）
        orb = KeplerianOrbit(state.getOrbit())

        # 打印真近点角和高度
        print(f"\n  t = {t/60:.1f} min:")
        # getTrueAnomaly() 返回真近点角（弧度）
        print(f"    真近点角 = {math.degrees(orb.getTrueAnomaly()):.2f} deg")
        # 高度 = 半长轴 - 地球半径
        print(f"    高度 = {(orb.getA()/1000 - 6378):.2f} km")

    # ============================================================
    # 示例4：比较开普勒传播和理论值
    # ============================================================
    print("\n--- 示例4：开普勒传播验证 ---")

    # 传播半个周期
    state_half = propagator.propagate(date.shiftedBy(period / 2))
    orb_half = KeplerianOrbit(state_half.getOrbit())

    # getTrueAnomaly() 返回真近点角（弧度）
    # math.degrees() 将弧度转换为角度
    print(f"  初始真近点角: {math.degrees(orbit.getTrueAnomaly()):.2f} deg")
    print(f"  半周期后真近点角: {math.degrees(orb_half.getTrueAnomaly()):.2f} deg")
    print(f"  理论值: 180.00 deg (从近地点到远地点)")

    # 传播一个完整周期
    state_full = propagator.propagate(date.shiftedBy(period))
    orb_full = KeplerianOrbit(state_full.getOrbit())

    # getA() 返回半长轴（单位：米）
    print(f"\n  初始半长轴: {orbit.getA()/1000:.3f} km")
    print(f"  一周期后半长轴: {orb_full.getA()/1000:.3f} km")
    print(f"  差异: {abs(orb_full.getA() - orbit.getA())/1000:.6f} km (应接近 0)")
    print(f"  说明：开普勒传播是理想两体问题，一个周期后轨道应完全闭合")

    print("\n" + "=" * 60)
    print("  [OK] 第04章完成！")
    print("=" * 60)

    # ============================================================
    # 可视化：绘制轨道轨迹
    # ============================================================
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        print("\n--- 绘制轨道轨迹 ---")

        # 收集一个周期内的轨道点
        n_plot = 200
        x_list, y_list, z_list = [], [], []

        for i in range(n_plot + 1):
            t = i * period / n_plot
            state = propagator.propagate(date.shiftedBy(t))
            pv = state.getPVCoordinates()
            pos = pv.getPosition()
            x_list.append(pos.getX() / 1000)  # 转换为 km
            y_list.append(pos.getY() / 1000)
            z_list.append(pos.getZ() / 1000)

        # 创建 3D 图形
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        # 绘制轨道轨迹
        ax.plot(x_list, y_list, z_list, 'b-', linewidth=1.5, label='Orbit')

        # 标记起点（绿色）
        ax.scatter([x_list[0]], [y_list[0]], [z_list[0]], c='green', s=100, label='Start', zorder=5)

        # 标记半周期点（红色）
        mid = n_plot // 2
        ax.scatter([x_list[mid]], [y_list[mid]], [z_list[mid]], c='red', s=100, label='Half Period', zorder=5)

        # 绘制地球（简化为球体）
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi, 50)
        Re = 6378.0  # 地球半径 (km)
        x_earth = Re * np.outer(np.cos(u), np.sin(v))
        y_earth = Re * np.outer(np.sin(u), np.sin(v))
        z_earth = Re * np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(x_earth, y_earth, z_earth, color='lightblue', alpha=0.3)

        # 设置坐标轴标签
        ax.set_xlabel('X (km)')
        ax.set_ylabel('Y (km)')
        ax.set_zlabel('Z (km)')
        ax.set_title('Keplerian Orbit Propagation (1 Period)')
        ax.legend()

        # 设置坐标轴等比例
        max_range = max(max(x_list) - min(x_list), max(y_list) - min(y_list), max(z_list) - min(z_list)) / 2
        mid_x = (max(x_list) + min(x_list)) / 2
        mid_y = (max(y_list) + min(y_list)) / 2
        mid_z = (max(z_list) + min(z_list)) / 2
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)

        plt.tight_layout()
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Result', '03_keplerian_propagation')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, 'orbit_propagation.png')
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  图像已保存: {save_path}")
        plt.close()

    except ImportError as e:
        print(f"\n  绘图需要安装 matplotlib 和 numpy: {e}")
        print(f"  运行: conda install matplotlib numpy")
