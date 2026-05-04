#   __.-._
#   '-._"7'
#    /'.-c
#    |  //
#   _)_/||
#
# star_defenders.py - A production-grade implementation of the classic game using Pygame.
# Author: santakd
# Contact: santakd at gmail dot com
# Date: May 04, 2026
# Version: 1.0.8
# License: MIT License 
#
# ========================================================================
# Star Defenders — Installation & Run Instructions
# ========================================================================
#
# REQUIREMENTS
#   Python 3.9+   (https://www.python.org/downloads/)
#   pip3 install pygame 
#
# RUN
#   python3 star_defenders.py
#
# CONTROLS:
#    Left Arrow: Move left.
#    Right Arrow: Move right.
#    Spacebar: Fire bullet.
#
#    Note: You cannot hold the spacebar to shoot a solid beam; there is a built-in cooldown logic dictating the fire rate.
#    The weapon to a "Twin-Linked" or dual-blaster setup.
#    Each time you press the spacebar, it fires two bullets simultaneously, one from the left side of the ship and one from the right.
#    This design choice adds a layer of strategy and visual flair, as players can cover more area and feel more powerful with each shot, while still maintaining a balanced fire rate to keep the game challenging and engaging.

import pygame
import sys
import logging
import os
import math
import random
import array
from datetime import datetime

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
SCREEN_WIDTH = 1024     # A wider screen allows for more strategic movement and a more cinematic feel, while still being a common resolution that runs well on most hardware. It gives players ample room to dodge and weave through alien attacks, and creates a satisfying sense of scale as the fleet of aliens approaches.
SCREEN_HEIGHT = 768     # A taller screen provides a more immersive vertical playfield, allowing players to see more of the alien fleet as they descend. It also gives a better sense of depth and progression as the aliens get closer to the player, increasing tension and engagement. This resolution is still widely supported and offers a good balance between visual appeal and performance.
FPS = 60                # A standard frame rate for smooth gameplay. It allows for responsive controls and fluid animations while still being achievable on a wide range of hardware. This ensures that the game feels polished and professional without requiring excessive resources, making it accessible to more players.

# Colors (R, G, B)
BLACK = (0, 0, 0)       # The black background creates a classic space setting, allowing the vibrant colors of the player ship, aliens, and explosions to pop visually. It also helps to reduce eye strain during extended play sessions and gives the game a timeless, arcade-style aesthetic that appeals to both nostalgic players and new audiences alike.
WHITE = (250, 250, 250) # The bright white color for bullets ensures they stand out clearly against the black space background, making it easy for players to track their shots and aim effectively. This high contrast also adds to the visual satisfaction of firing, as the bullets create a striking visual effect as they shoot upwards towards the alien fleet.
GREEN = (10, 250, 10)   # The vibrant green color for the player's ship gives it a distinct and visually appealing look that stands out against the dark background. It evokes a sense of energy and life, making the player's avatar feel dynamic and heroic as they battle against the alien invaders. This choice also adds to the overall retro arcade aesthetic, giving the game a fun and engaging visual style.
RED = (250, 10, 10)     # The bright red color for the aliens creates a strong visual contrast against the black background, making them easily identifiable as threats that players need to target and destroy. Red is often associated with danger and urgency, which adds to the tension and excitement of the game as players see the red alien fleet advancing towards them.
                        #This color choice enhances the overall arcade feel and helps to create a visually engaging experience that keeps players on their toes.

