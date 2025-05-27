import pygame
import sys
import random
import math
import os

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_HEIGHT = 50
GRAVITY = 1
JUMP_FORCE = 15
GAME_SPEED = 5
BOOST_SPEED = 10  # Speed when boost is active
ROTATION_SPEED = 10  # Degrees per frame for rotation animation
TRIANGLE_WIDTH = 150  # 300% of original 50
PLATFORM_WIDTH = 240  # 300% of original 80
PLATFORM_HEIGHT = 120  # 300% of original 40
OBSTACLE_MIN_HEIGHT = 50  # Base height before scaling
OBSTACLE_MAX_HEIGHT = 100  # Base height before scaling
OBSTACLE_FREQUENCY = 1500  # milliseconds
BOOST_FREQUENCY = 5000  # milliseconds

# Audio settings - direct values to avoid any issues
MUSIC_NORMAL_VOLUME = 1.0  # 100% volume during active gameplay
MUSIC_IDLE_VOLUME = 0.3    # 30% volume during idle state
MUSIC_MENU_VOLUME = 0.3    # 10% volume for menu/game over states

try:
    FONT_SMALL = pygame.font.Font(resource_path("assets/fonts/PixelOperator8.ttf"), 20)
    FONT_MEDIUM = pygame.font.Font(resource_path("assets/fonts/PixelOperator8.ttf"), 36)
    FONT_LARGE = pygame.font.Font(resource_path("assets/fonts/PixelOperator8-Bold.ttf"), 48)
except:
    # Fallback to system font if custom font fails to load
    FONT_SMALL = pygame.font.SysFont(None, 20)
    FONT_MEDIUM = pygame.font.SysFont(None, 36)
    FONT_LARGE = pygame.font.SysFont(None, 48)


# Obstacle types
OBSTACLE_TRIANGLE = 0
OBSTACLE_PLATFORM = 1

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)

# Neon Colors
NEON_PINK = (255, 20, 147)
NEON_GREEN = (57, 255, 20)
NEON_BLUE = (0, 191, 255)
NEON_PURPLE = (138, 43, 226)
NEON_ORANGE = (255, 153, 0)
NEON_BACKGROUND = (10, 10, 40)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cloud Dash")
clock = pygame.time.Clock()

class Player:
    def __init__(self, image_path):
        self.original_image = pygame.image.load(resource_path(image_path))
        self.original_image = pygame.transform.scale(self.original_image, (40, 40))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.rect.height
        self.velocity_y = 0
        self.is_jumping = False
        self.jump_count = 0
        self.rotation = 0
        self.target_rotation = 0  # Target rotation for smooth animation
        self.boost_active = False
        self.boost_time = 0
        self.shield_active = False  # Shield protection from boost
        self.score_multiplier = 1  # Default score multiplier
    
    def jump(self):
        if not self.is_jumping or self.jump_count < 2:  # Allow double jump
            self.velocity_y = -JUMP_FORCE
            self.is_jumping = True
            self.jump_count += 1
            # Always rotate clockwise by adding 90 to target_rotation
            self.target_rotation = (self.target_rotation - 90) % 360
            # Convert to negative value for clockwise rotation in pygame
            if self.target_rotation > 0:
                self.target_rotation -= 360
    
    def update(self):
        # Apply gravity
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        
        # Smooth rotation animation - always rotate clockwise
        if self.rotation != self.target_rotation:
            # Always rotate clockwise (decrease rotation value)
            self.rotation -= ROTATION_SPEED
            
            # Fix rotation if we passed the target
            if self.rotation <= self.target_rotation:
                self.rotation = self.target_rotation
        
        # Check if player is on the ground
        if self.rect.y >= SCREEN_HEIGHT - GROUND_HEIGHT - self.rect.height:
            self.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.rect.height
            self.velocity_y = 0
            self.is_jumping = False
            self.jump_count = 0
            
        # Handle boost
        if self.boost_active:
            if pygame.time.get_ticks() - self.boost_time > 3000:  # 3 seconds boost
                self.boost_active = False
                self.shield_active = False
                self.score_multiplier = 1  # Reset score multiplier when boost ends
                
    def activate_boost(self):
        self.boost_active = True
        self.shield_active = True  # Activate shield with boost
        self.boost_time = pygame.time.get_ticks()
        self.score_multiplier = 2  # Double score when boost is active

    def draw(self, surface):
        # Rotate the image
        rotated_image = pygame.transform.rotate(self.original_image, self.rotation)
        # Get the rect of the rotated image and set its center to the player's center
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        
        # Draw shield effect if active (filled circle with transparency)
        if self.shield_active:
            shield_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 100, 255, 100), (25, 25), 25)
            surface.blit(shield_surface, (self.rect.centerx - 25, self.rect.centery - 25))
            
        # Draw boost effect if active (glow without border)
        if self.boost_active:
            boost_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(boost_surface, (57, 255, 20, 80), (30, 30), 30)
            surface.blit(boost_surface, (self.rect.centerx - 30, self.rect.centery - 30))
            
        surface.blit(rotated_image, rotated_rect)

