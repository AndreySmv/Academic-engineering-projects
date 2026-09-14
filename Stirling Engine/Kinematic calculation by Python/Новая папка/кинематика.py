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

def create_animation():
    """Создание анимации для 5 периодов обращения"""
    print("Создание анимации для 5 периодов обращения...")
    
    # Углы для анимации (5 периодов = 1800 градусов)
    angles = np.linspace(0, 1800, 361)  # 361 кадр для плавной анимации
    
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
    
    # Настраиваем второй график (траектории)
    ax2.set_xlim(0, 1800)
    ax2.set_ylim(-80, 10)
    ax2.set_xlabel('Угол φ, градусы', fontsize=12)
    ax2.set_ylabel('X координата', fontsize=12)
    ax2.set_title('Траектории движения поршней', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Инициализируем элементы для анимации
    # Механизм
    circle_traj, = ax1.plot([], [], 'gray', linestyle='--', alpha=0.5)
    sync_rod, = ax1.plot([], [], 'b-', linewidth=3, label='Синхронизирующий рычаг')
    t_leg, = ax1.plot([], [], 'r-', linewidth=2, label='Ножка Т-качалки')
    t_crossbar, = ax1.plot([], [], 'g-', linewidth=2, label='Т-качалка')
    rod1, = ax1.plot([], [], 'm-', linewidth=2, label='Шатун 1')
    rod2, = ax1.plot([], [], 'c-', linewidth=2, label='Шатун 2')
    piston1, = ax1.plot([], [], 'k-', linewidth=2, label='Поршень 1')
    piston2, = ax1.plot([], [], 'k-', linewidth=2, label='Поршень 2')
    
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
        piston1.set_data([], [])
        piston2.set_data([], [])
        
        for point in points:
            point.set_data([], [])
        
        x5_line.set_data([], [])
        x6_line.set_data([], [])
        
        return (circle_traj, sync_rod, t_leg, t_crossbar, rod1, rod2, 
                piston1, piston2, *points, x5_line, x6_line)
    
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
        
        # Поршни
        piston_width = 3
        piston1.set_data([x5, x5], [y5-10, y5+10])
        piston2.set_data([x6, x6], [y6-10, y6+10])
        
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
                piston1, piston2, *points, x5_line, x6_line, current_angle_line)
    
    # Легенда
    ax1.legend(loc='upper right', fontsize=9)
    ax2.legend(loc='upper right', fontsize=9)
    
    # Создаем анимацию
    anim = FuncAnimation(fig, update, frames=len(frames_data),
                        init_func=init, blit=False, interval=20)
    
    # Сохраняем как GIF
    print("Сохранение анимации...")
    anim.save('mechanism_animation_5_periods.gif', writer='pillow', fps=30, dpi=100)
    print("Анимация сохранена как 'mechanism_animation_5_periods.gif'")
    
    plt.close(fig)
    return anim