# Game Settings
PLAYER_SPEED = 5        # The player's ship moves 5 pixels per frame, which translates to 300 pixels per second at 60 FPS. This speed allows for responsive controls while still requiring skillful maneuvering to dodge alien attacks and position for shots.
BULLET_SPEED = -7       # Negative value to move upwards. This means bullets will travel 7 pixels per frame, or 420 pixels per second, giving them a satisfying speed that allows players to react and aim effectively without feeling too slow or too fast.
ALIEN_SPEED = 2         # Aliens will move 2 pixels per frame horizontally, which creates a steady pace that ramps up tension as they approach the player. This speed allows for strategic movement and dodging while still providing a challenge.
ALIEN_DROP = 12         # When the alien fleet hits the edge of the screen, they will drop down by 12 pixels. This creates a sense of urgency as the aliens get closer to the player, while still giving them enough time to react and shoot before they reach the bottom.
SHOOT_COOLDOWN = 300    # This means the player can fire a new pair of bullets every 300 milliseconds, which balances the power of the dual shots with a reasonable rate of fire to keep the game challenging and prevent spamming.
BULLET_SPACING = 14     # Distance between the dual bullets when fired. This spacing creates a visually appealing spread that allows players to cover more area and increases the chances of hitting multiple aliens, while still maintaining a tight enough formation to feel like a cohesive twin-blaster shot.
                        # I used 14 so it divides cleanly by 2, placing a bullet perfectly 7 pixels to the left and 7 pixels to the right of the center!

# ==========================================
# LOGGING SETUP
# ==========================================
def setup_logging():
    """Sets up timestamped logging for the application."""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    # Create a log file with a timestamp in the filename for better organization and debugging
    # This ensures that each time you run the game, a new log file is created with a unique name based on the current date and time, making it easier to track and analyze logs from different sessions without overwriting previous logs.    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join('logs', f"star_defenders_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("Logging initialized. Log file: %s", log_filename)

# ==========================================
# GAME ENTITIES
# ==========================================