class Obstacle:
    def __init__(self, x):
        # Randomly choose obstacle type
        self.type = random.choice([OBSTACLE_TRIANGLE, OBSTACLE_PLATFORM])
        
        if self.type == OBSTACLE_TRIANGLE:
            # Triangle dimensions
            self.width = 40
            self.height = 40
            self.rect = pygame.Rect(x, SCREEN_HEIGHT - GROUND_HEIGHT - self.height, self.width, self.height)
            # Define triangle points for collision and drawing
            self.points = [
                (self.rect.x, self.rect.bottom),
                (self.rect.x + self.width, self.rect.bottom),
                (self.rect.x + self.width // 2, self.rect.top)
            ]
        else:
            # Rectangle dimensions
            self.width = 80
            self.height = 30
            self.rect = pygame.Rect(x, SCREEN_HEIGHT - GROUND_HEIGHT - self.height, self.width, self.height)
            
        self.passed = False
        self.landed_on = False  # Track if player has landed on this platform
        self.color = random.choice([NEON_PINK, NEON_GREEN, NEON_BLUE, NEON_PURPLE, NEON_ORANGE])
    
    def update(self, speed=GAME_SPEED):
        self.rect.x -= speed
        # Update triangle points if it's a triangle
        if self.type == OBSTACLE_TRIANGLE:
            self.points = [
                (self.rect.x, self.rect.bottom),
                (self.rect.x + self.width, self.rect.bottom),
                (self.rect.x + self.width // 2, self.rect.top)
            ]
    
    def draw(self, surface):
        # Draw with neon style (glow effect)
        if self.type == OBSTACLE_TRIANGLE:
            # Draw triangle with glow effect
            glow_surface = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
            pygame.draw.polygon(glow_surface, (*self.color[:3], 100), [
                (5, self.height + 5),
                (self.width + 5, self.height + 5),
                (self.width // 2 + 5, 5)
            ])
            surface.blit(glow_surface, (self.rect.x - 5, self.rect.y - 5))
            
            # Draw main triangle
            pygame.draw.polygon(surface, self.color, self.points)
            # Draw outline
            pygame.draw.polygon(surface, WHITE, self.points, 2)
        else:
            # Draw rectangle with glow effect
            glow_surface = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*self.color[:3], 100), (5, 5, self.width, self.height))
            surface.blit(glow_surface, (self.rect.x - 5, self.rect.y - 5))
            
            # Draw main rectangle
            pygame.draw.rect(surface, self.color, self.rect)
            # Draw outline
            pygame.draw.rect(surface, WHITE, self.rect, 2)
            
    def check_collision(self, player_rect):
        # For rectangle, use standard rect collision
        if self.type == OBSTACLE_PLATFORM:
            return player_rect.colliderect(self.rect)
        
        # For triangle, check if player is inside the triangle
        # First check if player rect overlaps with triangle rect (optimization)
        if not player_rect.colliderect(self.rect):
            return False
            
        # Check if player's bottom points are inside the triangle
        bottom_left = (player_rect.left + 5, player_rect.bottom - 5)
        bottom_right = (player_rect.right - 5, player_rect.bottom - 5)
        
        # Simple point in triangle check for bottom corners
        return self.point_in_triangle(bottom_left) or self.point_in_triangle(bottom_right)
    
    def point_in_triangle(self, point):
        # Check if a point is inside the triangle using barycentric coordinates
        x, y = point
        x1, y1 = self.points[0]
        x2, y2 = self.points[1]
        x3, y3 = self.points[2]
        
        def area(x1, y1, x2, y2, x3, y3):
            return abs((x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2))/2.0)
        
        # Calculate area of triangle
        A = area(x1, y1, x2, y2, x3, y3)
        
        # Calculate areas of 3 triangles formed by point and each side
        A1 = area(x, y, x2, y2, x3, y3)
        A2 = area(x1, y1, x, y, x3, y3)
        A3 = area(x1, y1, x2, y2, x, y)
        
        # Check if sum of 3 areas equals the original triangle area
        return abs(A - (A1 + A2 + A3)) < 0.1

