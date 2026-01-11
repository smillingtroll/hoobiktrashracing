import random
import math
from dataclasses import dataclass
from typing import List, Dict, Tuple
import json

@dataclass
class Vector2:
    x: float
    y: float
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def normalized(self):
        mag = self.magnitude()
        if mag == 0:
            return Vector2(0, 0)
        return Vector2(self.x/mag, self.y/mag)

@dataclass
class Player:
    position: Vector2
    velocity: Vector2
    rotation: float  # в радианах
    angular_velocity: float
    on_ground: bool
    alive: bool
    distance: float
    boost_charges: int
    wheel_rotation: float  # вращение колес для анимации
    
    def __init__(self):
        self.position = Vector2(100, 200)
        self.velocity = Vector2(5, 0)
        self.rotation = 0
        self.angular_velocity = 0
        self.on_ground = True
        self.alive = True
        self.distance = 0
        self.boost_charges = 3
        self.wheel_rotation = 0

@dataclass
class Obstacle:
    type: str  # 'head_red', 'head_blue', 'ramp', 'loop', 'bump'
    position: Vector2
    velocity: Vector2
    active: bool
    rotation: float = 0
    
    def __init__(self, type: str, x: float, y: float):
        self.type = type
        self.position = Vector2(x, y)
        self.velocity = Vector2(-3 if 'head' in type else 0, 0)
        self.active = True
        self.rotation = 0

class TerrainSegment:
    def __init__(self, start_x: float, end_x: float, base_height: float):
        self.start_x = start_x
        self.end_x = end_x
        self.base_height = base_height
        self.bumps = []
        if random.random() > 0.7:
            self._generate_bumps()
    
    def _generate_bumps(self):
        num_bumps = random.randint(1, 3)
        for i in range(num_bumps):
            pos = self.start_x + (self.end_x - self.start_x) * (i + 1) / (num_bumps + 1)
            height = random.uniform(5, 15)
            width = random.uniform(20, 40)
            self.bumps.append({'pos': pos, 'height': height, 'width': width})
    
    def get_height_at(self, x: float) -> float:
        height = self.base_height
        for bump in self.bumps:
            dist = abs(x - bump['pos'])
            if dist < bump['width'] / 2:
                # Параболическая форма кочки
                relative_dist = dist / (bump['width'] / 2)
                bump_height = bump['height'] * (1 - relative_dist**2)
                height -= bump_height
        return height

