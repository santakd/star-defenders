#
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

import pygame                       # Pygame library for game development
import sys                          # System-specific parameters and functions
import logging                      # Logging library for detailed debug and info messages
import os                           # Operating system interfaces for file handling and logging setup
import math                         # Math library for explosion animation calculations
import random                       # Random library for procedural sound generation and alien shooting logic
import array                        # Array library for efficient sound buffer creation
from datetime import datetime       # For timestamping log files

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
SCREEN_WIDTH = 1024     
SCREEN_HEIGHT = 768     
FPS = 60                

# Colors (R, G, B)
BLACK = (0, 0, 0)               # Background color       
WHITE = (250, 250, 250)         # Player bullet color
GREEN = (10, 250, 10)           # Player ship color
BLUE = (10, 10, 250)            # Score text color and alien explosion sparks
RED = (250, 10, 10)             # Regular alien color
DEEP_RED = (155, 10, 10)        # Game over text color
DEEP_BLUE = (10, 10, 155)       # Top row alien color
LIGHT_BLUE = (10, 191, 250)     # Alien projectile color

# Game Settings
PLAYER_SPEED = 7                        # Player movement speed (pixels per frame)
BULLET_SPEED = -7                       # Player bullet speed (negative for upwards)
ALIEN_SPEED = 2                         # Alien horizontal speed (pixels per frame)
ALIEN_DROP = 12                         # How much the aliens drop down when they hit the edge (pixels)
ALIEN_BULLET_SPEED = 8                  # Alien bullet speed (positive for downwards)
SHOOT_COOLDOWN = 300                    # Minimum time between shots in milliseconds (300ms = 0.3 seconds)
BULLET_SPACING = 14                     # Distance between the two bullets fired from the player ship (pixels)
TOP_ROW_SCORE = 60                      # Points for destroying a top row alien
OTHER_ROWS_SCORE = 10                   # Points for destroying aliens in rows below the top
ALIEN_SHOOT_TIME_MIN = 2000             # Minimum time between alien shots in milliseconds
ALIEN_SHOOT_TIME_MAX = 4000             # Maximum time between alien shots in milliseconds
END_DELAY_TIME = 15000                  # Time to show end game screen before closing (milliseconds)
SOUND_FREQUENCY = 44100                 # Audio frequency for sound effects
SOUND_SIZE = -16                        # Audio sample size (16-bit signed)
SOUND_CHANNELS = 2                      # Stereo sound
PLAYER_NOISE_AMPLITUDE_MIN = -20000     # Minimum amplitude for procedural noise generation (used in explosion sounds)
PLAYER_NOISE_AMPLITUDE_MAX = 20000      # Maximum amplitude for procedural noise generation (used in explosion sounds)
ALIEN_NOISE_AMPLITUDE_MIN = -24000      # Minimum amplitude for procedural noise generation (used in explosion sounds)
ALIEN_NOISE_AMPLITUDE_MAX = 24000       # Maximum amplitude for procedural noise generation (used in explosion sounds)