class BoostItem:
    def __init__(self, x, y=None):
        # Create a gold coin directly instead of using sprite sheet
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(self.image, NEON_ORANGE, (30, 30), 25)
        pygame.draw.circle(self.image, (255, 215, 0), (30, 30), 22)  # Gold color
        
        # Draw "x2" text on the coin
        text = FONT_SMALL.render("x2", True, WHITE)
        text_rect = text.get_rect(center=(30, 30))
        self.image.blit(text, text_rect)
        
        # Allow custom y position or use default
        if y is None:
            y = SCREEN_HEIGHT - GROUND_HEIGHT - 70
            
        self.rect = pygame.Rect(x, y, 60, 60)
        self.collected = False
        self.animation_angle = 0
        self.animation_speed = 5  # Degrees per frame
        
    def update(self, speed=GAME_SPEED):
        self.rect.x -= speed
        
        # Update animation angle for spinning effect
        self.animation_angle = (self.animation_angle + self.animation_speed) % 360
    
    def draw(self, surface):
        if not self.collected:
            # Add pulsing glow effect
            glow_size = 36 + int(math.sin(math.radians(self.animation_angle)) * 4)
            glow_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (NEON_ORANGE[0], NEON_ORANGE[1], NEON_ORANGE[2], 100), (40, 40), glow_size)
            surface.blit(glow_surface, (self.rect.x - 10, self.rect.y - 10))
            
            # Draw the coin with a slight bounce effect
            bounce_offset = int(math.sin(math.radians(self.animation_angle * 2)) * 3)
            surface.blit(self.image, (self.rect.x, self.rect.y + bounce_offset))

