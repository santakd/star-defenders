## 🚀 Star Defenders

![Star_Defenders](https://github.com/santakd/star-defenders/blob/main/star_defenders.gif)

Star Defenders is a classic, arcade-style space shooter built entirely in Python using pygame.

More than just a game, Star Defenders is engineered with production-grade architecture and design. 

It features zero external asset dependencies, relying completely on real-time procedural generation for its graphics, particle physics, and audio.

### 📃 Source File

[star_defenders.py](https://github.com/santakd/star-defenders/blob/main/star_defenders.py) - The only file required to play the game.

    
### ✨ Features

    Zero-Dependency Assets: No need to download .png or .wav files. 
    
    Every visual and sound is generated via math and memory buffers at runtime.

    Procedural Retro Audio: Explosion sounds are created using in-memory Pulse Code Modulation (PCM) wave generation.
    
    With rapid quadratic decay envelopes to perfectly simulate retro 8-bit noise channels.

    3 Escalating Levels with increasing enemy movement and projectile speeds.
    
    Procedural Retro Audio: Explosion sounds are created using in-memory Pulse Code Modulation (PCM) wave generation. 

    With rapid quadratic decay envelopes to perfectly simulate retro 8-bit noise channels.

    Dynamic Particle Effects: Destroying alien ships triggers a mathematical 360-degree radial particle burst that smoothly transitions colors as it dissipates.

    Twin-Linked Weaponry: Configurable dual-blasters with built-in cooldown management on the space ship.

    Dynamic Particle Effects: Destroying alien ships triggers a mathematical 360-degree radial particle burst that smoothly transitions colors as it dissipates.

    Need to Dodge: Need to dodge enemy fire by moving the space ship.

    Enterprise-Grade Logging: Every game session generates a timestamped log file detailing boot sequences, gameplay events, and graceful shutdowns.

    Resilient Error Handling: Global exception catching ensures that if a fatal error occurs, the stack trace is written to the log.
    
    Auto Close: The game shuts down safely without freezing the OS window.


### 🛠️ Getting Started

    Prerequisites: You will need Python 3.x installed on your machine, along with the pygame library.

    Running the Game: Simply run the Python script from your terminal or command prompt:

    python3 star_defenders.py


### 🎮 Controls

    Left Arrow (←): Move your ship left.

    Right Arrow (→): Move your ship right.

    Spacebar (␣): Fire dual-blasters.

*Defend the galaxy, prevent the alien fleet from touching the bottom of the screen, or getting hit and achieve the highest score!*


### 🔬 Under the Hood

For developers interested in the architecture of Star Defenders:

    Object-Oriented Design: The game strictly adheres to OOP principles. Game entities (Player, Alien, Bullet, Explosion) inherit from pygame.sprite.Sprite and manage their own state.

    Resilient Sprite Updates: Pygame group .update() loops are handled with *args, **kwargs safety, allowing diverse entities to share the same update loop without crashing due to mismatched arguments.

    Future-Proof Combat: The shoot() method returns a list of bullet entities rather than a single object, allowing for incredibly easy implementation of future power-ups (e.g., spread-shot, laser beams) without altering the core game loop.

    The game is designed to be lightweight and performant, with a focus on smooth gameplay and responsive controls.

    The code is structured for readability and maintainability, with clear separation of concerns between game entities, logic, rendering, and audio generation.

    All of this adds to the game's unique charm and replayability.


### 📝 Logs & Debugging

If you experience any issues or want to review your gameplay data, check the logs/ directory.

    A new log file (e.g., star_defenders_20260504_114500.log) is automatically generated every time you launch the application.

    All significant game events, player actions, and final statistics are logged to a timestamped file in the "logs" directory for later review.

    The logging system captures:
    - Game start and end times.
    - Player actions (trigger presses, shots fired, hits, misses).
    - Level transitions and completion.
    - Final performance statistics (score, accuracy, duration).   


### ⭐ Like it? Star it!

If you find this project interesting, please give it a star — it helps others discover it too.


*Created with Python & Pygame. Happy Coding and Happy Defending!*