class GameEngine:
    def __init__(self):
        self.player = Player()
        self.obstacles: List[Obstacle] = []
        self.terrain: List[TerrainSegment] = []
        self.game_time = 0
        self.gravity = Vector2(0, 0.5)
        self.ground_friction = 0.95
        self.air_friction = 0.99
        self.boost_power = 15
        self.max_velocity_x = 25
        self.max_velocity_y = 30
        self._generate_initial_terrain()
        self._generate_initial_obstacles()
        
        # Физические свойства
        self.kart_width = 40
        self.kart_height = 25
        self.wheel_radius = 8
        
    def _generate_initial_terrain(self):
        current_x = 0
        for i in range(10):
            length = random.uniform(200, 400)
            height = 220 + random.uniform(-20, 20)
            self.terrain.append(TerrainSegment(current_x, current_x + length, height))
            current_x += length
    
    def _generate_initial_obstacles(self):
        # Генерация голов
        for i in range(5):
            x = 300 + i * 200
            y = 200 + random.uniform(-20, 20)
            color = random.choice(['red', 'blue'])
            self.obstacles.append(Obstacle(f'head_{color}', x, y))
        
        # Генерация трамплинов
        for i in range(3):
            x = 500 + i * 300
            y = 180 + random.uniform(-10, 10)
            self.obstacles.append(Obstacle('ramp', x, y))
        
        # Генерация петель
        for i in range(2):
            x = 800 + i * 400
            self.obstacles.append(Obstacle('loop', x, 150))
    
    def get_terrain_height(self, x: float) -> float:
        for segment in self.terrain:
            if segment.start_x <= x <= segment.end_x:
                return segment.get_height_at(x)
        return 220
    
    def update(self, action: str = None):
        if not self.player.alive:
            return
        
        self.game_time += 1
        
        # Применяем действие игрока
        if action == 'gas':
            if self.player.on_ground:
                self.player.velocity.x += 0.8
                self.player.wheel_rotation += self.player.velocity.x * 0.1
        elif action == 'brake':
            if self.player.on_ground:
                self.player.velocity.x *= 0.7
        elif action == 'boost':
            if self.player.boost_charges > 0:
                boost_vector = Vector2(
                    math.cos(self.player.rotation) * self.boost_power,
                    math.sin(self.player.rotation) * self.boost_power
                )
                self.player.velocity = self.player.velocity + boost_vector
                self.player.boost_charges -= 1
        
        # Применяем физику
        self.player.velocity.y += self.gravity.y
        
        # Ограничение скорости
        self.player.velocity.x = max(-self.max_velocity_x, min(self.max_velocity_x, self.player.velocity.x))
        self.player.velocity.y = max(-self.max_velocity_y, min(self.max_velocity_y, self.player.velocity.y))
        
        # Обновление позиции
        new_position = self.player.position + self.player.velocity
        
        # Проверка столкновения с землей
        ground_height = self.get_terrain_height(new_position.x)
        if new_position.y >= ground_height - self.kart_height / 2:
            new_position.y = ground_height - self.kart_height / 2
            self.player.velocity.y = 0
            self.player.on_ground = True
            
            # Трение о землю
            self.player.velocity.x *= self.ground_friction
            # Восстановление вращения при приземлении
            if abs(self.player.rotation) > 0.1:
                self.player.angular_velocity = -self.player.rotation * 0.1
        else:
            self.player.on_ground = False
            # Сопротивление воздуха
            self.player.velocity.x *= self.air_friction
        
        # Обновление вращения
        if not self.player.on_ground:
            self.player.rotation += self.player.angular_velocity
            self.player.angular_velocity *= 0.98
        
        self.player.position = new_position
        self.player.distance = max(self.player.distance, self.player.position.x)
        
        # Обновление препятствий
        for obstacle in self.obstacles:
            if obstacle.active:
                obstacle.position = obstacle.position + obstacle.velocity
                obstacle.rotation += 0.1 if 'head' in obstacle.type else 0
                
                # Проверка столкновения с игроком
                if self._check_collision(obstacle):
                    if 'head' in obstacle.type:
                        obstacle.active = False
                    # Проверка смерти
                    if self._check_death_condition(obstacle):
                        self.player.alive = False
        
        # Генерация новых препятствий
        if random.random() < 0.02:
            self._generate_new_obstacle()
        
        # Генерация новой местности
        if self.player.position.x > self.terrain[-1].end_x - 500:
            self._extend_terrain()
    
    def _check_collision(self, obstacle: Obstacle) -> bool:
        dist = math.sqrt(
            (obstacle.position.x - self.player.position.x)**2 +
            (obstacle.position.y - self.player.position.y)**2
        )
        
        if 'head' in obstacle.type:
            collision_distance = 30
        elif obstacle.type == 'ramp':
            collision_distance = 40
        else:
            collision_distance = 50
            
        return dist < collision_distance
    
    def _check_death_condition(self, obstacle: Obstacle) -> bool:
        # Смерть если:
        # 1. Голова врезалась (не разрушена вовремя)
        if 'head' in obstacle.type and obstacle.active:
            return True
        
        # 2. Персонаж перевернулся (голова коснулась земли)
        if abs(self.player.rotation) > math.pi/2:  # 90 градусов
            head_position = Vector2(
                self.player.position.x + math.sin(self.player.rotation) * 20,
                self.player.position.y - math.cos(self.player.rotation) * 20
            )
            ground_height = self.get_terrain_height(head_position.x)
            if head_position.y >= ground_height - 5:
                return True
        
        return False
    
    def _generate_new_obstacle(self):
        x = self.player.position.x + 800 + random.uniform(0, 200)
        obstacle_type = random.choice(['head_red', 'head_blue', 'ramp', 'bump'])
        y = self.get_terrain_height(x) - 30
        
        if obstacle_type == 'ramp':
            y -= 20
        elif 'head' in obstacle_type:
            y += random.uniform(-20, 20)
        
        self.obstacles.append(Obstacle(obstacle_type, x, y))
    
    def _extend_terrain(self):
        last_segment = self.terrain[-1]
        new_length = random.uniform(200, 400)
        new_height = last_segment.base_height + random.uniform(-30, 30)
        self.terrain.append(TerrainSegment(
            last_segment.end_x,
            last_segment.end_x + new_length,
            new_height
        ))
    
    def get_game_state(self) -> Dict:
        return {
            'player': {
                'x': self.player.position.x,
                'y': self.player.position.y,
                'velocity_x': self.player.velocity.x,
                'velocity_y': self.player.velocity.y,
                'rotation': self.player.rotation,
                'on_ground': self.player.on_ground,
                'alive': self.player.alive,
                'distance': self.player.distance,
                'boost_charges': self.player.boost_charges,
                'wheel_rotation': self.player.wheel_rotation
            },
            'obstacles': [
                {
                    'type': o.type,
                    'x': o.position.x,
                    'y': o.position.y,
                    'rotation': o.rotation,
                    'active': o.active
                } for o in self.obstacles if o.active
            ],
            'terrain': [
                {
                    'start_x': t.start_x,
                    'end_x': t.end_x,
                    'base_height': t.base_height,
                    'bumps': t.bumps
                } for t in self.terrain[-5:]  # Только ближайшие сегменты
            ]
        }
