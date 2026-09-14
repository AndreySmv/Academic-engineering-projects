import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
import math
from matplotlib.animation import FuncAnimation
import warnings
warnings.filterwarnings('ignore')

def solve_mechanism(phi_deg, tolerance=1e-9):
    """
    Решение системы уравнений механизма для заданного угла phi (в градусах)
    """
    # Параметры механизма
    r = 10.0
    b = 25.0
    c = 20.0
    d = 20.0
    e = 62.0
    f = 62.0
    g = 35.3
    x0 = 22.0
    y0 = 35.0
    y5_fixed = 15.0  
    y6_fixed = 55.0
    
    # Преобразуем угол в радианы
    phi = math.radians(phi_deg)
    
    # Координаты эксцентрика (известны)
    x1 = x0 + r * math.cos(phi)
    y1 = y0 + r * math.sin(phi)
    
    # Система уравнений для неизвестных переменных
    def equations(vars):
        x2, y2, x3, y3, x4, y4, x5, x6 = vars
        
        eq = np.zeros(8)
        
        # 1. Уравнение синхронизирующего рычага
        eq[0] = x2**2 + y2**2 - g**2
        
        # 2. Ножка Т-качалки (эксцентрик - центр Т)
        eq[1] = (x2 - x1)**2 + (y2 - y1)**2 - b**2
        
        # 3. Левая часть перекладины Т-качалки (центр Т - точка 3)
        eq[2] = (x2 - x3)**2 + (y2 - y3)**2 - c**2
        
        # 4. Правая часть перекладины Т-качалки (центр Т - точка 4)
        eq[3] = (x4 - x2)**2 + (y4 - y2)**2 - d**2
        
        # 5. Перекладина целиком (точка 3 - точка 4)
        eq[4] = (x4 - x3)**2 + (y4 - y3)**2 - (c + d)**2
        
        # 6. Связь эксцентрика с левым концом перекладины
        eq[5] = (x3 - x1)**2 + (y3 - y1)**2 - (c**2 + b**2)
        
        # 7. Шатун первого поршня (точка 3 - поршень 6)
        eq[6] = (x6 - x3)**2 + (y6_fixed - y3)**2 - e**2
        
        # 8. Шатун второго поршня (точка 4 - поршень 5)
        eq[7] = (x5 - x4)**2 + (y5_fixed - y4)**2 - f**2
        
        return eq
    
    # Начальные приближения
    if phi_deg % 360 < 180:
        # Для первой половины оборота
        x2_guess = -10
        y2_guess = 35
        x3_guess = -10
        y3_guess = 40.0
        x4_guess = -10
        y4_guess = 5
    else:
        # Для второй половины оборота
        x2_guess = -10
        y2_guess = 20
        x3_guess = -10
        y3_guess = 30.0
        x4_guess = -10
        y4_guess = 5
    
    x5_guess = -50.0
    x6_guess = -50.0
    
    initial_guess = [x2_guess, y2_guess, x3_guess, y3_guess, x4_guess, y4_guess, x5_guess, x6_guess]
    
    # Решение системы уравнений
    try:
        solution = fsolve(equations, initial_guess, xtol=tolerance, maxfev=1000)
        x2, y2, x3, y3, x4, y4, x5, x6 = solution
        
        # Проверяем физическую реализуемость решения
        if abs(y2) > 100 or abs(x3) > 100 or abs(x4) > 100:
            return None
            
        result = {
            'phi_deg': phi_deg,
            'phi_rad': phi,
            'x0': x0, 'y0': y0,
            'x1': x1, 'y1': y1,
            'x2': x2, 'y2': y2,
            'x3': x3, 'y3': y3,
            'x4': x4, 'y4': y4,
            'x5': x5, 'y5': y5_fixed,
            'x6': x6, 'y6': y6_fixed,
            'convergence': True
        }
        return result
        
    except Exception as e:
        return None

