import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Game Window Dimensions
width = 800
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Python Subway Dash")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = (128, 128, 128)

# Load Assets (Ensure you have these images in the same directory or adjust paths)
# You can create placeholder images if you don't have actual assets yet
player_img = pygame.image.load("player.png").convert_alpha() # Replace "player.png" with your player image
train_img = pygame.image.load("train.png").convert_alpha()
coin_img = pygame.image.load("coin.png").convert_alpha()
background_img = pygame.image.load("background.png").convert()

# --- Scale images if needed ---
player_img = pygame.transform.scale(player_img, (50, 80)) # Example scaling, adjust as needed
train_img = pygame.transform.scale(train_img, (100, 60))
coin_img = pygame.transform.scale(coin_img, (30, 30))
background_img = pygame.transform.scale(background_img, (width, height)) # Scale background to window size


# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (width / 2, height - 100) # Start position
        self.speed_x = 0
        self.speed_y = 0
        self.lane = 2 # 1: left, 2: middle, 3: right (lanes for movement)
        self.is_jumping = False
        self.jump_power = 15
        self.gravity = 1
        self.is_invincible = False # For jump invincibility

    def update(self):
        self.speed_x = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.move_lane_left()
        if keys[pygame.K_RIGHT]:
            self.move_lane_right()
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.jump()

        # Lane Movement
        if self.lane == 1: # Left lane
            target_x = 150 # Adjust these lane positions based on your design
        elif self.lane == 2: # Middle lane
            target_x = width / 2
        elif self.lane == 3: # Right lane
            target_x = width - 150 # Adjust these lane positions based on your design

        if self.rect.centerx != target_x:
            direction = 1 if target_x > self.rect.centerx else -1
            self.rect.centerx += direction * 10 # Adjust speed as needed

        # Jumping Physics
        if self.is_jumping:
            self.speed_y -= self.gravity
            self.rect.y -= self.speed_y
            if self.rect.bottom >= height - 100: # Ground level
                self.rect.bottom = height - 100
                self.is_jumping = False
                self.speed_y = 0
                self.is_invincible = False # End invincibility after landing
        else:
            self.is_invincible = False # Not invincible when not jumping


    def move_lane_left(self):
        if self.lane > 1:
            self.lane -= 1

    def move_lane_right(self):
        if self.lane < 3:
            self.lane += 1

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.speed_y = self.jump_power
            self.is_invincible = True # Player becomes invincible during jump


# Train Obstacle Class
class Train(pygame.sprite.Sprite):
    def __init__(self, lane):
        super().__init__()
        self.image = train_img
        self.rect = self.image.get_rect()
        if lane == 1:
            self.rect.x = 150 # Left lane
        elif lane == 2:
            self.rect.x = width / 2 # Middle lane
        elif lane == 3:
            self.rect.x = width - 150 # Right lane
        self.rect.bottom = -train_img.get_height()  # Start from just above the top
        self.speed_y = 5  # Train speed, adjust for difficulty
        self.lane = lane # Store the lane of the train

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > height: # Move off screen
            self.rect.bottom =  -train_img.get_height() # Reset to top
            self.rect.x = random.choice([150, width/2, width-150]) # Re-appear in random lane
            self.lane =  get_lane_from_x(self.rect.x) # Update lane when respawning

def get_lane_from_x(x_pos):
    if abs(x_pos - 150) < 5: # Using a small tolerance for comparison
        return 1
    elif abs(x_pos - width/2) < 5:
        return 2
    elif abs(x_pos - (width - 150)) < 5:
        return 3
    return 2 # Default to middle lane if something goes wrong

# Coin Class
class Coin(pygame.sprite.Sprite):
    def __init__(self, lane):
        super().__init__()
        self.image = coin_img
        self.rect = self.image.get_rect()
        if lane == 1:
            self.rect.centerx = 150 # Left lane
        elif lane == 2:
            self.rect.centerx = width / 2 # Middle lane
        elif lane == 3:
            self.rect.centerx = width - 150 # Right lane
        self.rect.bottom = random.randint(-500, -50) # Start from random position above
        self.speed_y = 3 # Coin speed, can be different from train speed

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > height: # Move off screen
            self.rect.bottom = random.randint(-500, -50)
            self.rect.centerx = random.choice([150, width/2, width-150]) # Re-appear in random lane


# Sprite Groups
all_sprites = pygame.sprite.Group()
trains = pygame.sprite.Group()
coins = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