# ==========================================
# LOGGING SETUP
# ==========================================
def setup_logging():
    """Sets up timestamped logging for the application."""
    if not os.path.exists('logs'):
        os.makedirs('logs')
   
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
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30), pygame.SRCALPHA)
        ship_points = [(25, 0), (0, 30), (25, 22), (50, 30)]
        pygame.draw.polygon(self.image, GREEN, ship_points)
        cockpit_points = [(25, 8), (20, 20), (30, 20)]
        pygame.draw.polygon(self.image, (0, 255, 255), cockpit_points)
        
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
            
            offset = BULLET_SPACING // 2
            left_x = self.rect.centerx - offset
            right_x = self.rect.centerx + offset
            
            bullet_left = Bullet(left_x, self.rect.top)
            bullet_right = Bullet(right_x, self.rect.top)
            
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
        """Move bullet upwards."""
        self.rect.y += self.speed

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 12))
        self.image.fill(LIGHT_BLUE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = ALIEN_BULLET_SPEED

    def update(self):
        """Move bullet downwards and remove if off-screen."""
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, is_top_row=False):
        super().__init__()
        self.is_top_row = is_top_row
        
        self.score_value = TOP_ROW_SCORE if self.is_top_row else OTHER_ROWS_SCORE
        color = DEEP_BLUE if self.is_top_row else RED
        
        self.image = pygame.Surface((40, 30))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, direction=None, *args, **kwargs):
        """Move alien horizontally if a direction is provided."""
        if direction is not None:
            self.rect.x += (ALIEN_SPEED * direction)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.size = 50
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self.frame = 0
        self.max_frames = 15  

    def update(self, *args, **kwargs):
        """Animates the explosion by drawing expanding sparks."""
        self.frame += 1
        if self.frame > self.max_frames:
            self.kill() 
        else:
            self.image.fill((0, 0, 0, 0))
            progress = self.frame / self.max_frames
            green_val = max(int(255 * (1 - progress)), 0)
            color = (255, green_val, 0) 
            
            center = self.size // 2
            for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
                rad = math.radians(angle)
                inner_r = progress * (self.size // 2)
                outer_r = inner_r + 6  
                
                start_x = center + math.cos(rad) * inner_r
                start_y = center + math.sin(rad) * inner_r
                end_x = center + math.cos(rad) * outer_r
                end_y = center + math.sin(rad) * outer_r
                
                pygame.draw.line(self.image, color, (start_x, start_y), (end_x, end_y), 3)

# ==========================================
# PROCEDURAL AUDIO GENERATORS
# ==========================================
def create_explosion_sound():
    """Generates a retro 'crunch' explosion sound procedurally in memory (Heavier/Punchy)."""
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=SOUND_FREQUENCY, size=SOUND_SIZE, channels=SOUND_CHANNELS)
        
    freq, fmt, channels = pygame.mixer.get_init()
    duration = 0.22  # Slightly longer to let the heavier low frequencies resonate
    num_samples = int(freq * duration)
    
    buf = array.array('h')
    
    current_noise = 0
    hold_frames = 4  # Holds the random value to lower the pitch (adds bass/weight)
    
    for i in range(num_samples):
        if i % hold_frames == 0:
            # Increased amplitude range for a harder punch
            current_noise = random.randint(ALIEN_NOISE_AMPLITUDE_MIN, ALIEN_NOISE_AMPLITUDE_MAX) 
            
        # Fast fade out for a snappy impact
        envelope = (1.0 - (i / num_samples)) ** 2
        sample = int(current_noise * envelope)
        
        for _ in range(channels):
            buf.append(sample)
            
    return pygame.mixer.Sound(buffer=buf)

