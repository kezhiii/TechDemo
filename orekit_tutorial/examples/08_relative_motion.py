# -*- coding: utf-8 -*-
"""
第08章：卫星相对运动计算
========================
使用 Orekit 计算两颗卫星的相对运动（Hill/LVLH 坐标系）。

本章学习目标：
    1. 理解 Hill 坐标系（LVLH）的定义
    2. 使用 Orekit 计算惯性系差值
    3. 手动构建旋转矩阵变换到 Hill 坐标系
    4. 减去牵连速度得到 Hill 相对速度
    5. 可视化相对运动轨迹

Orekit 坐标系转换能力说明：
    - Orekit 提供 LocalOrbitalFrame 类用于创建 LVLH 坐标系
    - 但 LocalOrbitalFrame 构造函数需要 PVCoordinatesProvider 接口
    - KeplerianOrbit 不直接实现该接口，需要通过 propagator 获取状态
    - 因此本示例采用手动实现旋转矩阵的方式，更简洁直观

使用方法：
    python 08_relative_motion.py
"""

import sys
import os
import math
import numpy as np

# 导入 Orekit 初始化模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orekit_init import *


def inertial_to_hill(delta_r, delta_v, chief_elements, mu):
    """
    将惯性系差值转换到 Hill 坐标系

    参数:
        delta_r: 惯性系位置差 (Vector3D, m)
        delta_v: 惯性系速度差 (Vector3D, m/s)
        chief_elements: Chief 轨道根数 [a, e, i, Omega, omega, f]
        mu: 地球引力常数 (m^3/s^2)

    返回:
        hill_state: Hill 坐标系相对状态 [x, y, z, vx, vy, vz]
    """
    a, e, i, Omega, omega, f = chief_elements

    # 升交点角距
    u = omega + f

    # 轨道角速度
    n = math.sqrt(mu / a**3)

    # 313 欧拉角旋转矩阵
    Au = np.array([
        [math.cos(u), math.sin(u), 0],
        [-math.sin(u), math.cos(u), 0],
        [0, 0, 1]
    ])
    Ai = np.array([
        [1, 0, 0],
        [0, math.cos(i), math.sin(i)],
        [0, -math.sin(i), math.cos(i)]
    ])
    AOMG = np.array([
        [math.cos(Omega), math.sin(Omega), 0],
        [-math.sin(Omega), math.cos(Omega), 0],
        [0, 0, 1]
    ])
    A = Au @ Ai @ AOMG

    # 变换到 Hill 坐标系
    delta_r_arr = np.array([delta_r.getX(), delta_r.getY(), delta_r.getZ()])
    delta_v_arr = np.array([delta_v.getX(), delta_v.getY(), delta_v.getZ()])

    pos_hill = A @ delta_r_arr
    vel_hill_raw = A @ delta_v_arr

    # 减去牵连速度（Hill 坐标系中的旋转效应）
    transport = np.array([-n * pos_hill[1], n * pos_hill[0], 0])
    vel_hill = vel_hill_raw - transport

    return np.concatenate((pos_hill, vel_hill))


def compute_relative_state(chief_orbit, deputy_orbit, date, mu):
    """
    计算两颗卫星的相对状态

    参数:
        chief_orbit: Chief 轨道对象
        deputy_orbit: Deputy 轨道对象
        date: 时间
        mu: 地球引力常数

    返回:
        hill_state: Hill 坐标系相对状态
    """
    # 获取惯性系位置/速度
    chief_pv = chief_orbit.getPVCoordinates()
    deputy_pv = deputy_orbit.getPVCoordinates()

    # 计算惯性系差值
    delta_r = Vector3D(
        deputy_pv.getPosition().getX() - chief_pv.getPosition().getX(),
        deputy_pv.getPosition().getY() - chief_pv.getPosition().getY(),
        deputy_pv.getPosition().getZ() - chief_pv.getPosition().getZ()
    )
    delta_v = Vector3D(
        deputy_pv.getVelocity().getX() - chief_pv.getVelocity().getX(),
        deputy_pv.getVelocity().getY() - chief_pv.getVelocity().getY(),
        deputy_pv.getVelocity().getZ() - chief_pv.getVelocity().getZ()
    )

    # 提取 Chief 轨道根数
    chief_kep = KeplerianOrbit(chief_orbit)
    chief_elements = [
        chief_kep.getA(),
        chief_kep.getE(),
        chief_kep.getI(),
        chief_kep.getRightAscensionOfAscendingNode(),
        chief_kep.getPerigeeArgument(),
        chief_kep.getTrueAnomaly()
    ]

    # 转换到 Hill 坐标系
    return inertial_to_hill(delta_r, delta_v, chief_elements, mu)


