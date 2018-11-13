import sys
from time import sleep

import pygame

import json

from bullet import Bullet
from alien import Alien


def check_keydown_events(event, ai_settings, screen, stats, ship, bullets):
    """响应按键事件"""
    if event.key == pygame.K_RIGHT:
        # 如果右箭头按下, 向右移动飞船
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:  # TODO: 按住空格不松开, 无法连续发射子弹
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        # 按下q键退出游戏
        # 在退出游戏前, 将最高分写入文件
        with open("high_score.json", "w") as f_obj:
            json.dump(stats.high_score, f_obj)
        sys.exit()


def check_keyup_events(event, ship):
    """响应松开按键事件"""
    if event.key == pygame.K_RIGHT:
        # 如果右箭头弹起, 移动标志位置为False
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def check_events(ai_settings, screen, stats, sb, play_button, ship, aliens,
                 bullets):
    """响应键盘鼠标事件"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # 在退出游戏前, 将最高分写入文件
            with open("high_score.json", "w") as f_obj:
                json.dump(stats.high_score, f_obj)
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, stats, ship,
                                 bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, sb, play_button, ship,
                              aliens, bullets, mouse_x, mouse_y)


def check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens,
                      bullets, mouse_x, mouse_y):
    """在点击到了Play按钮的时候, 开始游戏"""
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    # 当点击到按钮区域并且游戏处于非活动状态的时候, 才重置游戏
    if button_clicked and not stats.game_active:
        # 重置游戏设置
        ai_settings.initialize_dynamic_settings()

        # 开始游戏后, 隐藏光标
        pygame.mouse.set_visible(False)

        # 重置游戏统计信息
        stats.reset_stats()
        stats.game_active = True

        # 重置记分牌图像
        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_ships()  # 显示可用的飞船

        # 清空外星人和子弹列表
        aliens.empty()
        bullets.empty()

        # 创建一群新的外星人, 并让飞船重新居中
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()


def update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets,
                  play_button):
    """更新屏幕上的图像, 并切换到新屏幕"""
    # 每次循环都重绘屏幕
    screen.fill(ai_settings.bg_color)

    # 在飞船和外星人后面重绘子弹
    for bullet in bullets.sprites():
        bullet.draw_bullet()

    # 绘制飞船
    ship.blitme()

    # 绘制外星人
    aliens.draw(screen)  # 对编组调用draw()时, Pygame会自动绘制编组的每个元素, 绘制的位置由元素的属性rect决定

    # 显示得分
    sb.show_score()

    # 如果游戏处于非活动状态, 就绘制Play按钮:
    if not stats.game_active:
        play_button.draw_buttom()

    # 让最近绘制的屏幕可见
    pygame.display.flip()


def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """更新子弹的位置, 并删除已消失的子弹"""
    # 更新子弹的位置
    bullets.update()  # 编组自动对每个精灵调用update()

    # 删除消失的子弹
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens,
                                  bullets)


def check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens,
                                  bullets):
    """检查是否有子弹击中了外星人"""
    # 删除发生碰撞的子弹和外星人
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
    # 遍历子弹编组和外星人编组, 当有子弹和外星人的rect重叠时, groupcollide()就会在它返回的字典中添加一个"子弹: 外星人"的键值对
    # 两个实参True高所pygame删除发生碰撞的子弹和外星人

    # 计分
    if collisions:
        # 可能有多个外星人被同时击中, 因此被击中的外星人是一个列表
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
        # 消灭外星人, 更新得分后, 要检查是否产生了新的最高分
        check_high_score(stats, sb)

    if len(aliens) == 0:
        # 如果整群外星人都被消灭了, 就提升一个等级
        # 删除现有的子弹并重新创建一群外星人
        bullets.empty()
        ai_settings.increase_speed()  # 加快游戏元素的速度

        # 提高等级
        stats.level += 1
        sb.prep_level()

        create_fleet(ai_settings, screen, ship, aliens)


def fire_bullet(ai_settings, screen, ship, bullets):
    """如果子弹数量没有到达限制, 就发射一个子弹"""
    # 创建一颗子弹, 并将其加入编组bullets中
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def get_number_aliens_x(ai_settings, alien_width):
    """计算每行容纳多少个外星人"""
    available_space_x = ai_settings.screen_width - 2 * alien_width  # 可用空间
    number_aliens_x = int(
        available_space_x / (2 * alien_width))  # 计算一行可容纳的外星人数量
    return number_aliens_x


def get_number_rows(ai_settings, ship_height, alien_height):
    """计算可以容纳多少行外星人"""
    available_space_y = (
            ai_settings.screen_height - 3 * alien_height - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """创建一个外星人并将其放入当前行"""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien_height = alien.rect.height
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien_height + 2 * alien_height * row_number
    aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens):
    """创建外星人群"""
    # 创建一个外星人, 并计算一行可以容纳多少个外星人
    # 外星人间距为外星人的宽度
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height,
                                  alien.rect.height)

    # 绘制一行外星人
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number, row_number)


def check_fleet_edges(ai_settings, aliens):
    """检测是否有外星人到达屏幕边缘"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def change_fleet_direction(ai_settings, aliens):
    """将整群外星人下移, 并改变它们的方向"""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """外星人撞到飞船"""
    # 将ships_left减1
    if stats.ships_left > 0:
        stats.ships_left -= 1

        # 更新记分牌剩余的飞船数量
        sb.prep_ships()

        # 清空外星人列表和子弹列表
        aliens.empty()
        bullets.empty()

        # 创建一群新的外星人, 并将飞船重新放到屏幕的底部中央
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

        # 暂停
        sleep(0.5)
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)  # 游戏结束后, 让光标可见


def check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """检测是否有外星人到达了屏幕底端"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # 像飞船被撞到那样处理
            ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)
            break


def update_aliens(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """
    检查是否有外星人位于屏幕的边缘, 并更新外星人群中所有外星人的位置
    """
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    # 检测外星人和飞船之间的碰撞
    if pygame.sprite.spritecollideany(ship, aliens):
        # spritecollideany()检测编组是否有成员和精灵发生了碰撞
        # 该函数返回第一个和飞船发生碰撞的外星人, 如果没有发生碰撞, 返回None
        ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)

    # 检测是否有外星人到达屏幕底端
    check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets)


def check_high_score(stats, sb):
    """检查是否产生了新的最高分"""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()