def create_player_explosion_sound():
    """Generates a deeper, longer rumbling explosion sound for the player ship."""
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=SOUND_FREQUENCY, size=SOUND_SIZE, channels=SOUND_CHANNELS)
        
    freq, fmt, channels = pygame.mixer.get_init()
    duration = 1.0  # Much longer duration
    num_samples = int(freq * duration)
    
    buf = array.array('h')
    
    current_noise = 0
    # Hold a random value for several frames to drop the frequency (creates a deeper bass/rumble)
    hold_frames = 8 
    
    for i in range(num_samples):
        if i % hold_frames == 0:
            current_noise = random.randint(PLAYER_NOISE_AMPLITUDE_MIN, PLAYER_NOISE_AMPLITUDE_MAX) # Reduced amplitude range to prevent it from being overwhelmingly loud, while still giving a strong presence
            
        # Fuller envelope that lingers longer before dying out
        envelope = (1.0 - (i / num_samples)) ** 1.5 
        sample = int(current_noise * envelope)
        
        for _ in range(channels):
            buf.append(sample)
            
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
            
            self.font_large = pygame.font.SysFont('arial', 44, bold=True)
            self.font_medium = pygame.font.SysFont('arial', 22)
            
            self.running = True
            self.game_started = False
            self.game_over = False
            self.victory = False
            self.score = 0
            
            # --- STATS TRACKING ---
            self.trigger_pressed = 0           
            self.bullets_fired = 0   
            self.bullets_hit = 0
            self.bullets_missed = 0
            self.accuracy_score = 0.0
            
            self.start_time = pygame.time.get_ticks()
            self.duration_seconds = 0.0
            self.stats_logged = False
            self.end_delay_started_time = 0
            
            # Sprite Groups
            self.all_sprites = pygame.sprite.Group()
            self.aliens = pygame.sprite.Group()
            self.bullets = pygame.sprite.Group()
            self.enemy_bullets = pygame.sprite.Group()
            
            # Timers for alien shooting
            self.next_alien_shoot_time = pygame.time.get_ticks() + random.randint(ALIEN_SHOOT_TIME_MIN, ALIEN_SHOOT_TIME_MAX)

            # Entity Setup
            self.player = Player()
            self.all_sprites.add(self.player)
            self._create_fleet()
            
            # Generate the sounds in memory during boot
            self.explosion_sound = create_explosion_sound()
            self.player_explosion_sound = create_player_explosion_sound()
            
            self.alien_direction = 1 
            
            logging.info("Game initialized successfully.")
        except Exception as e:
            logging.critical("Failed to initialize Pygame: %s", str(e), exc_info=True)
            raise

    def _create_fleet(self):
        """Generates the initial grid of aliens."""
        logging.info("Generating alien fleet...")
        rows, cols = 5, 10
        for row in range(rows):
            is_top = (row == 0)
            for col in range(cols):
                alien = Alien(60 + col * 60, 50 + row * 40, is_top_row=is_top)
                self.all_sprites.add(alien)
                self.aliens.add(alien)

    def process_events(self):
        """Process keyboard and system events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.KEYDOWN:
                # Start game on any key press
                if not self.game_started:
                    self.game_started = True
                    self.start_time = pygame.time.get_ticks() # Reset stats timer
                    logging.info("Game started by player.")
                    continue
                    
                # Only allow shooting if game is active
                if not self.game_over and not self.victory:
                    if event.key == pygame.K_SPACE:
                        bullets = self.player.shoot()
                        
                        # CRITICAL: Only process if bullets were actually fired (not on cooldown)
                        if bullets: 
                            self.trigger_pressed += 1
                            self.bullets_fired += len(bullets)
                            logging.debug("Trigger Pressed count: %d", self.trigger_pressed)
                            
                            for bullet in bullets:
                                self.all_sprites.add(bullet)
                                self.bullets.add(bullet)

    def _trigger_player_death(self, death_reason):
        """Handles the logic and visuals when the player is destroyed."""
        self.game_over = True
        logging.info(death_reason)
        
        # Create an explosion at the player's exact location
        burst = Explosion(self.player.rect.center)
        self.all_sprites.add(burst)
        
        # Play the deeper, longer sound and physically remove the player ship
        self.player_explosion_sound.play()
        self.player.kill()

    def update_logic(self):
        """Update game state, sprites, and check collisions."""
        
        # --- NEW: Wait for player to start ---
        if not self.game_started:
            return
            
        # --- END GAME LOGIC & TIMER ---
        if self.game_over or self.victory:
            
            # Even though the game is over (and frozen), allow explosions to finish animating
            for sprite in self.all_sprites:
                if isinstance(sprite, Explosion):
                    sprite.update()
            
            if not self.stats_logged:
                self.duration_seconds = round((pygame.time.get_ticks() - self.start_time) / 1000.0, 1)
                self.bullets_missed += len(self.bullets)
                
                if self.bullets_fired > 0:
                    accuracy = (self.bullets_hit / self.bullets_fired) * 100
                else:
                    accuracy = 0.0
                self.accuracy_score = round(accuracy, 1)
                
                logging.info("=== GAME OVER STATS ===")
                logging.info(f"Result: {'VICTORY' if self.victory else 'DEFEAT'}")
                logging.info(f"Score: {self.score}")
                logging.info(f"Duration: {self.duration_seconds} seconds")
                logging.info(f"Accuracy Score: {self.accuracy_score}%")
                logging.info(f"Trigger Pressed: {self.trigger_pressed}")
                logging.info(f"Total Shots: {self.bullets_fired}")
                logging.info(f"Total Hits: {self.bullets_hit}")
                logging.info(f"Total Missed: {self.bullets_missed}")
                
                logging.info("=======================")
                
                self.stats_logged = True
                self.end_delay_started_time = pygame.time.get_ticks()
            
            if pygame.time.get_ticks() - self.end_delay_started_time > END_DELAY_TIME:
                self.running = False
                
            return 

        # --- NORMAL GAME LOGIC ---
        self.all_sprites.update()
        
        # Check Player Missed Bullets
        for bullet in self.bullets:
            if bullet.rect.bottom < 0:
                self.bullets_missed += 1
                bullet.kill()
        
        # Alien Fleet Movement
        self.aliens.update(self.alien_direction)
        edge_hit = False
        for alien in self.aliens:
            if alien.rect.right >= SCREEN_WIDTH or alien.rect.left <= 0:
                edge_hit = True
                break
                
        if edge_hit:
            self.alien_direction *= -1
            for alien in self.aliens:
                alien.rect.y += ALIEN_DROP
                # Alien physically reaching bottom triggers death
                if alien.rect.bottom >= self.player.rect.top:
                    self._trigger_player_death("Aliens reached the player. Game Over.")

        # --- ALIEN FIRING LOGIC ---
        now = pygame.time.get_ticks()
        if now > self.next_alien_shoot_time:
            top_aliens = [a for a in self.aliens if a.is_top_row]
            
            if top_aliens and len(self.enemy_bullets) < 2:
                shooter = random.choice(top_aliens)
                enemy_bullet = EnemyBullet(shooter.rect.centerx, shooter.rect.bottom)
                self.all_sprites.add(enemy_bullet)
                self.enemy_bullets.add(enemy_bullet)
                logging.debug("Top row alien fired a projectile.")
                
            self.next_alien_shoot_time = now + random.randint(ALIEN_SHOOT_TIME_MIN, ALIEN_SHOOT_TIME_MAX)

        # Collision Check: Player Bullets vs Aliens
        hits = pygame.sprite.groupcollide(self.aliens, self.bullets, True, True)
        for alien, bullet_list in hits.items():
            self.score += alien.score_value
            self.bullets_hit += len(bullet_list)
            
            burst = Explosion(alien.rect.center)
            self.all_sprites.add(burst)
            self.explosion_sound.play()

        # Check Victory
        if len(self.aliens) == 0:
            self.victory = True
            logging.info("All aliens destroyed. Victory!")
            logging.info("May the force be with you, Defender.")

        # Check Collision: Aliens vs Player (Physical Crash)
        if pygame.sprite.spritecollideany(self.player, self.aliens):
            self._trigger_player_death("Player collided with alien. Game Over.")

        # Check Collision: Enemy Bullets vs Player (Shot)
        if pygame.sprite.spritecollideany(self.player, self.enemy_bullets):
            self._trigger_player_death("Player hit by alien projectile. Game Over.")

    def draw(self):
        """Render graphics to the screen."""
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        
        # UI: Top Left Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, BLUE)
        self.screen.blit(score_text, (10, 10))
        
        # Start Screen Overlay ---
        if not self.game_started:
            start_text = self.font_large.render("PRESS ANY KEY TO START", True, LIGHT_BLUE)
            # Center perfectly on both X and Y axes
            start_x = SCREEN_WIDTH // 2 - start_text.get_width() // 2
            start_y = SCREEN_HEIGHT // 2 - start_text.get_height() // 2
            self.screen.blit(start_text, (start_x, start_y))
        # ------------------------------------------------

        # UI: Game Over / Victory Screen & Stats
        if self.game_over or self.victory:
            banner_text = "ALIENS DESTROYED. YOU WIN!" if self.victory else "GAME OVER"
            banner_color = GREEN if self.victory else DEEP_RED
            banner_surf = self.font_large.render(banner_text, True, banner_color)
            
            stats_line1 = f"Game Duration: {self.duration_seconds}s"
            stats_line2 = f"Accuracy: {self.accuracy_score}%"
            stats_line3 = f"Trigger Pressed: {self.trigger_pressed}"
            stats_line4 = f"Total Shots: {self.bullets_fired} "
            stats_line5 = f"Total Hits: {self.bullets_hit}"
            stats_line6 = f"Total Missed: {self.bullets_missed}"
            
            # --- DYNAMIC COUNTDOWN LOGIC ---
            if self.stats_logged:
                # Calculate how many milliseconds have passed since the game ended
                time_passed_ms = pygame.time.get_ticks() - self.end_delay_started_time
                # Subtract from total delay time and convert to seconds (ceiling rounds up so 19.9s reads as 20)
                remaining_seconds = math.ceil((END_DELAY_TIME - time_passed_ms) / 1000)
                # Ensure it never displays 0 or a negative number right before closing
                remaining_seconds = max(1, remaining_seconds)
                
                stats_line7 = f"Auto closing in {remaining_seconds} seconds..."
            else:
                stats_line7 = "Calculating stats..."
            # -------------------------------
            
            stats_surf1 = self.font_medium.render(stats_line1, True, WHITE)
            stats_surf2 = self.font_medium.render(stats_line2, True, WHITE)
            stats_surf3 = self.font_medium.render(stats_line3, True, WHITE)
            stats_surf4 = self.font_medium.render(stats_line4, True, WHITE)
            stats_surf5 = self.font_medium.render(stats_line5, True, WHITE)
            stats_surf6 = self.font_medium.render(stats_line6, True, WHITE)
            
            # Rendering line 7 in a slightly different color (e.g., LIGHT_BLUE) so it acts as a footer
            stats_surf7 = self.font_medium.render(stats_line7, True, LIGHT_BLUE)
            
            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2
            
            # Shifted the whole block UP by 20 pixels to account for the new line
            self.screen.blit(banner_surf, (center_x - banner_surf.get_width() // 2, center_y - 170))
            self.screen.blit(stats_surf1, (center_x - stats_surf1.get_width() // 2, center_y - 90))
            self.screen.blit(stats_surf2, (center_x - stats_surf2.get_width() // 2, center_y - 50))
            self.screen.blit(stats_surf3, (center_x - stats_surf3.get_width() // 2, center_y - 10))
            self.screen.blit(stats_surf4, (center_x - stats_surf4.get_width() // 2, center_y + 30))
            self.screen.blit(stats_surf5, (center_x - stats_surf5.get_width() // 2, center_y + 70))
            self.screen.blit(stats_surf6, (center_x - stats_surf6.get_width() // 2, center_y + 110))
            
            # Added a slightly larger gap (60px instead of 40px) to separate the system message from the stats
            self.screen.blit(stats_surf7, (center_x - stats_surf7.get_width() // 2, center_y + 170))
            
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
        logging.critical("Fatal application error occurred: %s", str(e), exc_info=True)
        sys.exit(1)