if __name__ == "__main__":
    print("=" * 60)
    print("  第08章：卫星相对运动计算")
    print("=" * 60)

    # ============================================================
    # 参数设置
    # ============================================================
    date = create_date(2024, 1, 1, 12, 0, 0)
    mu = Constants.EGM96_EARTH_MU
    gcrf = FramesFactory.getGCRF()

    # Chief 卫星轨道参数（圆轨道，高度 500km）
    chief_a = 6_878_000.0       # 半长轴 (m)
    chief_e = 0.001             # 离心率
    chief_i = math.radians(51.6)  # 倾角 (rad)

    # Deputy 卫星轨道参数（近距离编队，小偏差）
    # 注意：Hill/CW 方程适用于近距离编队（相对距离 << 轨道半径）
    deputy_a = 6_878_100.0      # 半长轴略大 100m
    deputy_e = 0.00105          # 离心率略大
    deputy_i = math.radians(51.61)  # 倾角略大 0.01 度

    print(f"\n  Chief 轨道: a={chief_a/1000:.1f} km, e={chief_e}, i={math.degrees(chief_i):.1f} deg")
    print(f"  Deputy 轨道: a={deputy_a/1000:.1f} km, e={deputy_e}, i={math.degrees(deputy_i):.2f} deg")
    print(f"  注意：使用小偏差参数，确保相对距离在 Hill 方程适用范围内")

    # ============================================================
    # 步骤1：创建 Chief 和 Deputy 轨道
    # ============================================================
    print("\n--- 步骤1：创建轨道对象 ---")

    # Chief 轨道
    chief_orbit = KeplerianOrbit(
        chief_a, chief_e, chief_i,
        math.radians(90.0),     # 近地点幅角
        0.0,                    # 升交点赤经
        0.0,                    # 真近点角
        PositionAngle.TRUE, gcrf, date, mu
    )

    # Deputy 轨道（有小偏差）
    deputy_orbit = KeplerianOrbit(
        deputy_a, deputy_e, deputy_i,
        math.radians(90.0),
        0.0,
        math.radians(0.5),    # 真近点角偏移 0.5 度（小角度）
        PositionAngle.TRUE, gcrf, date, mu
    )

    print_orbit(chief_orbit, "Chief 轨道")
    print_orbit(deputy_orbit, "Deputy 轨道")

    # ============================================================
    # 步骤2：计算初始相对状态
    # ============================================================
    print("\n--- 步骤2：计算初始相对状态 ---")

    hill_state = compute_relative_state(chief_orbit, deputy_orbit, date, mu)

    print(f"\n  初始相对状态 (Hill 坐标系):")
    print(f"    相对位置 (m):")
    print(f"      x (径向)  = {hill_state[0]:.3f}")
    print(f"      y (横向)  = {hill_state[1]:.3f}")
    print(f"      z (法向)  = {hill_state[2]:.3f}")
    print(f"    相对速度 (m/s):")
    print(f"      vx = {hill_state[3]:.6f}")
    print(f"      vy = {hill_state[4]:.6f}")
    print(f"      vz = {hill_state[5]:.6f}")

    # ============================================================
    # 步骤3：传播并计算相对运动轨迹
    # ============================================================
    print("\n--- 步骤3：传播并计算相对运动轨迹 ---")

    # 传播参数
    period = chief_orbit.getKeplerianPeriod()
    n_orbits = 2  # 传播 2 个周期
    n_points = 200  # 每个周期 100 个点

    print(f"  轨道周期: {period:.2f} s ({period/60:.2f} min)")
    print(f"  传播 {n_orbits} 个周期，共 {n_orbits * n_points} 个点")

    # 创建传播器
    chief_propagator = KeplerianPropagator(chief_orbit)
    deputy_propagator = KeplerianPropagator(deputy_orbit)

    # 存储相对运动数据
    times = []
    rel_x, rel_y, rel_z = [], [], []

    for i in range(n_orbits * n_points + 1):
        t = i * period * n_orbits / (n_orbits * n_points)
        current_date = date.shiftedBy(t)

        # 传播 Chief 和 Deputy
        chief_state = chief_propagator.propagate(current_date)
        deputy_state = deputy_propagator.propagate(current_date)

        # 获取传播后的轨道
        chief_orbit_cur = KeplerianOrbit(chief_state.getOrbit())
        deputy_orbit_cur = KeplerianOrbit(deputy_state.getOrbit())

        # 计算相对状态
        hill = compute_relative_state(chief_orbit_cur, deputy_orbit_cur, current_date, mu)

        # 存储数据
        times.append(t / 60)  # 转换为分钟
        rel_x.append(hill[0])
        rel_y.append(hill[1])
        rel_z.append(hill[2])

    print(f"  相对运动轨迹计算完成")

    # ============================================================
    # 步骤4：可视化
    # ============================================================
    print("\n--- 步骤4：绘制相对运动轨迹 ---")

    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        fig = plt.figure(figsize=(14, 5))

        # 左图：3D 相对运动轨迹
        ax1 = fig.add_subplot(131, projection='3d')
        ax1.plot(rel_x, rel_y, rel_z, 'b-', linewidth=1.5)
        ax1.scatter([rel_x[0]], [rel_y[0]], [rel_z[0]], c='green', s=100, label='Start')
        ax1.scatter([rel_x[-1]], [rel_y[-1]], [rel_z[-1]], c='red', s=100, label='End')
        ax1.set_xlabel('x - Radial (m)')
        ax1.set_ylabel('y - Along-track (m)')
        ax1.set_zlabel('z - Cross-track (m)')
        ax1.set_title('Relative Motion (3D)')
        ax1.legend()

        # 中图：x-y 平面投影（径向-横向）
        ax2 = fig.add_subplot(132)
        ax2.plot(rel_x, rel_y, 'b-', linewidth=1.5)
        ax2.scatter([rel_x[0]], [rel_y[0]], c='green', s=100, label='Start')
        ax2.scatter([rel_x[-1]], [rel_y[-1]], c='red', s=100, label='End')
        ax2.set_xlabel('x - Radial (m)')
        ax2.set_ylabel('y - Along-track (m)')
        ax2.set_title('Radial vs Along-track')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_aspect('equal')

        # 右图：各分量随时间变化
        ax3 = fig.add_subplot(133)
        ax3.plot(times, rel_x, 'r-', linewidth=1.5, label='x (Radial)')
        ax3.plot(times, rel_y, 'g-', linewidth=1.5, label='y (Along-track)')
        ax3.plot(times, rel_z, 'b-', linewidth=1.5, label='z (Cross-track)')
        ax3.set_xlabel('Time (min)')
        ax3.set_ylabel('Relative Position (m)')
        ax3.set_title('Relative Position vs Time')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        plt.tight_layout()

        # 保存图像
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Result', '08_relative_motion')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, 'relative_motion.png')
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  图像已保存: {save_path}")
        plt.close()

    except ImportError as e:
        print(f"\n  绘图需要安装 matplotlib: {e}")

    # ============================================================
    # 步骤5：Clohessy-Wiltshire 方程验证
    # ============================================================
    print("\n--- 步骤5：Clohessy-Wiltshire 方程验证 ---")

    # 初始相对状态
    x0 = hill_state[0]
    y0 = hill_state[1]
    z0 = hill_state[2]
    vx0 = hill_state[3]
    vy0 = hill_state[4]
    vz0 = hill_state[5]

    # 轨道角速度
    n = math.sqrt(mu / chief_a**3)

    print(f"  初始相对状态:")
    print(f"    x0 = {x0:.3f} m, vx0 = {vx0:.6f} m/s")
    print(f"    y0 = {y0:.3f} m, vy0 = {vy0:.6f} m/s")
    print(f"    z0 = {z0:.3f} m, vz0 = {vz0:.6f} m/s")
    print(f"    n = {n:.6f} rad/s")

    # CW 方程解析解（圆轨道近似）
    print(f"\n  Clohessy-Wiltshire 方程解析解:")
    print(f"    x(t) = (4-3cos(nt))*x0 + (sin(nt)/n)*vx0 + (2/n)*(1-cos(nt))*vy0")
    print(f"    y(t) = 6*(sin(nt)-nt)*x0 + (2/n)*(cos(nt)-1)*vx0 + (4*sin(nt)-3*nt)*y0 + (vy0/n)*(1-cos(nt))")
    print(f"    z(t) = z0*cos(nt) + (vz0/n)*sin(nt)")

    print("\n" + "=" * 60)
    print("  [OK] 第08章完成！")
    print("=" * 60)