# pygame.SRCALPHA: By adding this flag to the Surface, Pygame knows that the "empty" parts of our 50x30 canvas should be completely invisible (transparent), 
# allowing the black space background to show through.
#
# pygame.draw.polygon: This allows us to draw any shape by feeding it a list of X and Y coordinates.
#    The ship_points draw a sweeping triangular dart shape with an indented thruster area at the back.
#    The cockpit_points overlay a tiny blue triangle near the front to serve as the window!

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 1. Create a transparent surface (SRCALPHA) so the background doesn't show a black box
        self.image = pygame.Surface((50, 30), pygame.SRCALPHA)
        
        # 2. Define the points of the spacecraft (Nose, Left Wing, Bottom Inner, Right Wing)
        ship_points = [(25, 0), (0, 30), (25, 22), (50, 30)]
        
        # 3. Draw the main green spacecraft body
        pygame.draw.polygon(self.image, GREEN, ship_points)
        
        # 4. Draw a small cyan cockpit for extra "production-grade" detail
        cockpit_points = [(25, 8), (20, 20), (30, 20)]
        pygame.draw.polygon(self.image, (0, 255, 255), cockpit_points)
        
        # 5. Set up the collision rectangle and positioning
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = PLAYER_SPEED
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        """Handle keyboard inputs and boundaries."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def shoot(self):
        """Creates a pair of bullets if cooldown has passed."""
        now = pygame.time.get_ticks()
        if now - self.last_shot > SHOOT_COOLDOWN:
            self.last_shot = now
            logging.debug("Player fired dual bullets.")
            
            # Calculate the left and right spawn points
            offset = BULLET_SPACING // 2
            left_x = self.rect.centerx - offset
            right_x = self.rect.centerx + offset
            
            # Create both bullets
            bullet_left = Bullet(left_x, self.rect.top)
            bullet_right = Bullet(right_x, self.rect.top)
            
            # Return them as a list so the Game engine can process both
            return [bullet_left, bullet_right]
        return None

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = BULLET_SPEED

    def update(self):
        """Move bullet and remove if off-screen."""
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    # ADDED: direction=None and *args, **kwargs to safely absorb mismatched group updates
    def update(self, direction=None, *args, **kwargs):
        """Move alien horizontally if a direction is provided."""
        if direction is not None:
            self.rect.x += (ALIEN_SPEED * direction)

    # To add a satisfying "burst" or "spark" effect when an alien is destroyed, we can create an Explosion sprite. 
    # This sprite will use Pygame's drawing tools to animate outward-expanding sparks and then automatically delete itself when the animation is finished.
    # Dynamic Animation: Every frame, the Explosion sprite clears its canvas and redraws the 8 lines slightly further out.
    # Math & Trigonometry: It uses math.cos and math.sin to perfectly calculate 8 directions (every 45 degrees) for the sparks to travel.
    # Color Blending: It dynamically calculates the RGB values. It starts at (255, 255, 0) which is Yellow, and over 15 frames, drops the middle value to 0, resulting in (255, 0, 0) which is Red. 
    # This simulates a cooling spark.
    # Self-Cleaning: Once the self.frame reaches self.max_frames, the sprite calls self.kill(). This safely removes it from self.all_sprites. 
    # This ensures the game uses minimal memory and won't slow down over time (a critical production-grade game design rule!).

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.size = 50
        # Create a transparent surface for the explosion
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self.frame = 0
        self.max_frames = 15  # The explosion lasts for 15 frames

    def update(self, *args, **kwargs):
        """Animates the explosion by drawing expanding sparks."""
        self.frame += 1
        if self.frame > self.max_frames:
            self.kill()  # Remove the sprite when the animation finishes
        else:
            # Clear the previous frame's drawings
            self.image.fill((0, 0, 0, 0))
            
            # Calculate how far along the explosion is (0.0 to 1.0)
            progress = self.frame / self.max_frames
            
            # Color shifts from Yellow to Red as it expands
            green_val = max(int(255 * (1 - progress)), 0)
            color = (255, green_val, 0) 
            
            center = self.size // 2
            # Draw 8 sparks shooting outward
            for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
                rad = math.radians(angle)
                
                # Calculate inner and outer points for the spark lines
                inner_r = progress * (self.size // 2)
                outer_r = inner_r + 6  # Spark length
                
                start_x = center + math.cos(rad) * inner_r
                start_y = center + math.sin(rad) * inner_r
                end_x = center + math.cos(rad) * outer_r
                end_y = center + math.sin(rad) * outer_r
                
                pygame.draw.line(self.image, color, (start_x, start_y), (end_x, end_y), 3)

    # We will generate a quick burst of "white noise" that rapidly fades out (creating a retro static "crunch" or "boom" sound) 
    # using Python's built-in array and random modules, and feed that raw data directly to Pygame's mixer.
    # Channel Management: By calling .play() on a pygame.mixer.Sound object, Pygame automatically handles audio channels. 
    # If you destroy 5 aliens at once with a laser beam, it will overlap the sounds dynamically without cutting the previous ones off.
    # Audio Envelopes: The math (envelope = (1.0 - (i / num_samples)) ** 2) applies a fast quadratic decay. 
    # It hits loud and tapers off exponentially, which is the exact technique retro synthesizers (like the NES or Atari) used to emulate percussion and explosions using noise channels!

def create_explosion_sound():
    """Generates a retro 'crunch' explosion sound procedurally in memory."""
    # Ensure the Pygame mixer is initialized
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2)
        
    freq, fmt, channels = pygame.mixer.get_init()
    duration = 0.15  # seconds
    num_samples = int(freq * duration)
    
    # 'h' creates an array of signed 16-bit integers, which matches Pygame's default mixer size (-16)
    buf = array.array('h')
    
    for i in range(num_samples):
        # Create an envelope that fades from 1.0 to 0.0 rapidly (x^2 curve for punchiness)
        envelope = (1.0 - (i / num_samples)) ** 2
        
        # Generate random static noise, scaled by the envelope volume
        noise = random.randint(-16000, 16000) 
        sample = int(noise * envelope)
        
        # Append the sample for each audio channel (Left/Right for stereo)
        for _ in range(channels):
            buf.append(sample)
            
    # Feed the raw memory buffer directly into a Pygame Sound object
    return pygame.mixer.Sound(buffer=buf)

# ==========================================
# MAIN GAME CONTROLLER
# ==========================================
class Game:
    def __init__(self):
        try:
            pygame.init()
            pygame.display.set_caption("Star Defenders - Galactic Edition")
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont('arial', 24)
            
            self.running = True
            self.game_over = False
            self.victory = False
            self.score = 0
            
            # Sprite Groups
            self.all_sprites = pygame.sprite.Group()
            self.aliens = pygame.sprite.Group()
            self.bullets = pygame.sprite.Group()
            
            # Entity Setup
            self.player = Player()
            self.all_sprites.add(self.player)
            self._create_fleet()
            
            # Generate the sound in memory during boot
            self.explosion_sound = create_explosion_sound()

            self.alien_direction = 1 # 1 for right, -1 for left
            
            logging.info("Game initialized successfully.")
        except Exception as e:
            logging.critical("Failed to initialize Pygame: %s", str(e), exc_info=True)
            raise

    def _create_fleet(self):
        """Generates the initial grid of aliens."""
        logging.info("Generating alien fleet...")
        rows, cols = 5, 10
        for row in range(rows):
            for col in range(cols):
                alien = Alien(60 + col * 60, 50 + row * 40)
                self.all_sprites.add(alien)
                self.aliens.add(alien)

    def process_events(self):
        """Process keyboard and system events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.KEYDOWN and not self.game_over and not self.victory:
                if event.key == pygame.K_SPACE:
                    bullet = self.player.shoot()
                    if bullet:
                        self.all_sprites.add(bullet)
                        self.bullets.add(bullet)

    def update_logic(self):
        """Update game state, sprites, and check collisions."""
        if self.game_over or self.victory:
            return

        self.all_sprites.update()
        
        # Alien Fleet Movement logic
        self.aliens.update(self.alien_direction)
        
        # Check if fleet hit the screen edges
        edge_hit = False
        for alien in self.aliens:
            if alien.rect.right >= SCREEN_WIDTH or alien.rect.left <= 0:
                edge_hit = True
                break
                
        if edge_hit:
            self.alien_direction *= -1
            for alien in self.aliens:
                alien.rect.y += ALIEN_DROP
                # Check if aliens reached the player
                if alien.rect.bottom >= self.player.rect.top:
                    self.game_over = True
                    logging.info("Aliens reached the player. Game Over.")

        # Collision Check: Bullets vs Aliens
        hits = pygame.sprite.groupcollide(self.aliens, self.bullets, True, True)
        
        # 'hits' is a dictionary where the keys are the aliens that were destroyed
        for alien in hits:
            self.score += 10
            logging.debug("Alien destroyed at %s", alien.rect.center)
            
            # Create an explosion at the dead alien's exact location
            burst = Explosion(alien.rect.center)
            self.all_sprites.add(burst)

            # Play the procedural sound effect
            self.explosion_sound.play()

        # Check Victory
        if len(self.aliens) == 0:
            self.victory = True
            logging.info("All aliens destroyed. Victory!")

        # Check Collision: Aliens vs Player
        if pygame.sprite.spritecollideany(self.player, self.aliens):
            self.game_over = True
            logging.info("Player collided with alien. Game Over.")

    def draw(self):
        """Render graphics to the screen."""
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        
        # UI: Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # UI: Game Over / Victory
        if self.game_over:
            go_text = self.font.render("GAME OVER", True, RED)
            self.screen.blit(go_text, (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2))
        elif self.victory:
            win_text = self.font.render("YOU WIN!", True, GREEN)
            self.screen.blit(win_text, (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2))
            
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        logging.info("Starting main game loop.")
        while self.running:
            self.process_events()
            self.update_logic()
            self.draw()
            self.clock.tick(FPS)
            
        logging.info("Game closed gracefully. Final Score: %d", self.score)
        pygame.quit()

# ==========================================
# APPLICATION ENTRY POINT
# ==========================================
if __name__ == "__main__":
    setup_logging()
    
    try:
        logging.info("Launching Star Defenders...")
        game = Game()
        game.run()
    except Exception as e:
        # Catch any unexpected fatal crashes
        logging.critical("Fatal application error occurred: %s", str(e), exc_info=True)
        sys.exit(1)