class Game:
    def __init__(self):
        # Randomly choose between pixel.png and pixel_1.png for player character
        player_image = random.choice(["assets/images/character/pixel.png", "assets/images/character/pixel_1.png"])
        self.player = Player(player_image)
        self.obstacles = []
        self.boost_items = []
        self.score = 0
        self.game_over = False
        self.last_obstacle_time = pygame.time.get_ticks()
        self.last_boost_time = pygame.time.get_ticks()
        self.last_action_time = pygame.time.get_ticks()
        self.idle_state = False
        
        # Load theme music and play at low volume
        try:
            pygame.mixer.music.load("assets/audio/them-song.mp3")
            pygame.mixer.music.set_volume(MUSIC_MENU_VOLUME)  # Start at 10% volume
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.music_playing = True
            self.game_active = False  # Track if gameplay has started
            print("Theme music playing at 10% volume")
        except Exception as e:
            print(f"Could not load theme music: {e}")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # Any key press resets the idle timer
                self.last_action_time = pygame.time.get_ticks()
                
                # Handle idle state volume
                if self.idle_state and self.game_active:
                    self.idle_state = False
                    pygame.mixer.music.set_volume(MUSIC_NORMAL_VOLUME)  # Force 100% volume
                    print("Key pressed: setting volume to 100%")
                
                # Space key starts the game or makes the player jump
                if event.key == pygame.K_SPACE:
                    if not self.game_active and not self.game_over:
                        # Start the game
                        self.game_active = True
                        pygame.mixer.music.set_volume(MUSIC_NORMAL_VOLUME)  # Full volume
                        print("Game started - music at 100% volume")
                    elif self.game_active:
                        # Jump only if game is active
                        self.player.jump()
                        
                # Reset game if game over
                if event.key == pygame.K_r and self.game_over:
                    self.reset()
    
    def check_idle_state(self):
        # Separate method to handle idle state and audio volume
        current_time = pygame.time.get_ticks()

        # Check for idle state (5 seconds of inactivity)
        if current_time - self.last_action_time > 5000 and not self.idle_state:
            self.idle_state = True
            # Set volume to 30% when in idle state
            pygame.mixer.music.set_volume(MUSIC_IDLE_VOLUME)
            print("Setting idle volume: 30%")  # Debug message
        
        # Check if player is active
        elif (self.player.velocity_y != 0 or self.player.boost_active) and self.idle_state:
            self.idle_state = False
            # Set volume to 100% when active
            pygame.mixer.music.set_volume(MUSIC_NORMAL_VOLUME)
            print("Setting active volume: 100%")  # Debug message
            self.last_action_time = current_time

            
    def update(self):
        if not self.game_over:
            self.player.update()
            
            # Check and update idle state
            self.check_idle_state()
            
            # Only update game elements if game is active
            if self.game_active:
                # Determine current game speed
                current_speed = BOOST_SPEED if self.player.boost_active else GAME_SPEED
                
                # Generate obstacles
                current_time = pygame.time.get_ticks()
                if current_time - self.last_obstacle_time > OBSTACLE_FREQUENCY:
                    self.obstacles.append(Obstacle(SCREEN_WIDTH))
                    self.last_obstacle_time = current_time
            
            # Generate boost items (only if game is active)
            if self.game_active and current_time - self.last_boost_time > BOOST_FREQUENCY:
                # Check if there's enough space for the coin (no obstacles nearby)
                can_place_coin = True
                coin_x = SCREEN_WIDTH
                min_distance = 200  # Minimum distance between coin and obstacles
                
                # Alternate between high and low positions for coins
                coin_positions = [
                    SCREEN_HEIGHT - GROUND_HEIGHT - 70,  # Low position
                    SCREEN_HEIGHT - GROUND_HEIGHT - 150  # High position
                ]
                coin_y = random.choice(coin_positions)
                
                # Create a temporary rect to check for collisions
                temp_coin_rect = pygame.Rect(coin_x, coin_y, 60, 60)
                
                for obstacle in self.obstacles:
                    # Check if any obstacle is too close to the coin position
                    if abs(obstacle.rect.x - coin_x) < min_distance:
                        can_place_coin = False
                        break
                    
                    # Also check if the obstacle rect would overlap with coin rect
                    obstacle_future_rect = pygame.Rect(
                        obstacle.rect.x, obstacle.rect.y, 
                        obstacle.rect.width, obstacle.rect.height
                    )
                    # Project obstacle position to where it would be when coin arrives
                    obstacle_future_rect.x += min_distance
                    
                    if obstacle_future_rect.colliderect(temp_coin_rect):
                        can_place_coin = False
                        break
                
                if can_place_coin:
                    self.boost_items.append(BoostItem(SCREEN_WIDTH, coin_y))
                    self.last_boost_time = current_time
                else:
                    # Delay coin generation by a bit to avoid obstacle
                    self.last_boost_time = current_time - 3000
            
            # Update obstacles (only if game is active)
            if self.game_active:
                for obstacle in self.obstacles[:]:
                    obstacle.update(current_speed)
                    
                    # Check if player passed the obstacle
                    if not obstacle.passed and obstacle.rect.right < self.player.rect.left:
                        obstacle.passed = True
                        # Apply score multiplier when player has boost active
                        self.score += (1 * self.player.score_multiplier)
                
                    # Remove obstacles that are off-screen
                    if obstacle.rect.right < 0:
                        self.obstacles.remove(obstacle)
                        continue
                    
                    # Check for collisions
                    if obstacle.check_collision(self.player.rect):
                        # For platforms, check if player is landing on top
                        if obstacle.type == OBSTACLE_PLATFORM:
                            # Check if player's bottom is near the platform's top and falling
                            platform_top = obstacle.rect.top
                            player_bottom = self.player.rect.bottom
                            
                            # If player is landing on top of platform (with small margin)
                            if player_bottom <= platform_top + 10 and self.player.velocity_y > 0:
                                # Land on platform
                                self.player.rect.bottom = platform_top
                                self.player.velocity_y = 0
                                self.player.is_jumping = False
                                self.player.jump_count = 0
                                obstacle.landed_on = True
                                continue
                    
                        # For triangles or side collisions with platforms, it's game over or shield loss
                        if self.player.shield_active:
                            # Remove shield protection instead of game over
                            self.player.shield_active = False
                            self.obstacles.remove(obstacle)
                        else:
                            self.game_over = True
                            self.game_active = False
                            # Reduce music volume when character dies
                            if self.music_playing:
                                pygame.mixer.music.set_volume(MUSIC_MENU_VOLUME)  # 10% volume
                                print("Character died - music at 10% volume")
            
            # Update boost items (only if game is active)
            if self.game_active:
                for boost in self.boost_items[:]:
                    boost.update(current_speed)
                    
                    # Check if player collected the boost
                    if not boost.collected and self.player.rect.colliderect(boost.rect):
                        boost.collected = True
                        self.player.activate_boost()
                    
                    # Remove boost items that are off-screen or collected
                    if boost.rect.right < 0 or boost.collected:
                        self.boost_items.remove(boost)
            
            # We've already handled collisions in the obstacle update loop above
            # This duplicate collision check is removed to fix the SyntaxError
    
    def draw(self):
        screen.fill(NEON_BACKGROUND)
        
        # Draw "Press SPACE to start" message if game is not active and not game over
        if not self.game_active and not self.game_over:
            start_text = FONT_MEDIUM.render("Press SPACE to start", True, NEON_GREEN)
            text_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(start_text, text_rect)
        
        # Draw ground
        pygame.draw.rect(screen, NEON_BLUE, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        # Add ground glow effect
        pygame.draw.line(screen, NEON_GREEN, (0, SCREEN_HEIGHT - GROUND_HEIGHT), 
                         (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT), 3)
        
        # Draw boost items
        for boost in self.boost_items:
            boost.draw(screen)
            
        # Draw player and obstacles
        self.player.draw(screen)
        for obstacle in self.obstacles:
            obstacle.draw(screen)
        
        # Draw score with custom font
        score_text = FONT_MEDIUM.render(f"Score: {self.score}", True, NEON_GREEN)
        screen.blit(score_text, (10, 10))
        
        # Draw status indicators at top right
        status_x = SCREEN_WIDTH - 10
        status_y = 10
        
        # Draw shield status if active
        if self.player.shield_active:
            shield_text = FONT_SMALL.render("Protected", True, NEON_BLUE)
            shield_rect = shield_text.get_rect(topright=(status_x, status_y))
            
            # Draw background for better visibility
            bg_rect = shield_rect.copy()
            bg_rect.inflate_ip(10, 6)
            pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect, border_radius=5)
            
            screen.blit(shield_text, shield_rect)
            status_y += 25
        
        # Draw boost countdown if active
        if self.player.boost_active:
            remaining = 3 - (pygame.time.get_ticks() - self.player.boost_time) // 1000
            if remaining < 0:
                remaining = 0
            boost_text = FONT_SMALL.render(f"x2 Score: {remaining}s", True, NEON_ORANGE)
            boost_rect = boost_text.get_rect(topright=(status_x, status_y))
            
            # Draw background for better visibility
            bg_rect = boost_rect.copy()
            bg_rect.inflate_ip(10, 6)
            pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect, border_radius=5)
            
            screen.blit(boost_text, boost_rect)
        
        # Draw game over message with custom font
        if self.game_over:
            # Shadow effect for game over text
            game_over_shadow = FONT_LARGE.render("Game Over!", True, (20, 20, 20))
            shadow_rect = game_over_shadow.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 28))
            screen.blit(game_over_shadow, shadow_rect)
            
            # Main game over text
            game_over_text = FONT_LARGE.render("Game Over!", True, NEON_PINK)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
            screen.blit(game_over_text, text_rect)
            
            # Restart instruction
            restart_text = FONT_MEDIUM.render("Press R to restart", True, NEON_GREEN)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            screen.blit(restart_text, restart_rect)
    
    def reset(self):
        # Randomly choose between pixel.png and pixel_1.png for player character on reset
        player_image = random.choice(["assets/images/character/pixel.png", "assets/images/character/pixel_1.png"])
        self.player = Player(player_image)
        self.obstacles = []
        self.boost_items = []
        self.score = 0
        self.game_over = False
        self.last_obstacle_time = pygame.time.get_ticks()
        self.last_boost_time = pygame.time.get_ticks()
        self.last_action_time = pygame.time.get_ticks()
        self.idle_state = False
        self.game_active = True
        
        # Reset music to normal volume when game restarts
        if self.music_playing:
            pygame.mixer.music.set_volume(MUSIC_NORMAL_VOLUME)
            print("Game reset - music at 100% volume")
    
    def run(self):
        # Music will start only when user interacts with the game
        while True:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(60)

# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()