def create_animation_original():
    """Создание анимации для 5 периодов обращения (оригинальная версия)"""
    print("Создание ОРИГИНАЛЬНОЙ анимации для 5 периодов обращения...")
    
    # Углы для анимации (5 периодов = 1800 градусов)
    angles = np.linspace(0, 1800, 361)
    
    # Собираем данные для анимации
    frames_data = []
    valid_angles = []
    
    for phi in angles:
        result = solve_mechanism(phi % 360)
        if result is not None:
            frames_data.append(result)
            valid_angles.append(phi)
        else:
            print(f"Пропущен угол {phi}°")
    
    if not frames_data:
        print("Не удалось получить данные для анимации")
        return
    
    print(f"Собрано {len(frames_data)} кадров из {len(angles)} возможных")
    
    # Создаем фигуру для анимации
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Настраиваем первый график (механизм)
    ax1.set_xlim(-80, 50)
    ax1.set_ylim(-10, 80)
    ax1.set_xlabel('X координата', fontsize=12)
    ax1.set_ylabel('Y координата', fontsize=12)
    ax1.set_title('Анимация механизма с Т-качалкой', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal', adjustable='box')
    
    # Настраиваем второй график (траектории поршней)
    ax2.set_xlim(0, 1800)
    ax2.set_ylim(-80, 10)
    ax2.set_xlabel('Угол φ, градусы', fontsize=12)
    ax2.set_ylabel('X координата поршней', fontsize=12)
    ax2.set_title('Траектории движения поршней', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Инициализируем элементы для анимации
    # Механизм
    circle_traj, = ax1.plot([], [], 'gray', linestyle='--', alpha=0.5)
    sync_rod, = ax1.plot([], [], 'b-', linewidth=3, label='Синхронизирующий рычаг')
    t_leg, = ax1.plot([], [], 'r-', linewidth=2, label='Ножка Т-качалки')
    t_crossbar, = ax1.plot([], [], 'g-', linewidth=2, label='Т-качалка')
    rod1, = ax1.plot([], [], 'm-', linewidth=2, label='Шатун 1 (к поршню 1)')
    rod2, = ax1.plot([], [], 'c-', linewidth=2, label='Шатун 2 (к поршню 2)')
    
    # Поршни (прямоугольники)
    piston1 = plt.Rectangle((0, 0), 5, 20, color='darkblue', alpha=0.7)
    piston2 = plt.Rectangle((0, 0), 5, 20, color='darkred', alpha=0.7)
    ax1.add_patch(piston1)
    ax1.add_patch(piston2)
    
    # Точки
    points = []
    for i in range(7):
        point, = ax1.plot([], [], 'o', markersize=8)
        points.append(point)
    
    # Траектории
    x5_line, = ax2.plot([], [], 'c-', linewidth=2, label='x5 (поршень 2)')
    x6_line, = ax2.plot([], [], 'm-', linewidth=2, label='x6 (поршень 1)')
    current_angle_line = ax2.axvline(x=0, color='r', linestyle='--', alpha=0.5)
    
    # Собираем историю для траекторий
    history_x5 = []
    history_x6 = []
    history_angles = []
    
    def init():
        """Инициализация анимации"""
        circle_traj.set_data([], [])
        sync_rod.set_data([], [])
        t_leg.set_data([], [])
        t_crossbar.set_data([], [])
        rod1.set_data([], [])
        rod2.set_data([], [])
        
        piston1.set_xy((-50, 45))
        piston2.set_xy((-50, 5))
        
        for point in points:
            point.set_data([], [])
        
        x5_line.set_data([], [])
        x6_line.set_data([], [])
        
        return (circle_traj, sync_rod, t_leg, t_crossbar, rod1, rod2, 
                *points, x5_line, x6_line)
    
    def update(frame_idx):
        """Обновление кадра анимации"""
        result = frames_data[frame_idx]
        phi = valid_angles[frame_idx]
        
        # Извлекаем координаты
        x0, y0 = result['x0'], result['y0']
        x1, y1 = result['x1'], result['y1']
        x2, y2 = result['x2'], result['y2']
        x3, y3 = result['x3'], result['y3']
        x4, y4 = result['x4'], result['y4']
        x5, y5 = result['x5'], result['y5']
        x6, y6 = result['x6'], result['y6']
        
        # Обновляем элементы механизма
        # Траектория эксцентрика
        theta = np.linspace(0, 2*np.pi, 100)
        circle_x = x0 + 10 * np.cos(theta)
        circle_y = y0 + 10 * np.sin(theta)
        circle_traj.set_data(circle_x, circle_y)
        
        # Стержни
        sync_rod.set_data([0, x2], [0, y2])
        t_leg.set_data([x1, x2], [y1, y2])
        t_crossbar.set_data([x3, x2, x4], [y3, y2, y4])
        rod1.set_data([x3, x6], [y3, y6])
        rod2.set_data([x4, x5], [y4, y5])
        
        # Поршни (прямоугольники)
        piston_width = 5
        piston1.set_xy((x5 - piston_width/2, y5 - 10))
        piston2.set_xy((x6 - piston_width/2, y6 - 10))
        
        # Точки
        points_coords = [(x0, y0), (x1, y1), (x2, y2), (x3, y3), 
                        (x4, y4), (x5, y5), (x6, y6)]
        
        for i, (px, py) in enumerate(points_coords):
            points[i].set_data([px], [py])
        
        # Обновляем траектории
        history_angles.append(phi)
        history_x5.append(x5)
        history_x6.append(x6)
        
        x5_line.set_data(history_angles, history_x5)
        x6_line.set_data(history_angles, history_x6)
        
        # Обновляем вертикальную линию текущего угла
        current_angle_line.set_xdata([phi, phi])
        
        # Обновляем заголовок
        ax1.set_title(f'Механизм с Т-качалкой при φ = {phi:.1f}°', fontsize=14, fontweight='bold')
        
        return (circle_traj, sync_rod, t_leg, t_crossbar, rod1, rod2, 
                *points, x5_line, x6_line, current_angle_line)
    
    # Легенда
    ax1.legend(loc='upper right', fontsize=9)
    ax2.legend(loc='upper right', fontsize=9)
    
    # Создаем анимацию
    anim = FuncAnimation(fig, update, frames=len(frames_data),
                        init_func=init, blit=False, interval=20)
    
    # Сохраняем как GIF
    print("Сохранение оригинальной анимации...")
    anim.save('mechanism_animation_original.gif', writer='pillow', fps=30, dpi=150)
    print("Оригинальная анимация сохранена как 'mechanism_animation_original.gif'")
    
    plt.close(fig)
    return anim

def create_animation_with_velocities():
    """Создание анимации с графиками скоростей поршней"""
    print("\nСоздание анимации С ГРАФИКАМИ СКОРОСТЕЙ для 5 периодов обращения...")
    
    # Углы для анимации (5 периодов = 1800 градусов)
    angles = np.linspace(0, 1800, 361)
    
    # Собираем данные для анимации
    frames_data = []
    valid_angles = []
    
    for phi in angles:
        result = solve_mechanism(phi % 360)
        if result is not None:
            frames_data.append(result)
            valid_angles.append(phi)
    
    if not frames_data:
        print("Не удалось получить данные для анимации")
        return
    
    print(f"Собрано {len(frames_data)} кадров из {len(angles)} возможных")
    
    # Угловая скорость (рад/с) - для расчета скоростей поршней
    omega_rpm = 100  # об/мин
    omega_rad_per_sec = omega_rpm * 2 * np.pi / 60  # рад/с
    
    # Подготовка данных для расчета скоростей
    angles_rad = np.radians([d['phi_deg'] for d in frames_data])
    x5_vals = [d['x5'] for d in frames_data]
    x6_vals = [d['x6'] for d in frames_data]
    
    # Вычисляем производные (скорости изменения координат по углу)
    dx5_dphi = np.gradient(x5_vals, angles_rad)
    dx6_dphi = np.gradient(x6_vals, angles_rad)
    
    # Скорости поршней (dx/dt = dx/dφ * dφ/dt = dx/dφ * ω)
    v5_vals = dx5_dphi * omega_rad_per_sec
    v6_vals = dx6_dphi * omega_rad_per_sec
    
    # Создаем фигуру для анимации (теперь 3 графика)
    fig = plt.figure(figsize=(18, 10))
    
    # 1. График механизма
    ax1 = plt.subplot(2, 3, (1, 3))
    ax1.set_xlim(-80, 50)
    ax1.set_ylim(-10, 80)
    ax1.set_xlabel('X координата', fontsize=12)
    ax1.set_ylabel('Y координата', fontsize=12)
    ax1.set_title('Механизм с Т-качалкой', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal', adjustable='box')
    
    # 2. График траекторий поршней
    ax2 = plt.subplot(2, 3, 4)
    ax2.set_xlim(0, 1800)
    ax2.set_ylim(-80, 10)
    ax2.set_xlabel('Угол φ, градусы', fontsize=12)
    ax2.set_ylabel('X координата поршней', fontsize=12)
    ax2.set_title('Траектории движения поршней', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 3. График скоростей поршней
    ax3 = plt.subplot(2, 3, 5)
    ax3.set_xlim(0, 1800)
    ax3.set_ylim(-500, 500)
    ax3.set_xlabel('Угол φ, градусы', fontsize=12)
    ax3.set_ylabel('Скорость поршней, мм/с', fontsize=12)
    ax3.set_title(f'Скорости поршней при ω={omega_rpm} об/мин', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    
    # 4. График разности скоростей
    ax4 = plt.subplot(2, 3, 6)
    ax4.set_xlim(0, 1800)
    ax4.set_ylim(-300, 300)
    ax4.set_xlabel('Угол φ, градусы', fontsize=12)
    ax4.set_ylabel('Разность скоростей, мм/с', fontsize=12)
    ax4.set_title('Разность скоростей поршней (v6 - v5)', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    
    # Инициализируем элементы для анимации
    # Механизм
    circle_traj, = ax1.plot([], [], 'gray', linestyle='--', alpha=0.5)
    sync_rod, = ax1.plot([], [], 'b-', linewidth=3, label='Синхронизирующий рычаг')
    t_leg, = ax1.plot([], [], 'r-', linewidth=2, label='Ножка Т-качалки')
    t_crossbar, = ax1.plot([], [], 'g-', linewidth=2, label='Т-качалка')
    rod1, = ax1.plot([], [], 'm-', linewidth=2, label='Шатун 1 (к поршню 1)')
    rod2, = ax1.plot([], [], 'c-', linewidth=2, label='Шатун 2 (к поршню 2)')
    
    # Поршни
    piston1 = plt.Rectangle((0, 0), 5, 20, color='darkblue', alpha=0.7)
    piston2 = plt.Rectangle((0, 0), 5, 20, color='darkred', alpha=0.7)
    ax1.add_patch(piston1)
    ax1.add_patch(piston2)
    
    # Точки
    points = []
    for i in range(7):
        point, = ax1.plot([], [], 'o', markersize=8)
        points.append(point)
    
    # Траектории
    x5_line, = ax2.plot([], [], 'c-', linewidth=2, label='x5 (поршень 2)')
    x6_line, = ax2.plot([], [], 'm-', linewidth=2, label='x6 (поршень 1)')
    current_angle_line2 = ax2.axvline(x=0, color='r', linestyle='--', alpha=0.5)
    
    # Скорости
    v5_line, = ax3.plot([], [], 'c-', linewidth=2, label='v5 (поршень 2)')
    v6_line, = ax3.plot([], [], 'm-', linewidth=2, label='v6 (поршень 1)')
    current_angle_line3 = ax3.axvline(x=0, color='r', linestyle='--', alpha=0.5)
    
    # Разность скоростей
    v_diff_line, = ax4.plot([], [], 'purple', linewidth=2, label='v6 - v5')
    current_angle_line4 = ax4.axvline(x=0, color='r', linestyle='--', alpha=0.5)
    
    # Текущие значения скоростей (текст)
    v5_text = ax3.text(0.02, 0.95, '', transform=ax3.transAxes, fontsize=10,
                      bbox=dict(boxstyle='round', facecolor='cyan', alpha=0.5))
    v6_text = ax3.text(0.02, 0.85, '', transform=ax3.transAxes, fontsize=10,
                      bbox=dict(boxstyle='round', facecolor='magenta', alpha=0.5))
    
    # Собираем историю
    history_angles = []
    history_x5 = []
    history_x6 = []
    history_v5 = []
    history_v6 = []
    history_v_diff = []
    
    def init():
        """Инициализация анимации"""
        circle_traj.set_data([], [])
        sync_rod.set_data([], [])
        t_leg.set_data([], [])
        t_crossbar.set_data([], [])
        rod1.set_data([], [])
        rod2.set_data([], [])
        
        piston1.set_xy((-50, 45))
        piston2.set_xy((-50, 5))
        
        for point in points:
            point.set_data([], [])
        
        x5_line.set_data([], [])
        x6_line.set_data([], [])
        v5_line.set_data([], [])
        v6_line.set_data([], [])
        v_diff_line.set_data([], [])
        
        v5_text.set_text('')
        v6_text.set_text('')
        
        return (circle_traj, sync_rod, t_leg, t_crossbar, rod1, rod2, 
                *points, x5_line, x6_line, v5_line, v6_line, v_diff_line,
                v5_text, v6_text)
    
    def update(frame_idx):
        """Обновление кадра анимации"""
        result = frames_data[frame_idx]
        phi = valid_angles[frame_idx]
        
        # Извлекаем координаты
        x0, y0 = result['x0'], result['y0']
        x1, y1 = result['x1'], result['y1']
        x2, y2 = result['x2'], result['y2']
        x3, y3 = result['x3'], result['y3']
        x4, y4 = result['x4'], result['y4']
        x5, y5 = result['x5'], result['y5']
        x6, y6 = result['x6'], result['y6']
        
        # Текущие скорости
        v5 = v5_vals[frame_idx]
        v6 = v6_vals[frame_idx]
        v_diff = v6 - v5
        
        # Обновляем элементы механизма
        theta = np.linspace(0, 2*np.pi, 100)
        circle_x = x0 + 10 * np.cos(theta)
        circle_y = y0 + 10 * np.sin(theta)
        circle_traj.set_data(circle_x, circle_y)
        
        sync_rod.set_data([0, x2], [0, y2])
        t_leg.set_data([x1, x2], [y1, y2])
        t_crossbar.set_data([x3, x2, x4], [y3, y2, y4])
        rod1.set_data([x3, x6], [y3, y6])
        rod2.set_data([x4, x5], [y4, y5])
        
        piston_width = 5
        piston1.set_xy((x5 - piston_width/2, y5 - 10))
        piston2.set_xy((x6 - piston_width/2, y6 - 10))
        
        points_coords = [(x0, y0), (x1, y1), (x2, y2), (x3, y3), 
                        (x4, y4), (x5, y5), (x6, y6)]
        
        for i, (px, py) in enumerate(points_coords):
            points[i].set_data([px], [py])
        
        # Обновляем историю
        history_angles.append(phi)
        history_x5.append(x5)
        history_x6.append(x6)
        history_v5.append(v5)
        history_v6.append(v6)
        history_v_diff.append(v_diff)
        
        x5_line.set_data(history_angles, history_x5)
        x6_line.set_data(history_angles, history_x6)
        v5_line.set_data(history_angles, history_v5)
        v6_line.set_data(history_angles, history_v6)
        v_diff_line.set_data(history_angles, history_v_diff)
        
        # Обновляем вертикальные линии
        current_angle_line2.set_xdata([phi, phi])
        current_angle_line3.set_xdata([phi, phi])
        current_angle_line4.set_xdata([phi, phi])
        
        # Обновляем тексты скоростей
        v5_text.set_text(f'v5 = {v5:.1f} мм/с')
        v6_text.set_text(f'v6 = {v6:.1f} мм/с')
        
        # Обновляем заголовки
        ax1.set_title(f'Механизм при φ = {phi:.1f}°', fontsize=14, fontweight='bold')
        
        return (circle_traj, sync_rod, t_leg, t_crossbar, rod1, rod2, 
                *points, x5_line, x6_line, v5_line, v6_line, v_diff_line,
                v5_text, v6_text)
    
    # Легенды
    ax1.legend(loc='upper right', fontsize=9)
    ax2.legend(loc='upper right', fontsize=9)
    ax3.legend(loc='upper right', fontsize=9)
    ax4.legend(loc='upper right', fontsize=9)
    
    # Создаем анимацию
    anim = FuncAnimation(fig, update, frames=len(frames_data),
                        init_func=init, blit=False, interval=20)
    
    # Сохраняем как GIF
    print("Сохранение анимации со скоростями...")
    anim.save('mechanism_animation_with_velocities.gif', writer='pillow', fps=30, dpi=150)
    print("Анимация со скоростями сохранена как 'mechanism_animation_with_velocities.gif'")
    
    plt.close(fig)
    return anim

def plot_coordinates_vs_angle():
    """Построение графиков зависимости координат от угла (отдельные графики)"""
    print("\nПостроение графиков зависимости координат от угла...")
    
    # Углы для анализа (один полный оборот)
    angles = np.linspace(0, 360, 361)
    
    # Собираем данные
    data = []
    for phi in angles:
        result = solve_mechanism(phi)
        if result is not None:
            data.append(result)
    
    if not data:
        print("Не удалось получить данные для графиков")
        return
    
    angles_vals = [d['phi_deg'] for d in data]
    
    # ========== ГРАФИК 1: Координаты центра Т-качалки (x2, y2) ОТДЕЛЬНО ==========
    fig1, (ax1_x, ax1_y) = plt.subplots(2, 1, figsize=(12, 8))
    
    x2_vals = [d['x2'] for d in data]
    y2_vals = [d['y2'] for d in data]
    
    # График x2
    ax1_x.plot(angles_vals, x2_vals, 'b-', linewidth=2)
    ax1_x.set_xlabel('Угол φ, градусы', fontsize=12)
    ax1_x.set_ylabel('Координата x2', fontsize=12)
    ax1_x.set_title('Зависимость координаты X центра Т-качалки (точка 2) от угла φ', 
                   fontsize=14, fontweight='bold')
    ax1_x.grid(True, alpha=0.3)
    ax1_x.set_xlim(0, 360)
    
    # График y2
    ax1_y.plot(angles_vals, y2_vals, 'r-', linewidth=2)
    ax1_y.set_xlabel('Угол φ, градусы', fontsize=12)
    ax1_y.set_ylabel('Координата y2', fontsize=12)
    ax1_y.set_title('Зависимость координаты Y центра Т-качалки (точка 2) от угла φ', 
                   fontsize=14, fontweight='bold')
    ax1_y.grid(True, alpha=0.3)
    ax1_y.set_xlim(0, 360)
    
    plt.tight_layout()
    plt.savefig('x2_y2_vs_angle.png', dpi=150, bbox_inches='tight')
    print("График 1 сохранен как 'x2_y2_vs_angle.png'")
    plt.show()
    
    # ========== ГРАФИК 2: Координаты левого конца Т-качалки (x3, y3) ОТДЕЛЬНО ==========
    fig2, (ax2_x, ax2_y) = plt.subplots(2, 1, figsize=(12, 8))
    
    x3_vals = [d['x3'] for d in data]
    y3_vals = [d['y3'] for d in data]
    
    # График x3
    ax2_x.plot(angles_vals, x3_vals, 'b-', linewidth=2)
    ax2_x.set_xlabel('Угол φ, градусы', fontsize=12)
    ax2_x.set_ylabel('Координата x3', fontsize=12)
    ax2_x.set_title('Зависимость координаты X левого конца Т-качалки (точка 3) от угла φ', 
                   fontsize=14, fontweight='bold')
    ax2_x.grid(True, alpha=0.3)
    ax2_x.set_xlim(0, 360)
    
    # График y3
    ax2_y.plot(angles_vals, y3_vals, 'r-', linewidth=2)
    ax2_y.set_xlabel('Угол φ, градусы', fontsize=12)
    ax2_y.set_ylabel('Координата y3', fontsize=12)
    ax2_y.set_title('Зависимость координаты Y левого конца Т-качалки (точка 3) от угла φ', 
                   fontsize=14, fontweight='bold')
    ax2_y.grid(True, alpha=0.3)
    ax2_y.set_xlim(0, 360)
    
    plt.tight_layout()
    plt.savefig('x3_y3_vs_angle.png', dpi=150, bbox_inches='tight')
    print("График 2 сохранен как 'x3_y3_vs_angle.png'")
    plt.show()
    
    # ========== ГРАФИК 3: Координаты правого конца Т-качалки (x4, y4) ОТДЕЛЬНО ==========
    fig3, (ax3_x, ax3_y) = plt.subplots(2, 1, figsize=(12, 8))
    
    x4_vals = [d['x4'] for d in data]
    y4_vals = [d['y4'] for d in data]
    
    # График x4
    ax3_x.plot(angles_vals, x4_vals, 'b-', linewidth=2)
    ax3_x.set_xlabel('Угол φ, градусы', fontsize=12)
    ax3_x.set_ylabel('Координата x4', fontsize=12)
    ax3_x.set_title('Зависимость координаты X правого конца Т-качалки (точка 4) от угла φ', 
                   fontsize=14, fontweight='bold')
    ax3_x.grid(True, alpha=0.3)
    ax3_x.set_xlim(0, 360)
    
    # График y4
    ax3_y.plot(angles_vals, y4_vals, 'r-', linewidth=2)
    ax3_y.set_xlabel('Угол φ, градусы', fontsize=12)
    ax3_y.set_ylabel('Координата y4', fontsize=12)
    ax3_y.set_title('Зависимость координаты Y правого конца Т-качалки (точка 4) от угла φ', 
                   fontsize=14, fontweight='bold')
    ax3_y.grid(True, alpha=0.3)
    ax3_y.set_xlim(0, 360)
    
    plt.tight_layout()
    plt.savefig('x4_y4_vs_angle.png', dpi=150, bbox_inches='tight')
    print("График 3 сохранен как 'x4_y4_vs_angle.png'")
    plt.show()
    
    # ========== ГРАФИК 4: Координаты поршней (x5, x6) на ОДНОМ листе ==========
    fig4, ax4 = plt.subplots(figsize=(12, 8))
    
    x5_vals = [d['x5'] for d in data]
    x6_vals = [d['x6'] for d in data]
    
    ax4.plot(angles_vals, x5_vals, 'c-', label='x5 (поршень 2)', linewidth=3, alpha=0.8)
    ax4.plot(angles_vals, x6_vals, 'm-', label='x6 (поршень 1)', linewidth=3, alpha=0.8)
    
    ax4.set_xlabel('Угол φ, градусы', fontsize=12)
    ax4.set_ylabel('X координата поршней', fontsize=12)
    ax4.set_title('Зависимость координат X поршней от угла φ (оба на одном графике)', 
                 fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend(fontsize=12, loc='upper right')
    ax4.set_xlim(0, 360)
    
    # Вычисляем и выводим статистику
    min_x5_idx = np.argmin(x5_vals)
    max_x5_idx = np.argmax(x5_vals)
    min_x6_idx = np.argmin(x6_vals)
    max_x6_idx = np.argmax(x6_vals)
    
    # Отмечаем экстремумы
    ax4.plot(angles_vals[min_x5_idx], x5_vals[min_x5_idx], 'co', markersize=10)
    ax4.plot(angles_vals[max_x5_idx], x5_vals[max_x5_idx], 'co', markersize=10)
    ax4.plot(angles_vals[min_x6_idx], x6_vals[min_x6_idx], 'mo', markersize=10)
    ax4.plot(angles_vals[max_x6_idx], x6_vals[max_x6_idx], 'mo', markersize=10)
    
    # Статистика
    stats_text = f"""
    Статистика для одного оборота:
    
    Поршень 1 (x6):
      Минимум: {min(x6_vals):.2f} при φ={angles_vals[min_x6_idx]:.0f}°
      Максимум: {max(x6_vals):.2f} при φ={angles_vals[max_x6_idx]:.0f}°
      Амплитуда: {max(x6_vals)-min(x6_vals):.2f}
      Ход поршня: {max(x6_vals)-min(x6_vals):.2f}
    
    Поршень 2 (x5):
      Минимум: {min(x5_vals):.2f} при φ={angles_vals[min_x5_idx]:.0f}°
      Максимум: {max(x5_vals):.2f} при φ={angles_vals[max_x5_idx]:.0f}°
      Амплитуда: {max(x5_vals)-min(x5_vals):.2f}
      Ход поршня: {max(x5_vals)-min(x5_vals):.2f}
    """
    
    ax4.text(0.02, 0.02, stats_text, transform=ax4.transAxes,
             fontsize=10, verticalalignment='bottom',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('pistons_x5_x6_vs_angle.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("График 4 сохранен как 'pistons_x5_x6_vs_angle.png'")
    
    # ========== ГРАФИК 5: Скорости поршней ==========
    # Угловая скорость для расчета
    omega_rpm = 1000
    omega_rad_per_sec = omega_rpm * 2 * np.pi / 60
    
    # Преобразуем углы в радианы
    angles_rad = np.radians(angles_vals)
    
    # Вычисляем производные
    dx5_dphi = np.gradient(x5_vals, angles_rad)
    dx6_dphi = np.gradient(x6_vals, angles_rad)
    
    # Скорости поршней
    v5_vals = dx5_dphi * omega_rad_per_sec
    v6_vals = dx6_dphi * omega_rad_per_sec
    
    fig5, (ax5_v, ax5_diff) = plt.subplots(2, 1, figsize=(12, 8))
    
    # График скоростей
    ax5_v.plot(angles_vals, v5_vals, 'c-', label='v5 (поршень 2)', linewidth=2)
    ax5_v.plot(angles_vals, v6_vals, 'm-', label='v6 (поршень 1)', linewidth=2)
    ax5_v.set_xlabel('Угол φ, градусы', fontsize=12)
    ax5_v.set_ylabel('Скорость поршней, мм/с', fontsize=12)
    ax5_v.set_title(f'Скорости поршней при ω = {omega_rpm} об/мин', 
                   fontsize=14, fontweight='bold')
    ax5_v.grid(True, alpha=0.3)
    ax5_v.legend()
    ax5_v.axhline(y=0, color='k', linestyle='-', alpha=0.2)
    ax5_v.set_xlim(0, 360)
    
    # График разности скоростей
    v_diff = [v6 - v5 for v6, v5 in zip(v6_vals, v5_vals)]
    ax5_diff.plot(angles_vals, v_diff, 'purple', linewidth=2)
    ax5_diff.set_xlabel('Угол φ, градусы', fontsize=12)
    ax5_diff.set_ylabel('Разность скоростей v6 - v5, мм/с', fontsize=12)
    ax5_diff.set_title('Разность скоростей поршней', fontsize=14, fontweight='bold')
    ax5_diff.grid(True, alpha=0.3)
    ax5_diff.axhline(y=0, color='k', linestyle='-', alpha=0.2)
    ax5_diff.fill_between(angles_vals, 0, v_diff, where=(v_diff > 0), 
                         color='green', alpha=0.2, label='v6 > v5')
    ax5_diff.fill_between(angles_vals, 0, v_diff, where=(v_diff < 0), 
                         color='red', alpha=0.2, label='v6 < v5')
    ax5_diff.legend()
    ax5_diff.set_xlim(0, 360)
    
    # Статистика скоростей
    stats_v_text = f"""
    Статистика скоростей при ω={omega_rpm} об/мин:
    
    Максимальные скорости:
      v5_max: {max(v5_vals):.1f} мм/с
      v6_max: {max(v6_vals):.1f} мм/с
    
    Средние скорости:
      v5_avg: {np.mean(np.abs(v5_vals)):.1f} мм/с
      v6_avg: {np.mean(np.abs(v6_vals)):.1f} мм/с
    """
    
    ax5_v.text(0.02, 0.02, stats_v_text, transform=ax5_v.transAxes,
               fontsize=9, verticalalignment='bottom',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('pistons_velocities.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("График 5 сохранен как 'pistons_velocities.png'")
    
    return fig1, fig2, fig3, fig4, fig5

def main():
    """Основная функция"""
    print("=" * 60)
    print("ПОЛНЫЙ АНАЛИЗ МЕХАНИЗМА С Т-КАЧАЛКОЙ")
    print("=" * 60)
    
    # Создаем ОРИГИНАЛЬНУЮ анимацию
    print("\n1. СОЗДАНИЕ ОРИГИНАЛЬНОЙ АНИМАЦИИ (5 периодов)")
    anim1 = create_animation_original()
    
    # Создаем анимацию со скоростями
    print("\n2. СОЗДАНИЕ АНИМАЦИИ С ГРАФИКАМИ СКОРОСТЕЙ")
    anim2 = create_animation_with_velocities()
    
    # Строим графики зависимостей
    print("\n3. ПОСТРОЕНИЕ ГРАФИКОВ ЗАВИСИМОСТЕЙ")
    figs = plot_coordinates_vs_angle()
    
    # Демонстрация для конкретного угла
    print("\n4. ДЕМОНСТРАЦИЯ ДЛЯ КОНКРЕТНОГО УГЛА")
    try:
        phi_input = float(input("Введите угол φ в градусах для демонстрации (0-360): "))
        tolerance_input = 1e-9
        
        result = solve_mechanism(phi_input, tolerance_input)
        
        if result is not None and result['convergence']:
            print(f"\nРезультаты для φ = {phi_input}°:")
            print(f"x5 (поршень 2) = {result['x5']:.3f}")
            print(f"x6 (поршень 1) = {result['x6']:.3f}")
            print(f"Разность x6 - x5 = {result['x6'] - result['x5']:.3f}")
            
            # Построение схемы механизма для этого угла
            fig_single, ax_single = plt.subplots(figsize=(10, 8))
            
            # Извлекаем координаты
            x0, y0 = result['x0'], result['y0']
            x1, y1 = result['x1'], result['y1']
            x2, y2 = result['x2'], result['y2']
            x3, y3 = result['x3'], result['y3']
            x4, y4 = result['x4'], result['y4']
            x5, y5 = result['x5'], result['y5']
            x6, y6 = result['x6'], result['y6']
            
            # Рисуем элементы механизма
            # Траектория эксцентрика
            theta = np.linspace(0, 2*np.pi, 100)
            circle_x = x0 + 10 * np.cos(theta)
            circle_y = y0 + 10 * np.sin(theta)
            ax_single.plot(circle_x, circle_y, 'gray', linestyle='--', alpha=0.5)
            
            # Стержни
            ax_single.plot([0, x2], [0, y2], 'b-', linewidth=3, label='Синхронизирующий рычаг')
            ax_single.plot([x1, x2], [y1, y2], 'r-', linewidth=2, label='Ножка Т-качалки')
            ax_single.plot([x3, x2, x4], [y3, y2, y4], 'g-', linewidth=2, label='Т-качалка')
            ax_single.plot([x3, x6], [y3, y6], 'm-', linewidth=2, label='Шатун 1 (к поршню 1)')
            ax_single.plot([x4, x5], [y4, y5], 'c-', linewidth=2, label='Шатун 2 (к поршню 2)')
            
            # Поршни
            piston_width = 5
            ax_single.add_patch(plt.Rectangle((x5 - piston_width/2, y5 - 10), 
                                             piston_width, 20, 
                                             color='darkblue', alpha=0.7, label='Поршень 2'))
            ax_single.add_patch(plt.Rectangle((x6 - piston_width/2, y6 - 10), 
                                             piston_width, 20, 
                                             color='darkred', alpha=0.7, label='Поршень 1'))
            
            # Точки
            points_coords = [(x0, y0), (x1, y1), (x2, y2), (x3, y3), 
                            (x4, y4), (x5, y5), (x6, y6)]
            labels = ['O₀', '1', '2', '3', '4', '5', '6']
            colors = ['black', 'red', 'blue', 'green', 'green', 'cyan', 'magenta']
            
            for (px, py), label, color in zip(points_coords, labels, colors):
                ax_single.plot(px, py, 'o', markersize=8, color=color)
                offset_x = 2 if px >= 0 else -15
                offset_y = 2 if py >= 0 else -10
                ax_single.text(px + offset_x, py + offset_y, label, 
                              fontsize=9, fontweight='bold')
            
            # Настройки графика
            ax_single.set_xlabel('X координата', fontsize=12)
            ax_single.set_ylabel('Y координата', fontsize=12)
            ax_single.set_title(f'Механизм с Т-качалкой при φ = {phi_input}°', 
                              fontsize=14, fontweight='bold')
            ax_single.grid(True, alpha=0.3)
            ax_single.set_aspect('equal', adjustable='box')
            ax_single.legend(loc='upper right', fontsize=9)
            
            # Добавляем информацию о координатах поршней
            info_text = f"Координаты поршней при φ={phi_input}°:\n"
            info_text += f"x5 (поршень 2) = {x5:.2f}\n"
            info_text += f"x6 (поршень 1) = {x6:.2f}\n"
            info_text += f"Разность = {x6 - x5:.2f}"
            
            ax_single.text(0.02, 0.98, info_text, transform=ax_single.transAxes,
                          fontsize=10, verticalalignment='top',
                          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            plt.tight_layout()
            plt.savefig(f'mechanism_phi_{phi_input:.0f}.png', dpi=150, bbox_inches='tight')
            plt.show()
            print(f"\nСхема механизма сохранена как 'mechanism_phi_{phi_input:.0f}.png'")
            
        else:
            print(f"Не удалось найти решение для φ = {phi_input}°")
            
    except ValueError:
        print("Ошибка ввода! Используется значение по умолчанию φ = 45°")
        phi_input = 45
        result = solve_mechanism(phi_input)
        if result is not None:
            print(f"\nРезультаты для φ = {phi_input}°:")
            print(f"x5 (поршень 2) = {result['x5']:.3f}")
            print(f"x6 (поршень 1) = {result['x6']:.3f}")
            print(f"Разность x6 - x5 = {result['x6'] - result['x5']:.3f}")
    
    print("\n" + "=" * 60)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("Созданы файлы:")
    print("1. mechanism_animation_original.gif - оригинальная анимация")
    print("2. mechanism_animation_with_velocities.gif - анимация со скоростями")
    print("3. x2_y2_vs_angle.png - графики координат точки 2")
    print("4. x3_y3_vs_angle.png - графики координат точки 3")
    print("5. x4_y4_vs_angle.png - графики координат точки 4")
    print("6. pistons_x5_x6_vs_angle.png - графики координат поршней")
    print("7. pistons_velocities.png - графики скоростей поршней")
    print("=" * 60)

# Запуск программы
if __name__ == "__main__":
    main()
