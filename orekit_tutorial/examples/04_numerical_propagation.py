# -*- coding: utf-8 -*-
"""
第04章：数值传播与力学模型对比
==============================
使用数值传播器进行轨道传播，并对比不同力学模型的组合效果。

本章学习目标：
    1. 理解数值传播器与开普勒传播器的区别
    2. 学会使用 DormandPrince853Integrator 积分器
    3. 添加多种力学模型并观察其影响
    4. 对比不同摄动组合对轨道的影响

使用方法：
    python 04_numerical_propagation.py
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
    print("  第04章：数值传播与力学模型对比")
    print("=" * 60)

    # 创建公共时间对象
    date = create_date(2024, 1, 1, 12, 0, 0)

    # 地球引力常数
    mu = Constants.EGM96_EARTH_MU

    # 获取地心惯性参考系
    gcrf = FramesFactory.getGCRF()

    # ============================================================
    # 示例1：创建数值传播器
    # ============================================================
    print("\n--- 示例1：创建数值传播器 ---")

    # 创建初始轨道
    orbit = KeplerianOrbit(
        7_000_000.0,            # 半长轴 7000 km
        0.001,                  # 离心率
        math.radians(98.0),     # 倾角 98 deg
        math.radians(90.0),     # 近地点幅角
        0.0,                    # 升交点赤经
        0.0,                    # 真近点角
        PositionAngle.TRUE,     # 角度类型
        gcrf,                   # 参考坐标系
        date,                   # 历元时间
        mu                      # 引力常数
    )

    # DormandPrince853Integrator 是一种 Runge-Kutta 数值积分器
    # 它通过数值方法求解轨道运动的微分方程
    # 参数说明：
    #   1.0    - 最小步长 (s)：积分器可以使用的最小时间步长
    #   600.0  - 最大步长 (s)：积分器可以使用的最大时间步长
    #   1.0e-9 - 绝对精度 (m)：位置误差容限
    #   1.0e-12 - 相对精度：速度误差容限
    integrator = DormandPrince853Integrator(
        1.0,        # 最小步长 (s)
        600.0,      # 最大步长 (s)
        1.0e-9,     # 绝对精度
        1.0e-12     # 相对精度
    )

    # NumericalPropagator 使用数值积分器传播轨道
    # 与 KeplerianPropagator 不同，它可以添加各种力学模型
    propagator = NumericalPropagator(integrator)

    # setOrbitType() 设置内部使用的轨道表示类型
    # EQUINOCTIAL（等角轨道）对于近圆轨道更稳定
    propagator.setOrbitType(OrbitType.EQUINOCTIAL)

    # SpacecraftState(orbit, mass) 创建航天器状态
    # mass = 100.0 kg（航天器质量）
    initial_state = SpacecraftState(orbit, 100.0)

    # setInitialState() 设置传播的初始状态
    propagator.setInitialState(initial_state)

    # addForceModel() 添加力学模型
    # NewtonianAttraction(mu) 是最基本的力学模型：中心引力
    # 这相当于开普勒传播器的效果
    propagator.addForceModel(NewtonianAttraction(mu))

    print_orbit(orbit, "初始轨道")

    # ============================================================
    # 示例2：仅中心引力传播
    # ============================================================
    print("\n--- 示例2：仅中心引力传播 ---")

    period = orbit.getKeplerianPeriod()
    target_date = date.shiftedBy(period / 2)

    # propagate() 执行传播，返回目标时间的状态
    final_state = propagator.propagate(target_date)
    print_orbit(final_state.getOrbit(), "传播半个周期后")

    # ============================================================
    # 示例3：添加重力场摄动 + 大气阻力 + 日月引力
    # ============================================================
    print("\n--- 示例3：添加多种摄动 ---")

    # 重新创建传播器（因为传播器不能重用）
    propagator_j2 = NumericalPropagator(integrator)
    propagator_j2.setOrbitType(OrbitType.EQUINOCTIAL)
    propagator_j2.setInitialState(initial_state)

    # 添加中心引力
    propagator_j2.addForceModel(NewtonianAttraction(mu))

    # 导入重力场模型类
    # HolmesFeatherstoneAttractionModel 使用球谐展开描述地球非球形引力
    from org.orekit.forces.gravity import HolmesFeatherstoneAttractionModel
    # GravityFieldFactory 用于加载重力场模型数据
    from org.orekit.forces.gravity.potential import GravityFieldFactory
    from org.orekit.utils import IERSConventions

    # 创建 ITRF 坐标系（国际地球参考系）
    # HolmesFeatherstoneAttractionModel 需要在地固系中计算
    itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)

    # getNormalizedProvider(6, 6) 加载 6x6 阶归一化重力场模型
    # 第一个 6 是最大阶数，第二个 6 是最大次数
    # 阶数越高越精确，但计算量越大
    provider = GravityFieldFactory.getNormalizedProvider(6, 6)

    # 创建重力场力学模型
    # 参数：地固系坐标系，重力场提供者
    hf_model = HolmesFeatherstoneAttractionModel(itrf, provider)

    # 添加到传播器
    propagator_j2.addForceModel(hf_model)

    # ----------------------------------------------------------
    # 添加大气阻力（对低轨卫星影响很大）
    # ----------------------------------------------------------
    # 导入大气阻力相关类
    from org.orekit.models.earth.atmosphere import HarrisPriester
    from org.orekit.forces.drag import DragForce, IsotropicDrag

    # HarrisPriester 大气密度模型
    # 参数：太阳天体，地球椭球体
    # 需要地球椭球体用于计算高度
    from org.orekit.bodies import OneAxisEllipsoid
    earth = OneAxisEllipsoid(
        Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
        Constants.WGS84_EARTH_FLATTENING,
        itrf
    )
    sun = CelestialBodyFactory.getSun()
    atmosphere = HarrisPriester(sun, earth)

    # IsotropicDrag 定义航天器的阻力特性
    # 参数：
    #   0.01 - 有效截面积 (m^2)
    #   2.2  - 阻力系数 Cd（典型值 2.0-2.5）
    sc_drag = IsotropicDrag(0.01, 2.2)

    # DragForce 创建大气阻力模型
    drag_force = DragForce(atmosphere, sc_drag)
    propagator_j2.addForceModel(drag_force)

    # ----------------------------------------------------------
    # 添加日月引力（第三体引力）
    # ----------------------------------------------------------
    # CelestialBodyFactory 获取天体对象
    from org.orekit.forces.gravity import ThirdBodyAttraction
    moon = CelestialBodyFactory.getMoon()

    # ThirdBodyAttraction 创建第三体引力模型
    # 太阳和月球的引力会扰动卫星轨道
    propagator_j2.addForceModel(ThirdBodyAttraction(sun))
    propagator_j2.addForceModel(ThirdBodyAttraction(moon))

    print(f"  添加的摄动模型:")
    print(f"    - 地球重力场 (6x6 阶)")
    print(f"    - 大气阻力 (HarrisPriester 模型, Cd=2.2)")
    print(f"    - 日月引力 (太阳 + 月球)")

    # # ----------------------------------------------------------
    # # 太阳光压
    # # ----------------------------------------------------------
    # from org.orekit.forces.radiation import SolarRadiationPressure, IsotropicRadiationSingleCoefficient

    # # IsotropicRadiationSingleCoefficient 定义航天器的光压特性
    # # 参数：
    # #   0.01 - 有效截面积 (m^2)
    # #   1.5  - 光压系数 Cr（典型值 1.0-2.0）
    # sc_srp = IsotropicRadiationSingleCoefficient(0.01, 1.5)

    # # SolarRadiationPressure 构造函数签名：
    # # SolarRadiationPressure(CelestialBody sun, double equatorialRadius, RadiationSensitive spacecraft)
    # # 第二个参数是地球赤道半径（遮挡天体的半径），不是天体对象
    # earth_radius = Constants.WGS84_EARTH_EQUATORIAL_RADIUS
    # srp_force = SolarRadiationPressure(sun, earth_radius, sc_srp)
    # propagator_j2.addForceModel(srp_force)
    # print(f"    - 太阳光压 (Cr=1.5)")



    # 传播
    final_state_j2 = propagator_j2.propagate(target_date)
    print_orbit(final_state_j2.getOrbit(), "多种摄动传播半个周期后")

    # ============================================================
    # 示例4：对比有无摄动的结果
    # ============================================================
    print("\n--- 示例4：摄动影响对比 ---")

    # KeplerianOrbit() 可以将任意轨道对象转换为开普勒轨道
    # 这样可以方便地获取六个开普勒要素
    orb_no_pert = KeplerianOrbit(final_state.getOrbit())
    orb_j2 = KeplerianOrbit(final_state_j2.getOrbit())

    print(f"  {'参数':<20} {'无摄动':<20} {'重力场摄动':<20} {'差异':<15}")
    print(f"  {'-'*75}")

    # getA() 返回半长轴（米）
    a_no = orb_no_pert.getA() / 1000
    a_j2 = orb_j2.getA() / 1000
    print(f"  {'半长轴(km)':<20} {a_no:<20.6f} {a_j2:<20.6f} {a_j2-a_no:<15.6f}")

    # getE() 返回离心率
    e_no = orb_no_pert.getE()
    e_j2 = orb_j2.getE()
    print(f"  {'离心率':<20} {e_no:<20.6f} {e_j2:<20.6f} {e_j2-e_no:<15.6f}")

    # getI() 返回倾角（弧度），math.degrees() 转换为角度
    i_no = math.degrees(orb_no_pert.getI())
    i_j2 = math.degrees(orb_j2.getI())
    print(f"  {'倾角(deg)':<20} {i_no:<20.6f} {i_j2:<20.6f} {i_j2-i_no:<15.6f}")

    # getRightAscensionOfAscendingNode() 返回升交点赤经（弧度）
    raan_no = math.degrees(orb_no_pert.getRightAscensionOfAscendingNode())
    raan_j2 = math.degrees(orb_j2.getRightAscensionOfAscendingNode())
    print(f"  {'升交点赤经(deg)':<20} {raan_no:<20.6f} {raan_j2:<20.6f} {raan_j2-raan_no:<15.6f}")

    # getPerigeeArgument() 返回近地点幅角（弧度）
    omega_no = math.degrees(orb_no_pert.getPerigeeArgument())
    omega_j2 = math.degrees(orb_j2.getPerigeeArgument())
    print(f"  {'近地点幅角(deg)':<20} {omega_no:<20.6f} {omega_j2:<20.6f} {omega_j2-omega_no:<15.6f}")

    print("\n  注意：重力场摄动主要影响升交点赤经和近地点幅角的进动")

    # ============================================================
    # 示例5：传播多个周期
    # ============================================================
    print("\n--- 示例5：传播 10 个周期 ---")

    # 创建新的传播器用于多周期传播
    propagator_j2_10 = NumericalPropagator(integrator)
    propagator_j2_10.setOrbitType(OrbitType.EQUINOCTIAL)
    propagator_j2_10.setInitialState(initial_state)
    propagator_j2_10.addForceModel(NewtonianAttraction(mu))

    # 添加重力场摄动
    itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
    provider = GravityFieldFactory.getNormalizedProvider(6, 6)
    hf_model = HolmesFeatherstoneAttractionModel(itrf, provider)
    propagator_j2_10.addForceModel(hf_model)

    # 添加大气阻力
    propagator_j2_10.addForceModel(drag_force)

    # 添加日月引力
    propagator_j2_10.addForceModel(ThirdBodyAttraction(sun))
    propagator_j2_10.addForceModel(ThirdBodyAttraction(moon))

    print(f"\n  {'周期数':<10} {'半长轴(km)':<15} {'离心率':<12} {'倾角(deg)':<12} {'RAAN(deg)':<12}")
    print(f"  {'-'*65}")

    for n in range(11):
        t = n * period
        state = propagator_j2_10.propagate(date.shiftedBy(t))
        orb = state.getOrbit()

        # 将轨道转换为开普勒轨道以获取完整参数
        kep = KeplerianOrbit(orb)
        a = kep.getA() / 1000
        e = kep.getE()
        i = math.degrees(kep.getI())
        raan = math.degrees(kep.getRightAscensionOfAscendingNode())

        print(f"  {n:<10} {a:<15.3f} {e:<12.6f} {i:<12.4f} {raan:<12.4f}")

    print("\n" + "=" * 60)
    print("  [OK] 第04章完成！")
    print("=" * 60)

    # ============================================================
    # 多场景对比：不同力学模型组合的效果
    # ============================================================
    print("\n" + "=" * 60)
    print("  附录：多种力学模型组合对比")
    print("=" * 60)

    # 场景1：仅中心引力（开普勒轨道）
    print("\n--- 场景1：仅中心引力 ---")
    integrator_s1 = DormandPrince853Integrator(1.0, 600.0, 1.0e-9, 1.0e-12)
    propagator_s1 = NumericalPropagator(integrator_s1)
    propagator_s1.setOrbitType(OrbitType.EQUINOCTIAL)
    propagator_s1.setInitialState(SpacecraftState(orbit, 100.0))
    propagator_s1.addForceModel(NewtonianAttraction(mu))

    state_s1 = propagator_s1.propagate(date.shiftedBy(period))
    orb_s1 = KeplerianOrbit(state_s1.getOrbit())
    print_orbit(orb_s1, "场景1：中心引力")

    # 场景2：中心引力 + 重力场
    print("\n--- 场景2：中心引力 + 重力场 (6x6) ---")
    integrator_s2 = DormandPrince853Integrator(1.0, 600.0, 1.0e-9, 1.0e-12)
    propagator_s2 = NumericalPropagator(integrator_s2)
    propagator_s2.setOrbitType(OrbitType.EQUINOCTIAL)
    propagator_s2.setInitialState(SpacecraftState(orbit, 100.0))
    propagator_s2.addForceModel(NewtonianAttraction(mu))
    propagator_s2.addForceModel(HolmesFeatherstoneAttractionModel(itrf, provider))

    state_s2 = propagator_s2.propagate(date.shiftedBy(period))
    orb_s2 = KeplerianOrbit(state_s2.getOrbit())
    print_orbit(orb_s2, "场景2：+重力场")

    # 场景3：中心引力 + 重力场 + 日月引力
    print("\n--- 场景3：中心引力 + 重力场 + 日月引力 ---")
    integrator_s3 = DormandPrince853Integrator(1.0, 600.0, 1.0e-9, 1.0e-12)
    propagator_s3 = NumericalPropagator(integrator_s3)
    propagator_s3.setOrbitType(OrbitType.EQUINOCTIAL)
    propagator_s3.setInitialState(SpacecraftState(orbit, 100.0))
    propagator_s3.addForceModel(NewtonianAttraction(mu))
    propagator_s3.addForceModel(HolmesFeatherstoneAttractionModel(itrf, provider))
    propagator_s3.addForceModel(ThirdBodyAttraction(sun))
    propagator_s3.addForceModel(ThirdBodyAttraction(moon))

    state_s3 = propagator_s3.propagate(date.shiftedBy(period))
    orb_s3 = KeplerianOrbit(state_s3.getOrbit())
    print_orbit(orb_s3, "场景3：+日月引力")

    # 对比结果
    print("\n--- 三种场景对比结果 ---")
    print(f"\n  {'参数':<20} {'场景1':<18} {'场景2':<18} {'场景3':<18}")
    print(f"  {'-'*75}")

    params = [
        ("半长轴(km)", lambda o: o.getA()/1000),
        ("离心率", lambda o: o.getE()),
        ("倾角(deg)", lambda o: math.degrees(o.getI())),
        ("RAAN(deg)", lambda o: math.degrees(o.getRightAscensionOfAscendingNode())),
        ("近地点幅角(deg)", lambda o: math.degrees(o.getPerigeeArgument())),
    ]

    for name, func in params:
        v1 = func(orb_s1)
        v2 = func(orb_s2)
        v3 = func(orb_s3)
        if isinstance(v1, float) and abs(v1) > 100:
            print(f"  {name:<20} {v1:<18.3f} {v2:<18.3f} {v3:<18.3f}")
        else:
            print(f"  {name:<20} {v1:<18.6f} {v2:<18.6f} {v3:<18.6f}")

    print("\n" + "=" * 60)

    # ============================================================
    # 可视化：对比有无摄动的轨道
    # ============================================================
    try:
        import matplotlib.pyplot as plt
        import numpy as np

        print("\n--- 绘制轨道对比图 ---")

        n_plot = 200

        # 无摄动轨道
        x1, y1, z1 = [], [], []
        for i in range(n_plot + 1):
            t = i * period / n_plot
            state = propagator.propagate(date.shiftedBy(t))
            pv = state.getPVCoordinates()
            pos = pv.getPosition()
            x1.append(pos.getX() / 1000)
            y1.append(pos.getY() / 1000)
            z1.append(pos.getZ() / 1000)

        # 有摄动轨道
        x2, y2, z2 = [], [], []
        for i in range(n_plot + 1):
            t = i * period / n_plot
            state = propagator_j2.propagate(date.shiftedBy(t))
            pv = state.getPVCoordinates()
            pos = pv.getPosition()
            x2.append(pos.getX() / 1000)
            y2.append(pos.getY() / 1000)
            z2.append(pos.getZ() / 1000)

        # 创建 3D 图形
        fig = plt.figure(figsize=(12, 5))

        # 左图：3D 轨道对比
        ax1 = fig.add_subplot(121, projection='3d')
        ax1.plot(x1, y1, z1, 'b-', linewidth=1.5, label='No Perturbation')
        ax1.plot(x2, y2, z2, 'r-', linewidth=1.5, label='With Gravity Field')
        ax1.set_xlabel('X (km)')
        ax1.set_ylabel('Y (km)')
        ax1.set_zlabel('Z (km)')
        ax1.set_title('Orbit Comparison (3D)')
        ax1.legend()

        # 右图：X-Y 平面投影
        ax2 = fig.add_subplot(122)
        ax2.plot(x1, y1, 'b-', linewidth=1.5, label='No Perturbation')
        ax2.plot(x2, y2, 'r-', linewidth=1.5, label='With Gravity Field')
        ax2.set_xlabel('X (km)')
        ax2.set_ylabel('Y (km)')
        ax2.set_title('Orbit Comparison (X-Y Plane)')
        ax2.legend()
        ax2.set_aspect('equal')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Result', '04_numerical_propagation')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, 'orbit_comparison.png')
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  图像已保存: {save_path}")
        plt.close()  # 关闭图形，避免阻塞

    except ImportError as e:
        print(f"\n  绘图需要安装 matplotlib 和 numpy: {e}")
