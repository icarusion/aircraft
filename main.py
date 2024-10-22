import pygame
import sys
import random

# 初始化Pygame
pygame.init()

# 屏幕尺寸
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("打飞机游戏")

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# 分数
score = 0
font = pygame.font.Font(None, 36)

# 加载背景图片
background = pygame.image.load("bg.png")
bg_y1 = 0
bg_y2 = -SCREEN_HEIGHT

# 加载并播放背景音乐
pygame.mixer.music.load("bg.mp3")
pygame.mixer.music.play(-1)  # -1表示循环播放

# 加载音效
ding_sound = pygame.mixer.Sound("ding.wav")

# 飞机类
class Plane(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("ship.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.shooting = False
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 250  # 子弹发射间隔（毫秒）

    def update(self):
        mouse_x, _ = pygame.mouse.get_pos()
        self.rect.centerx = mouse_x
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)

# 子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("bullet.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

# 敌机类
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = [pygame.image.load("1.png").convert_alpha(),
                       pygame.image.load("2.png").convert_alpha(),
                       pygame.image.load("3.png").convert_alpha()]
        self.image = random.choice(self.images)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.speed_y = random.randint(1, 5)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.speed_y = random.randint(1, 5)

# 岩石类
class Stone(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("stone.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed_y = random.randint(1, 5)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# 初始化精灵组
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
stones = pygame.sprite.Group()

# 创建飞机
plane = Plane()
all_sprites.add(plane)

# 创建敌机
for i in range(8):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

def reset_game():
    global score, all_sprites, bullets, enemies, stones, plane
    score = 0
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    stones = pygame.sprite.Group()
    plane = Plane()
    all_sprites.add(plane)
    for i in range(8):
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

# 游戏循环
running = True
game_over = False
stone_timer = 0
STONE_INTERVAL = 3000  # 每3秒生成一个岩石
while running:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                plane.shooting = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 左键
                plane.shooting = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_over:
                reset_game()
                game_over = False

    if not game_over:
        # 更新游戏状态
        all_sprites.update()

        # 连续发射子弹
        if plane.shooting:
            plane.shoot()

        # 检测子弹和敌机的碰撞
        hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
        for hit in hits:
            score += 1
            ding_sound.play()
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)

        # 检测飞机和敌机的碰撞
        if pygame.sprite.spritecollideany(plane, enemies):
            game_over = True

        # 检测飞机和岩石的碰撞
        if pygame.sprite.spritecollideany(plane, stones):
            game_over = True

        # 生成岩石
        if current_time - stone_timer > STONE_INTERVAL:
            stone = Stone()
            all_sprites.add(stone)
            stones.add(stone)
            stone_timer = current_time

        # 背景滚动
        bg_y1 += 2
        bg_y2 += 2
        if bg_y1 >= SCREEN_HEIGHT:
            bg_y1 = -SCREEN_HEIGHT
        if bg_y2 >= SCREEN_HEIGHT:
            bg_y2 = -SCREEN_HEIGHT
        screen.blit(background, (0, bg_y1))
        screen.blit(background, (0, bg_y2))

        all_sprites.draw(screen)

        # 显示分数
        score_text = font.render("Score: {}".format(score), True, WHITE)
        screen.blit(score_text, (10, 10))
    else:
        game_over_text = font.render("Game Over! Press Space to Restart", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))

    pygame.display.flip()

    # 帧率控制
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
