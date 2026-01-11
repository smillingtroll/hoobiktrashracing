from PIL import Image, ImageDraw, ImageFilter
import math
import random
import numpy as np
from game_engine import GameEngine, Vector2

class TextureGenerator:
    @staticmethod
    def create_underground_background(width=800, height=300):
        """Создает детальный фон свалки в андеграунд-стиле"""
        img = Image.new('RGB', (width, height), (25, 20, 30))
        draw = ImageDraw.Draw(img)
        
        # Градиентное небо
        for y in range(height // 2):
            color = (25 + y//20, 20 + y//15, 30 + y//10)
            draw.line([(0, y), (width, y)], fill=color)
        
        # Текстура стен
        for i in range(50):
            x = random.randint(0, width)
            y = random.randint(0, height//3)
            length = random.randint(20, 100)
            color = random.choice([(40, 35, 45), (45, 40, 50), (35, 30, 40)])
            draw.line([(x, y), (x, y + length)], fill=color, width=2)
        
        # Трубы и провода
        for i in range(10):
            y = random.randint(50, 150)
            color = (60, 60, 70) if random.random() > 0.5 else (80, 60, 40)
            draw.line([(0, y), (width, y)], fill=color, width=3)
            
            # Крепления труб
            for j in range(0, width, 40):
                draw.rectangle([j-2, y-2, j+2, y+2], fill=(100, 100, 110))
        
        # Граффити (текстурные детали)
        graffiti_texts = ["WASTE", "KART", "RUN", "TRASH"]
        for text in graffiti_texts:
            x = random.randint(50, width-100)
            y = random.randint(30, 100)
            draw.text((x, y), text, fill=(150, 40, 60), 
                     font_size=random.choice([20, 24, 28]))
        
        # Добавляем шум для текстуры
        noise = np.random.randint(0, 10, (height, width, 3), dtype=np.uint8)
        noise_img = Image.fromarray(noise, 'RGB')
        img = Image.blend(img, noise_img, alpha=0.05)
        
        return img
    
    @staticmethod
    def create_terrain_texture():
        """Текстура земли с мусором"""
        img = Image.new('RGB', (64, 64), (60, 50, 40))
        draw = ImageDraw.Draw(img)
        
        # Базовая текстура земли
        for y in range(64):
            for x in range(64):
                if random.random() > 0.7:
                    r = random.randint(-5, 5)
                    g = random.randint(-5, 5)
                    b = random.randint(-5, 5)
                    color = (60 + r, 50 + g, 40 + b)
                    draw.point((x, y), fill=color)
        
        # Камни и мусор
        for i in range(30):
            x, y = random.randint(0, 63), random.randint(0, 63)
            size = random.randint(2, 5)
            color = random.choice([(80, 70, 60), (70, 80, 70), (90, 80, 70)])
            draw.ellipse([x, y, x+size, y+size], fill=color)
        
        # Трещины
        for i in range(5):
            start_x, start_y = random.randint(0, 63), random.randint(0, 63)
            for j in range(random.randint(3, 8)):
                draw.point((start_x + j, start_y + j//2), fill=(40, 30, 20))
        
        return img
    
    @staticmethod
    def create_kart_texture():
        """Детальная текстура карта"""
        img = Image.new('RGBA', (60, 40), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Основной корпус карта
        draw.ellipse([5, 10, 55, 30], fill=(40, 40, 45))  # Серый металл
        
        # Детали корпуса
        draw.rectangle([15, 12, 45, 28], fill=(30, 30, 35))  # Центральная часть
        draw.line([20, 12, 40, 12], fill=(100, 100, 110), width=2)  # Верхняя кромка
        
        # Решетки и вентиляция
        for i in range(3):
            x = 18 + i * 8
            draw.rectangle([x, 15, x+4, 25], fill=(20, 20, 25))
        
        # Ржавчина и потертости
        for i in range(10):
            x, y = random.randint(5, 55), random.randint(10, 30)
            if random.random() > 0.5:
                draw.point((x, y), fill=(80, 50, 30))  # Ржавчина
            else:
                draw.point((x, y), fill=(120, 120, 130))  # Металлический блеск
        
        return img
    
    @staticmethod
    def create_character_texture():
        """Текстура персонажа"""
        img = Image.new('RGBA', (24, 36), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Ноги (большие кросовки)
        draw.rectangle([4, 28, 8, 35], fill=(0, 0, 0))  # Левая нога
        draw.rectangle([16, 28, 20, 35], fill=(0, 0, 0))  # Правая нога
        
        # Добавляем белые детали кросовок
        draw.rectangle([5, 30, 7, 32], fill=(255, 255, 255))
        draw.rectangle([17, 30, 19, 32], fill=(255, 255, 255))
        
        # Штаны (серые)
        draw.rectangle([6, 18, 18, 28], fill=(80, 80, 90))
        
        # Складки на штанах
        draw.line([8, 20, 8, 26], fill=(60, 60, 70), width=1)
        draw.line([16, 20, 16, 26], fill=(60, 60, 70), width=1)
        
        # Тело (белая майка)
        draw.rectangle([8, 10, 16, 18], fill=(240, 240, 240))
        
        # Руки
        draw.rectangle([4, 12, 8, 16], fill=(240, 220, 200))  # Левая рука
        draw.rectangle([16, 12, 20, 16], fill=(240, 220, 200))  # Правая рука
        
        # Голова
        draw.ellipse([8, 0, 16, 8], fill=(240, 220, 200))
        
        # Черная шапка "бини"
        draw.rectangle([6, -2, 18, 4], fill=(20, 20, 20))
        draw.ellipse([4, 0, 20, 8], fill=(20, 20, 20))
        
        # Лицо (спокойное выражение)
        draw.point((10, 3), fill=(0, 0, 0))  # Левый глаз
        draw.point((14, 3), fill=(0, 0, 0))  # Правый глаз
        draw.line([11, 5, 13, 5], fill=(0, 0, 0), width=1)  # Рот
        
        return img
    
    @staticmethod
    def create_head_texture(color='red'):
        """Текстура катящейся головы"""
        img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Основной цвет
        if color == 'red':
            base_color = (180, 40, 40)
            dark_color = (120, 20, 20)
            light_color = (220, 80, 80)
        else:  # blue
            base_color = (40, 60, 180)
            dark_color = (20, 40, 120)
            light_color = (80, 100, 220)
        
        # Голова (круг)
        draw.ellipse([4, 4, 28, 28], fill=base_color)
        
        # Детали: глаза
        draw.ellipse([12, 12, 16, 16], fill=(255, 255, 255))
        draw.ellipse([18, 12, 22, 16], fill=(255, 255, 255))
        draw.ellipse([13, 13, 15, 15], fill=(0, 0, 0))
        draw.ellipse([19, 13, 21, 15], fill=(0, 0, 0))
        
        # Рот
        draw.arc([12, 18, 22, 24], 0, 180, fill=(0, 0, 0), width=2)
        
        # Блики (световые эффекты)
        draw.ellipse([8, 8, 12, 12], fill=light_color)
        draw.ellipse([22, 20, 26, 24], fill=light_color)
        
        # Трещины (если голова повреждена)
        draw.line([10, 20, 15, 25], fill=dark_color, width=1)
        draw.line([20, 10, 25, 15], fill=dark_color, width=1)
        
        return img
    
    @staticmethod
    def create_wheel_texture():
        """Текстура колеса"""
        img = Image.new('RGBA', (20, 20), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Шина
        draw.ellipse([2, 2, 18, 18], fill=(20, 20, 20))
        
        # Диск
        draw.ellipse([6, 6, 14, 14], fill=(60, 60, 70))
        
        # Спицы
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = 10 + 5 * math.cos(rad)
            y1 = 10 + 5 * math.sin(rad)
            x2 = 10 + 2 * math.cos(rad)
            y2 = 10 + 2 * math.sin(rad)
            draw.line([(x1, y1), (x2, y2)], fill=(100, 100, 110), width=2)
        
        # Болты
        for angle in range(0, 360, 90):
            rad = math.radians(angle)
            x = 10 + 8 * math.cos(rad)
            y = 10 + 8 * math.sin(rad)
            draw.ellipse([x-2, y-2, x+2, y+2], fill=(150, 150, 160))
        
        return img

class GameRenderer:
    def __init__(self, width=800, height=300):
        self.width = width
        self.height = height
        self.texture_gen = TextureGenerator()
        
        # Предварительная генерация текстур
        self.background = self.texture_gen.create_underground_background(width, height)
        self.terrain_texture = self.texture_gen.create_terrain_texture()
        self.kart_texture = self.texture_gen.create_kart_texture()
        self.character_texture = self.texture_gen.create_character_texture()
        self.red_head_texture = self.texture_gen.create_head_texture('red')
        self.blue_head_texture = self.texture_gen.create_head_texture('blue')
        self.wheel_texture = self.texture_gen.create_wheel_texture()
        
        # Текстура пыли
        self.dust_texture = self._create_dust_texture()
    
    def _create_dust_texture(self):
        img = Image.new('RGBA', (40, 20), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        for i in range(50):
            x = random.randint(0, 39)
            y = random.randint(0, 19)
            alpha = random.randint(50, 150)
            size = random.randint(1, 3)
            color = (150, 120, 80, alpha)
            draw.ellipse([x, y, x+size, y+size], fill=color)
        
        return img
    
    def render_frame(self, game_state, show_death=False):
        # Создаем базовое изображение
        img = self.background.copy()
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Определяем область видимости (камера следует за игроком)
        camera_x = game_state['player']['x'] - self.width // 3
        camera_x = max(0, camera_x)
        
        # Рендерим terrain
        self._render_terrain(draw, game_state['terrain'], camera_x)
        
        # Рендерим препятствия
        for obstacle in game_state['obstacles']:
            if obstacle['active']:
                self._render_obstacle(draw, obstacle, camera_x)
        
        # Рендерим карт с персонажем
        if not show_death or (show_death and game_state['player']['alive']):
            self._render_kart_with_character(draw, game_state['player'], camera_x)
        
        # Эффекты пыли
        if game_state['player']['on_ground'] and abs(game_state['player']['velocity_x']) > 2:
            self._render_dust(draw, game_state['player'], camera_x)
        
        # Анимация смерти
        if show_death and not game_state['player']['alive']:
            self._render_death_animation(draw, game_state['player'], camera_x)
        
        # Интерфейс
        self._render_ui(draw, game_state['player'])
        
        return img
    
    def _render_terrain(self, draw, terrain_segments, camera_x):
        """Рендеринг земли с текстурой"""
        for segment in terrain_segments:
            start_x = segment['start_x'] - camera_x
            end_x = segment['end_x'] - camera_x
            
            if end_x < 0 or start_x > self.width:
                continue
            
            # Рисуем землю
            y_base = segment['base_height']
            
            # Текстурная земля
            for x in range(int(start_x), int(end_x), 64):
                for y in range(int(y_base), self.height, 64):
                    tex_x = x % 64
                    tex_y = (y - int(y_base)) % 64
                    color = self.terrain_texture.getpixel((tex_x, tex_y))
                    draw.point((x - camera_x % 64, y), fill=color)
            
            # Кочки
            for bump in segment['bumps']:
                bump_x = bump['pos'] - camera_x
                if 0 <= bump_x <= self.width:
                    bump_height = bump['height']
                    bump_width = bump['width']
                    
                    # Рисуем кочку как параболу
                    for dx in range(int(-bump_width/2), int(bump_width/2)):
                        x_pos = bump_x + dx
                        if 0 <= x_pos <= self.width:
                            # Форма кочки
                            rel = dx / (bump_width/2)
                            height_offset = bump_height * (1 - rel**2)
                            y_pos = y_base - height_offset
                            
                            # Текстура для кочки
                            tex_x = (int(x_pos) + int(camera_x)) % 64
                            tex_y = int(height_offset) % 64
                            color = self.terrain_texture.getpixel((tex_x, tex_y))
                            
                            # Рисуем вертикальную линию для кочки
                            for dy in range(int(height_offset)):
                                if y_pos + dy < self.height:
                                    # Затемняем цвет для объема
                                    dark_factor = 1.0 - dy / height_offset * 0.3
                                    shaded_color = tuple(int(c * dark_factor) for c in color[:3])
                                    draw.point((x_pos, y_pos + dy), fill=shaded_color)
    
    def _render_obstacle(self, draw, obstacle, camera_x):
        x = obstacle['x'] - camera_x
        y = obstacle['y']
        
        if not (0 <= x <= self.width and 0 <= y <= self.height):
            return
        
        if 'head' in obstacle['type']:
            texture = self.red_head_texture if 'red' in obstacle['type'] else self.blue_head_texture
            
            # Применяем вращение
            rotated = texture.rotate(obstacle['rotation'] * 180 / math.pi, 
                                    resample=Image.BICUBIC, 
                                    expand=True)
            
            # Центрируем
            paste_x = int(x - rotated.width // 2)
            paste_y = int(y - rotated.height // 2)
            
            img = draw._image
            img.paste(rotated, (paste_x, paste_y), rotated)
            
        elif obstacle['type'] == 'ramp':
            # Рисуем трамплин
            ramp_width = 60
            ramp_height = 20
            
            points = [
                (x, y),
                (x + ramp_width, y - ramp_height),
                (x + ramp_width, y),
                (x, y)
            ]
            
            # Металлическая текстура трамплина
            for i in range(len(points)-1):
                x1, y1 = points[i]
                x2, y2 = points[i+1]
                
                steps = int(math.sqrt((x2-x1)**2 + (y2-y1)**2))
                for j in range(steps):
                    px = x1 + (x2-x1) * j/steps
                    py = y1 + (y2-y1) * j/steps
                    
                    # Металлический цвет с текстурой
                    metal_color = (100 + (int(px+py) % 3) * 10, 
                                  90 + (int(px) % 3) * 5, 
                                  80 + (int(py) % 3) * 5)
                    draw.point((int(px), int(py)), fill=metal_color)
            
            # Опорная конструкция
            draw.rectangle([x+10, y, x+15, y+10], fill=(80, 80, 90))
            draw.rectangle([x+45, y-ramp_height, x+50, y-ramp_height+10], fill=(80, 80, 90))
    
    def _render_kart_with_character(self, draw, player, camera_x):
        x = player['x'] - camera_x
        y = player['y']
        rotation = player['rotation']
        
        # Сохраняем текущее состояние трансформации
        original_draw = draw._image
        
        # Создаем временное изображение для карта
        kart_img = Image.new('RGBA', (80, 60), (0, 0, 0, 0))
        kart_draw = ImageDraw.Draw(kart_img)
        
        # Позиции колес относительно центра карта
        wheel_base = 30
        wheel_y_offset = 10
        
        # Заднее колесо
        back_wheel_x = -wheel_base // 2
        back_wheel_y = wheel_y_offset
        
        # Переднее колесо
        front_wheel_x = wheel_base // 2
        front_wheel_y = wheel_y_offset
        
        # Вращение колес в зависимости от скорости
        wheel_rotation = player['wheel_rotation']
        
        # Рисуем заднее колесо
        wheel = self.wheel_texture.rotate(wheel_rotation * 180 / math.pi, 
                                         resample=Image.BICUBIC)
        kart_img.paste(wheel, 
                      (40 + back_wheel_x - wheel.width//2, 
                       30 + back_wheel_y - wheel.height//2), 
                      wheel)
        
        # Рисуем переднее колесо
        wheel = self.wheel_texture.rotate(wheel_rotation * 180 / math.pi, 
                                         resample=Image.BICUBIC)
        kart_img.paste(wheel, 
                      (40 + front_wheel_x - wheel.width//2, 
                       30 + front_wheel_y - wheel.height//2), 
                      wheel)
        
        # Рисуем корпус карта
        kart_body = self.kart_texture.copy()
        kart_img.paste(kart_body, (40 - kart_body.width//2, 30 - kart_body.height//2), 
                      kart_body)
        
        # Рисуем персонажа в карте
        character = self.character_texture.copy()
        
        # Наклон персонажа в зависимости от вращения карта
        char_rotation = rotation * 0.5
        if char_rotation > 0.3:
            char_rotation = 0.3
        elif char_rotation < -0.3:
            char_rotation = -0.3
        
        character_rotated = character.rotate(char_rotation * 180 / math.pi, 
                                            resample=Image.BICUBIC)
        
        kart_img.paste(character_rotated, 
                      (40 - character_rotated.width//2, 
                       30 - character_rotated.height//2 - 5), 
                      character_rotated)
        
        # Применяем общее вращение карта
        kart_rotated = kart_img.rotate(rotation * 180 / math.pi, 
                                      resample=Image.BICUBIC, 
                                      expand=True)
        
        # Вставляем в основное изображение
        paste_x = int(x - kart_rotated.width // 2)
        paste_y = int(y - kart_rotated.height // 2)
        
        if 0 <= paste_x <= self.width and 0 <= paste_y <= self.height:
            original_draw.paste(kart_rotated, (paste_x, paste_y), kart_rotated)
    
    def _render_dust(self, draw, player, camera_x):
        x = player['x'] - camera_x
        y = player['y'] + 5  # Немного ниже колес
        
        # Позиции под колесами
        wheel_offset = 15
        rotation = player['rotation']
        
        # Координаты колес с учетом вращения
        back_wheel_x = x - wheel_offset * math.cos(rotation)
        back_wheel_y = y + wheel_offset * math.sin(rotation)
        
        front_wheel_x = x + wheel_offset * math.cos(rotation)
        front_wheel_y = y - wheel_offset * math.sin(rotation)
        
        # Интенсивность пыли в зависимости от скорости
        dust_intensity = min(abs(player['velocity_x']) / 10, 1.0)
        
        # Рендерим пыль под колесами
        for wheel_x, wheel_y in [(back_wheel_x, back_wheel_y), (front_wheel_x, front_wheel_y)]:
            dust = self.dust_texture.copy()
            
            # Настраиваем прозрачность в зависимости от интенсивности
            dust = dust.point(lambda p: p * dust_intensity)
            
            # Вставляем пыль
            paste_x = int(wheel_x - dust.width // 2)
            paste_y = int(wheel_y - dust.height // 2)
            
            if 0 <= paste_x <= self.width and 0 <= paste_y <= self.height:
                img = draw._image
                img.paste(dust, (paste_x, paste_y), dust)
    
    def _render_death_animation(self, draw, player, camera_x):
        x = player['x'] - camera_x
        y = player['y']
        
        # Анимация взрыва
        radius = 30
        for r in range(radius, 0, -3):
            alpha = int(200 * (r / radius))
            color = (255, 100, 50, alpha)
            
            # Рисуем круги разного размера
            draw.ellipse([x-r, y-r, x+r, y+r], 
                        fill=color, 
                        outline=(255, 150, 100, alpha))
        
        # Частицы
        for i in range(20):
            angle = random.random() * 2 * math.pi
            distance = random.randint(10, 40)
            particle_x = x + distance * math.cos(angle)
            particle_y = y + distance * math.sin(angle)
            
            size = random.randint(2, 5)
            color = random.choice([(255, 200, 100), (255, 100, 50), (200, 50, 30)])
            
            draw.ellipse([particle_x-size, particle_y-size, 
                         particle_x+size, particle_y+size], 
                        fill=color)
    
    def _render_ui(self, draw, player):
        # Счетчик дистанции
        distance_text = f"DISTANCE: {int(player['distance'] // 5)}"
        
        # Фон для текста
        draw.rectangle([10, 10, 200, 40], fill=(0, 0, 0, 150))
        
        # Текст дистанции
        for i, char in enumerate(distance_text):
            x = 15 + i * 12
            y = 15
            
            # Пиксельный шрифт
            if char != ' ':
                draw.rectangle([x, y, x+8, y+12], fill=(255, 255, 255))
                draw.rectangle([x+2, y+2, x+6, y+10], fill=(255, 50, 50))
        
        # Счетчик рывков
        for i in range(player['boost_charges']):
            x = 15 + i * 25
            y = 50
            
            # Иконка рывка
            draw.ellipse([x, y, x+15, y+15], fill=(100, 200, 255, 200))
            draw.polygon([(x+7, y+4), (x+12, y+7), (x+7, y+10)], 
                        fill=(255, 255, 255))
