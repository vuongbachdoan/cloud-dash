# Cloud Dash

A Geometry Dash-inspired platformer game built with Pygame featuring neon visuals and dynamic gameplay.

## Description

Cloud Dash is a fast-paced side-scrolling platformer where you control a rotating cube that must navigate through a series of obstacles. The game features smooth animations, neon visuals, and an adaptive soundtrack that changes based on gameplay state.

## Features

- **Dynamic Gameplay**: Jump over triangles and onto platforms to progress
- **Double Jump**: Press SPACE twice for a double jump
- **Power-ups**: Collect coins for temporary speed boost and shield protection
- **Score Multiplier**: Active boosts double your score
- **Adaptive Music**: Background music changes volume based on game state
- **Neon Visuals**: Vibrant colors and glow effects

## Controls

- **SPACE**: Start game / Jump
- **R**: Restart after game over

## Game Elements

- **Triangles**: Cannot be jumped over, must be avoided
- **Platforms**: Can be jumped on to avoid obstacles
- **Coins**: Collect for temporary speed boost, shield, and 2x score multiplier

## Installation

1. Ensure you have Python and Pygame installed:
   ```
   pip install pygame
   ```

2. Clone the repository or download the game files

3. Run the game:
   ```
   python cloud_dash.py
   ```

## Directory Structure

```
cloud-dash/
├── assets/
│   ├── fonts/
│   │   ├── PixelOperator8.ttf
│   │   └── PixelOperator8-Bold.ttf
│   ├── audio/
│   │   └── them-song.mp3
│   └── images/
│       ├── character/
│       │   ├── pixel.png
│       │   └── pixel_1.png
│       └── objects/
│           └── coin.png
└── geometry_dash.py
```

## Credits

- Developed as a Geometry Dash styled game using Pygame
- Pixel fonts from itch.io
- Background music: Stability AI Stable Audio

Enjoy the game!