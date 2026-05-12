# -*- coding: utf-8 -*-
"""
第07章：TLE解析与传播
======================
学习解析两行根数 (TLE) 并使用 SGP4/SDP4 传播器。

本章学习目标：
    1. 理解 TLE 的格式和含义
    2. 学会解析和创建 TLE 对象
    3. 使用 TLEPropagator 传播 TLE 轨道
    4. 对比 TLE 传播和开普勒传播的区别

关键概念：
    - TLE 存储的是"平均轨道根数"（Mean Elements）
    - SGP4/SDP4 传播后输出"密切轨道根数"（Osculating Elements）
    - 开普勒传播仅考虑两体问题，不包含任何摄动

使用方法：
    python 07_tle_propagation.py
"""

import sys
import os
import math

# 导入 Orekit 初始化模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orekit_init import *

if __name__ == "__main__":
    print("=" * 60)
    print("  第07章：TLE解析与传播")
    print("=" * 60)

    # ============================================================
    # 示例1：创建 TLE 对象
    # ============================================================
    print("\n--- 示例1：创建 TLE 对象 ---")

    # TLE (Two-Line Element Set) 是描述人造卫星轨道的标准格式
    # 由美国太空司令部发布和维护
    #
    # 重要：TLE 中存储的是"平均轨道根数"（Mean Elements）
    # - 已经"平均掉"了短周期摄动（如 J2 项的周期性变化）
    # - 不能直接用于计算瞬时位置
    # - 必须通过 SGP4/SDP4 传播器转换为"密切轨道根数"
    #
    # 第1行包含：卫星编号、分类、历元时间、大气阻力项等
    # 第2行包含：倾角、升交点赤经、离心率、近地点幅角、平近点角、圈数

    # 国际空间站 (ISS) 的 TLE
    line1 = "1 25544U 98067A   24100.50000000  .00016717  00000-0  10270-3 0  9005"
    line2 = "2 25544  51.6400 200.0000 0005000  50.0000 310.0000 15.49000000400000"

    # TLE(line1, line2) 创建 TLE 对象
    # 参数：第1行字符串，第2行字符串
    tle = TLE(line1, line2)

    # 获取 TLE 的各个参数
    print(f"  卫星编号: {tle.getSatelliteNumber()}")     # 25544 = ISS
    print(f"  历元时间: {tle.getDate()}")                  # TLE 对应的时间
    print(f"  平均运动: {tle.getMeanMotion():.6f} rev/day")  # 每天绕地球圈数
    print(f"  离心率: {tle.getE():.6f}")                   # 轨道离心率
    print(f"  倾角: {tle.getI():.4f} deg")                 # 轨道倾角
    print(f"  升交点赤经: {tle.getRaan():.4f} deg")        # 升交点赤经
    print(f"  近地点幅角: {tle.getPerigeeArgument():.4f} deg")  # 近地点幅角
    print(f"  平近点角: {tle.getMeanAnomaly():.4f} deg")   # 平近点角
    print(f"  B*阻力项: {tle.getBStar():.6e} 1/m")        # 大气阻力参数

    # ============================================================
    # 示例2：创建 TLE 传播器
    # ============================================================
    print("\n--- 示例2：创建 TLE 传播器 ---")

    # TLEPropagator.selectExtrapolator(tle) 自动选择合适的传播器
    # 对于 LEO 卫星使用 SGP4，对于高轨卫星使用 SDP4
    #
    # SGP4/SDP4 的工作流程：
    #   平均根数 (TLE) --> SGP4/SDP4 --> 密切根数 (位置/速度)
    #
    # 传播器内部会：
    # 1. 从 TLE 读取平均轨道根数
    # 2. 应用大气阻力模型（通过 B* 参数）
    # 3. 应用地球扁率摄动（J2-J4）
    # 4. 输出密切轨道根数（瞬时位置和速度）
    propagator = TLEPropagator.selectExtrapolator(tle)

    # getInitialState() 获取传播器的初始状态
    initial_state = propagator.getInitialState()

    print(f"  传播器类型: {type(propagator).__name__}")

    # 将初始轨道转换为开普勒轨道以便查看
    orb_init = KeplerianOrbit(initial_state.getOrbit())
    print_orbit(orb_init, "TLE 初始轨道")

    # ============================================================
    # 示例3：传播 TLE
    # ============================================================
    print("\n--- 示例3：传播 TLE ---")

    # 创建目标时间：2024年4月11日 12:00:00 UTC
    target_date = create_date(2024, 4, 11, 12, 0, 0)

    # propagate(target_date) 传播到目标时间
    final_state = propagator.propagate(target_date)

    # 获取传播后的轨道并打印
    orb_final = KeplerianOrbit(final_state.getOrbit())
    print_orbit(orb_final, "传播 1 天后")

    # ============================================================
    # 示例4：传播多个时间点
    # ============================================================
    print("\n--- 示例4：传播多个时间点 ---")

    # tle.getDate() 获取 TLE 的历元时间
    epoch = tle.getDate()

    print(f"\n  {'时间(h)':<12} {'半长轴(km)':<15} {'离心率':<12} {'倾角(deg)':<12} {'高度(km)':<12}")
    print(f"  {'-'*65}")

    # 每 6 小时一个点，共 5 个点（0h, 6h, 12h, 18h, 24h）
    for i in range(5):
        # t = i * 6 * 3600.0 计算偏移秒数
        # 注意：使用浮点数 3600.0 而不是整数 3600
        t = i * 6 * 3600.0  # 每 6 小时一个点

        # epoch.shiftedBy(t) 创建偏移后的时间
        state = propagator.propagate(epoch.shiftedBy(t))

        # 获取轨道参数
        orb = KeplerianOrbit(state.getOrbit())

        # 计算高度（半长轴 - 地球半径）
        a_km = orb.getA() / 1000
        height = a_km - 6378.137  # 地球平均半径 (km)

        print(f"  {t/3600:<12.1f} {a_km:<15.3f} {orb.getE():<12.6f} {math.degrees(orb.getI()):<12.4f} {height:<12.3f}")

    # ============================================================
    # 示例5：与开普勒传播对比
    # ============================================================
    print("\n--- 示例5：TLE 传播 vs 开普勒传播 ---")

    # 创建开普勒传播器，从 TLE 轨道开始传播
    kep_propagator = KeplerianPropagator(orb_init)
    target_date = create_date(2024, 4, 11, 12, 0, 0)

    # 开普勒传播
    state_kep = kep_propagator.propagate(target_date)
    orb_kep = KeplerianOrbit(state_kep.getOrbit())

    # TLE 传播
    state_tle = propagator.propagate(target_date)
    orb_tle = KeplerianOrbit(state_tle.getOrbit())

    print(f"\n  {'参数':<20} {'TLE传播':<20} {'开普勒传播':<20} {'差异':<15}")
    print(f"  {'-'*75}")

    # 半长轴对比
    a_tle = orb_tle.getA() / 1000
    a_kep = orb_kep.getA() / 1000
    print(f"  {'半长轴(km)':<20} {a_tle:<20.3f} {a_kep:<20.3f} {a_tle-a_kep:<15.3f}")

    # 离心率对比
    e_tle = orb_tle.getE()
    e_kep = orb_kep.getE()
    print(f"  {'离心率':<20} {e_tle:<20.6f} {e_kep:<20.6f} {e_tle-e_kep:<15.6f}")

    # 倾角对比
    i_tle = math.degrees(orb_tle.getI())
    i_kep = math.degrees(orb_kep.getI())
    print(f"  {'倾角(deg)':<20} {i_tle:<20.4f} {i_kep:<20.4f} {i_tle-i_kep:<15.4f}")

    print("\n  注意：TLE 传播器包含大气阻力等摄动，开普勒传播仅考虑中心引力")
    print("  TLE 传播精度约 1km（LEO），适合短期预报；长期预报需要数值传播")
    print("\n  关键区别：")
    print("    - TLE 输入：平均轨道根数 (Mean Elements)")
    print("    - TLE 输出：密切轨道根数 (Osculating Elements)")
    print("    - 开普勒传播：始终使用密切轨道根数，无摄动")

    print("\n" + "=" * 60)
    print("  [OK] 第07章完成！")
    print("=" * 60)

    # ============================================================
    # 可视化：绘制 TLE 传播轨迹
    # ============================================================
    try:
        import matplotlib.pyplot as plt

        print("\n--- 绘制 TLE 传播轨迹 ---")

        # 收集 24 小时的轨迹点（每 10 分钟一个点）
        n_points = 144  # 24h * 6 points/h
        x_tle, y_tle, z_tle = [], [], []
        x_kep, y_kep, z_kep = [], [], []

        for i in range(n_points + 1):
            t = i * 600.0  # 10 分钟 = 600 秒

            # TLE 传播
            state_tle = propagator.propagate(epoch.shiftedBy(t))
            pv_tle = state_tle.getPVCoordinates()
            pos_tle = pv_tle.getPosition()
            x_tle.append(pos_tle.getX() / 1000)
            y_tle.append(pos_tle.getY() / 1000)
            z_tle.append(pos_tle.getZ() / 1000)

            # 开普勒传播
            state_kep = kep_propagator.propagate(epoch.shiftedBy(t))
            pv_kep = state_kep.getPVCoordinates()
            pos_kep = pv_kep.getPosition()
            x_kep.append(pos_kep.getX() / 1000)
            y_kep.append(pos_kep.getY() / 1000)
            z_kep.append(pos_kep.getZ() / 1000)

        # 创建图形
        fig = plt.figure(figsize=(12, 5))

        # 左图：3D 轨道对比
        ax1 = fig.add_subplot(121, projection='3d')
        ax1.plot(x_tle, y_tle, z_tle, 'b-', linewidth=1.5, label='TLE (SGP4)')
        ax1.plot(x_kep, y_kep, z_kep, 'r--', linewidth=1.5, label='Keplerian')
        ax1.set_xlabel('X (km)')
        ax1.set_ylabel('Y (km)')
        ax1.set_zlabel('Z (km)')
        ax1.set_title('TLE vs Keplerian (24h)')
        ax1.legend()

        # 右图：高度随时间变化
        ax2 = fig.add_subplot(122)
        times = [i * 10 / 60 for i in range(n_points + 1)]  # 小时
        heights_tle = [(math.sqrt(x**2 + y**2 + z**2) - 6378) for x, y, z in zip(x_tle, y_tle, z_tle)]
        heights_kep = [(math.sqrt(x**2 + y**2 + z**2) - 6378) for x, y, z in zip(x_kep, y_kep, z_kep)]

        ax2.plot(times, heights_tle, 'b-', linewidth=1.5, label='TLE (SGP4)')
        ax2.plot(times, heights_kep, 'r--', linewidth=1.5, label='Keplerian')
        ax2.set_xlabel('Time (hours)')
        ax2.set_ylabel('Altitude (km)')
        ax2.set_title('Altitude vs Time')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Result', '07_tle_propagation')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, 'tle_propagation.png')
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  图像已保存: {save_path}")
        plt.close()

    except ImportError as e:
        print(f"\n  绘图需要安装 matplotlib: {e}")
