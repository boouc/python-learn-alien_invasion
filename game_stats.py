import json


class GameStats:
    """跟踪游戏的统计信息"""

    def __init__(self, ai_settings):
        """初始化游戏统计信息"""
        self.ai_settings = ai_settings
        self.reset_stats()

        # 游戏刚启动时, 处于活动状态
        self.game_active = False

        # 玩家最高得分, 在任何情况下都不应该重置最高得分
        # 从文件中读取最高分
        try:
            with open("high_score.json", "r") as f_obj:
                old_high_score = json.load(f_obj)
        except FileNotFoundError:
            self.high_score = 0
        else:
            self.high_score = old_high_score

    def reset_stats(self):
        """初始化在游戏运行期间可能变化的统计信息"""
        self.ships_left = self.ai_settings.ship_limit
        self.score = 0
        # 玩家等级
        self.level = 1