# Create Trains - Start with only one train
train_lanes = [1, 2, 3] # Lanes where trains can spawn
for lane_index in range(1): # Start with fewer trains, e.g., 1
    lane = train_lanes[lane_index] # Initial train in the first lane
    train = Train(lane)
    all_sprites.add(train)
    trains.add(train)


# Create Coins
for _ in range(10): # Create multiple coins
    lane = random.randint(1, 3)
    coin = Coin(lane)
    all_sprites.add(coin)
    coins.add(coin)


# Game Variables
score = 0
font = pygame.font.Font(None, 36)
running = True
clock = pygame.time.Clock()
background_x = 0 # For scrolling background
train_spawn_rate = 2000 # Milliseconds between train spawns (start with 2 seconds)
last_train_spawn = pygame.time.get_ticks()


# Game Loop
while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update Sprites
    all_sprites.update()

    # Background Scrolling
    background_x -= 2 # Adjust scrolling speed
    if background_x < -background_img.get_width():
        background_x = 0

    # Train Spawning Logic - Control train frequency over time
    if current_time - last_train_spawn > train_spawn_rate:
        lane = random.choice([1, 2, 3])
        train = Train(lane)
        all_sprites.add(train)
        trains.add(train)
        last_train_spawn = current_time
        train_spawn_rate = max(500, train_spawn_rate - 10) # Gradually increase train frequency, but not below 0.5 sec

    # Check for Collisions (Player and Trains)
    train_hits = pygame.sprite.spritecollide(player, trains, False) # False for do not kill train on collision
    for train in train_hits:
        if not player.is_jumping and player.lane == train.lane and not player.is_invincible: # Only collide if not jumping and in same lane
            running = False # Game Over

    # Check for Coin Collection
    coin_hits = pygame.sprite.spritecollide(player, coins, True) # True to remove coin after collision
    for coin in coin_hits:
        score += 1
        lane = random.randint(1, 3) # Create new coin in random lane
        new_coin = Coin(lane)
        all_sprites.add(new_coin)
        coins.add(new_coin)


    # Draw / Render
    screen.blit(background_img, (background_x, 0))
    screen.blit(background_img, (background_x + background_img.get_width(), 0)) # Seamless scrolling

    all_sprites.draw(screen)

    # Display Score
    score_text = font.render(f"Score: {score}", True, white)
    screen.blit(score_text, (10, 10))


    # --- Example Beautiful UI Enhancements (Expand on these) ---
    # You can draw lines for lanes, add more UI elements, etc.
    pygame.draw.line(screen, gray, (width/3, 0), (width/3, height), 3) # Left lane divider
    pygame.draw.line(screen, gray, (2*width/3, 0), (2*width/3, height), 3) # Right lane divider


    # After Game Over - Example (Basic Game Over Screen)
    if not running:
        screen.fill(black) # Black screen
        game_over_text = font.render("Game Over! Press R to Restart", True, white)
        screen.blit(game_over_text, (width/2 - game_over_text.get_width()/2, height/2 - 50))
        final_score_text = font.render(f"Your Score: {score}", True, white)
        screen.blit(final_score_text, (width/2 - final_score_text.get_width()/2, height/2 + 10))
        pygame.display.flip() # Update display for game over screen

        waiting_for_restart = True
        while waiting_for_restart:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting_for_restart = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: # Press 'R' to restart
                        # --- Reset Game ---
                        score = 0
                        running = True # Set running back to True to restart the main loop
                        player.rect.center = (width / 2, height - 100)
                        player.lane = 2
                        player.is_jumping = False
                        player.speed_y = 0
                        train_spawn_rate = 2000
                        last_train_spawn = pygame.time.get_ticks()


                        # Clear existing trains and coins
                        for entity in trains:
                            entity.kill()
                        trains.empty()
                        for entity in coins:
                            entity.kill()
                        coins.empty()

                        # Re-create trains and coins
                        train_lanes = [1, 2, 3] # Lanes where trains can spawn
                        for lane_index in range(1): # Start with fewer trains, e.g., 1
                            lane = train_lanes[lane_index] # Initial train in the first lane
                            train = Train(lane)
                            all_sprites.add(train)
                            trains.add(train)
                        for _ in range(10):
                            lane = random.randint(1, 3)
                            coin = Coin(lane)
                            all_sprites.add(coin)
                            coins.add(coin)

                        waiting_for_restart = False # Exit restart loop and continue game loop


    pygame.display.flip() # Update the display
    clock.tick(60) # FPS


pygame.quit()
