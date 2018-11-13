import pygame
from pygame.sprite import Sprite


class Ship(Sprite):
    """飞船类"""

    def __init__(self, screen, ai_settings):
        """初始化飞船并设置其初始位置"""
        super(Ship, self).__init__()
        self.screen = screen
        self.ai_settings = ai_settings

        # 加载飞船图像并获取其外接矩形
        self.image = pygame.image.load("images/ship.bmp")
        self.rect = self.image.get_rect()  # 飞船图像外接矩形
        self.screen_rect = screen.get_rect()  # 屏幕窗口矩形

        # 将飞船放在屏幕的底部中央
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom

        # 在飞船的属性center中存储小数值
        self.center = float(self.rect.centerx)  # 将飞船的外接矩形的中心横坐标转换成小数

        # 移动标志
        self.moving_right = False
        self.moving_left = False

    def update(self):
        """根据移动标志位调整飞船的位置"""
        # 更新飞船的center值而不是rect
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.center += self.ai_settings.ship_speed_factor
        if self.moving_left and self.rect.left > 0:
            # 使用if而不是elif, 这样当同时按下左箭头和右箭头的时候moving_right和moving_left具有相同的优先级
            self.center -= self.ai_settings.ship_speed_factor

        # 根据self.center更新rect对象
        self.rect.centerx = self.center

    def center_ship(self):
        """将飞船重新放到屏幕的底部中央"""
        self.center = self.screen_rect.centerx

    def blitme(self):
        """在指定位置绘制飞船"""
        self.screen.blit(self.image, self.rect)