def plot_coordinates_vs_angle():
    """Построение графиков зависимости координат от угла"""
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
    
    # Создаем фигуру с несколькими графиками
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    axes = axes.flatten()
    
    # 1. Координаты центра Т-качалки (x2, y2)
    ax = axes[0]
    x2_vals = [d['x2'] for d in data]
    y2_vals = [d['y2'] for d in data]
    angles_vals = [d['phi_deg'] for d in data]
    
    ax.plot(angles_vals, x2_vals, 'b-', label='x2', linewidth=2)
    ax.plot(angles_vals, y2_vals, 'r-', label='y2', linewidth=2)
    ax.set_xlabel('Угол φ, градусы', fontsize=10)
    ax.set_ylabel('Координаты', fontsize=10)
    ax.set_title('Координаты центра Т-качалки (точка 2)', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # 2. Координаты левого конца Т-качалки (x3, y3)
    ax = axes[1]
    x3_vals = [d['x3'] for d in data]
    y3_vals = [d['y3'] for d in data]
    
    ax.plot(angles_vals, x3_vals, 'b-', label='x3', linewidth=2)
    ax.plot(angles_vals, y3_vals, 'r-', label='y3', linewidth=2)
    ax.set_xlabel('Угол φ, градусы', fontsize=10)
    ax.set_ylabel('Координаты', fontsize=10)
    ax.set_title('Координаты левого конца Т-качалки (точка 3)', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # 3. Координаты правого конца Т-качалки (x4, y4)
    ax = axes[2]
    x4_vals = [d['x4'] for d in data]
    y4_vals = [d['y4'] for d in data]
    
    ax.plot(angles_vals, x4_vals, 'b-', label='x4', linewidth=2)
    ax.plot(angles_vals, y4_vals, 'r-', label='y4', linewidth=2)
    ax.set_xlabel('Угол φ, градусы', fontsize=10)
    ax.set_ylabel('Координаты', fontsize=10)
    ax.set_title('Координаты правого конца Т-качалки (точка 4)', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # 4. Координаты поршней (x5, x6)
    ax = axes[3]
    x5_vals = [d['x5'] for d in data]
    x6_vals = [d['x6'] for d in data]
    
    ax.plot(angles_vals, x5_vals, 'c-', label='x5 (поршень 2)', linewidth=3)
    ax.plot(angles_vals, x6_vals, 'm-', label='x6 (поршень 1)', linewidth=3)
    ax.set_xlabel('Угол φ, градусы', fontsize=10)
    ax.set_ylabel('X координата', fontsize=10)
    ax.set_title('Координаты поршней по X', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # 5. Скорости изменения координат поршней
    ax = axes[4]
    # Вычисляем производные (скорости)
    dx5 = np.gradient(x5_vals, angles_vals)
    dx6 = np.gradient(x6_vals, angles_vals)
    
    ax.plot(angles_vals, dx5, 'c--', label='dx5/dφ', linewidth=2)
    ax.plot(angles_vals, dx6, 'm--', label='dx6/dφ', linewidth=2)
    ax.set_xlabel('Угол φ, градусы', fontsize=10)
    ax.set_ylabel('Скорость', fontsize=10)
    ax.set_title('Скорости изменения координат поршней', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.axhline(y=0, color='k', linestyle='-', alpha=0.2)
    
    # 6. Разность координат поршней
    ax = axes[5]
    diff_x = [x6 - x5 for x6, x5 in zip(x6_vals, x5_vals)]
    
    ax.plot(angles_vals, diff_x, 'g-', linewidth=2)
    ax.set_xlabel('Угол φ, градусы', fontsize=10)
    ax.set_ylabel('Разность x6 - x5', fontsize=10)
    ax.set_title('Разность координат поршней', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linestyle='-', alpha=0.2)
    
    plt.tight_layout()
    plt.savefig('coordinates_vs_angle.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Графики сохранены как 'coordinates_vs_angle.png'")
    
    # Дополнительный график: x5 и x6 на одном графике (увеличенный)
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    
    ax2.plot(angles_vals, x5_vals, 'c-', label='x5 (поршень 2)', linewidth=3, alpha=0.8)
    ax2.plot(angles_vals, x6_vals, 'm-', label='x6 (поршень 1)', linewidth=3, alpha=0.8)
    
    # Добавляем заполнение между кривыми
    ax2.fill_between(angles_vals, x5_vals, x6_vals, where=(x6_vals > x5_vals), 
                     color='purple', alpha=0.2, label='Область x6 > x5')
    
    ax2.set_xlabel('Угол φ, градусы', fontsize=12)
    ax2.set_ylabel('X координата поршней', fontsize=12)
    ax2.set_title('Зависимость координат поршней от угла φ', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10, loc='upper right')
    
    # Добавляем аннотации для экстремальных значений
    min_x5_idx = np.argmin(x5_vals)
    max_x5_idx = np.argmax(x5_vals)
    min_x6_idx = np.argmin(x6_vals)
    max_x6_idx = np.argmax(x6_vals)
    
    ax2.plot(angles_vals[min_x5_idx], x5_vals[min_x5_idx], 'co', markersize=8)
    ax2.text(angles_vals[min_x5_idx], x5_vals[min_x5_idx]-2, 
             f'min x5={x5_vals[min_x5_idx]:.1f}\nφ={angles_vals[min_x5_idx]:.0f}°',
             ha='center', va='top', fontsize=9)
    
    ax2.plot(angles_vals[min_x6_idx], x6_vals[min_x6_idx], 'mo', markersize=8)
    ax2.text(angles_vals[min_x6_idx], x6_vals[min_x6_idx]-2, 
             f'min x6={x6_vals[min_x6_idx]:.1f}\nφ={angles_vals[min_x6_idx]:.0f}°',
             ha='center', va='top', fontsize=9)
    
    # Вычисляем и выводим статистику
    stats_text = f"""
    Статистика для одного оборота:
    x5 (поршень 2):
      Минимум: {min(x5_vals):.2f} при φ={angles_vals[min_x5_idx]:.0f}°
      Максимум: {max(x5_vals):.2f} при φ={angles_vals[max_x5_idx]:.0f}°
      Амплитуда: {max(x5_vals)-min(x5_vals):.2f}
      
    x6 (поршень 1):
      Минимум: {min(x6_vals):.2f} при φ={angles_vals[min_x6_idx]:.0f}°
      Максимум: {max(x6_vals):.2f} при φ={angles_vals[max_x6_idx]:.0f}°
      Амплитуда: {max(x6_vals)-min(x6_vals):.2f}
      
    Средняя разность: {np.mean(diff_x):.2f}
    """
    
    ax2.text(0.02, 0.02, stats_text, transform=ax2.transAxes,
             fontsize=9, verticalalignment='bottom',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('pistons_vs_angle_detailed.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Детальный график сохранен как 'pistons_vs_angle_detailed.png'")
    
    return fig, fig2

def main():
    """Основная функция"""
    print("=" * 60)
    print("ПОЛНЫЙ АНАЛИЗ МЕХАНИЗМА С Т-КАЧАЛКОЙ")
    print("=" * 60)
    
    # Создаем анимацию для 5 периодов
    print("\n1. СОЗДАНИЕ АНИМАЦИИ (5 периодов)")
    anim = create_animation()
    
    # Строим графики зависимостей
    print("\n2. ПОСТРОЕНИЕ ГРАФИКОВ ЗАВИСИМОСТЕЙ")
    figs = plot_coordinates_vs_angle()
    
    # Демонстрация для конкретного угла
    print("\n3. ДЕМОНСТРАЦИЯ ДЛЯ КОНКРЕТНОГО УГЛА")
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
            ax_single.plot([x3, x6], [y3, y6], 'm-', linewidth=2, label='Шатун 1')
            ax_single.plot([x4, x5], [y4, y5], 'c-', linewidth=2, label='Шатун 2')
            
            # Поршни
            ax_single.plot([x5, x5], [y5-10, y5+10], 'k-', linewidth=2, label='Поршень 2')
            ax_single.plot([x6, x6], [y6-10, y6+10], 'k-', linewidth=2, label='Поршень 1')
            
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
            info_text = f"Координаты поршней:\n"
            info_text += f"x5 = {x5:.2f}\n"
            info_text += f"x6 = {x6:.2f}\n"
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
    
    print("\n" + "=" * 60)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("Созданы файлы:")
    print("1. mechanism_animation_5_periods.gif - анимация 5 периодов")
    print("2. coordinates_vs_angle.png - все графики зависимостей")
    print("3. pistons_vs_angle_detailed.png - детальный график x5 и x6")
    print("=" * 60)

# Запуск программы
if __name__ == "__main__":
    main()
