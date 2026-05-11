import pgzrun


# Globale Variablen
WIDTH = 1934
HEIGHT = 972

MOVE_SPEED = 5
JUMP_SPEED = 20
GRAVITY = 0.8
MAX_FALL_SPEED = 15

# Charakter
hero = Actor("red_hero_idle_1", anchor=("center", "bottom"))
hero.midbottom = (200, 100)
hero.vx = 0
hero.vy = 0
hero.on_ground = False

# Powerup-System
powerup_active_timer = 0
powerup_duration = 4 * 60  # 4 Sekunden 
original_move_speed = MOVE_SPEED
original_jump_speed = JUMP_SPEED

# Level-System
current_level = 0

# Level-Definitionen (Plattformen, Türen und Powerups für jedes Level)
LEVELS = [
    {
        "platforms": [
            Actor("platform_1", topleft=(100, 300)),
            Actor("platform_2", topleft=(500, 450)),
            Actor("platform_3", topleft=(1000, 350)),
            Actor("platform_3", topleft=(1400, 450)),
            Actor("corner_platform", topleft=(1654, 400)),
        ],
        "door": Actor("door", bottomleft=(1750, 450)),
        "powerup": Actor("coin", anchor=("center", "center"), pos=(550, 380)),
    },
    {
        "platforms": [
            Actor("platform_2", topleft=(200, 250)),
            Actor("platform_1", topleft=(700, 400)),
            Actor("platform_3", topleft=(1200, 300)),
            Actor("platform_2", topleft=(1600, 500)),
        ],
        "door": Actor("door", bottomleft=(1750, 500)),
        "powerup": Actor("coin", anchor=("center", "center"), pos=(900, 350)),
    },
    {
        "platforms": [
            Actor("platform_3", topleft=(150, 350)),
            Actor("platform_2", topleft=(600, 500)),
            Actor("platform_1", topleft=(1100, 300)),
            Actor("corner_platform", topleft=(1650, 450)),
        ],
        "door": Actor("door", bottomleft=(1750, 450)),
        "powerup": Actor("coin", anchor=("center", "center"), pos=(750, 450)),
    },
]

# Aktuelle Plattformen, Tür und Powerup
platforms = LEVELS[current_level]["platforms"]
door = LEVELS[current_level]["door"]
powerup = LEVELS[current_level]["powerup"]
powerup.notactive = True

# Lava
lava = Actor("lava_top", topleft=(0, HEIGHT - 50))
lava.span_width = WIDTH

def draw():
    # Zeichne Hintergrund
    screen.blit("background", (0, 0))

    # Zeichne Plattformen
    for platform in platforms:
        platform.draw()

    # Zeichne Tür
    door.draw()

    # Zeichne Powerup
    if powerup.notactive:
        powerup.draw()

    # Zeichne Charakter
    hero.draw()

    # Zeichne Lava
    lava_tile_x = lava.left
    while lava_tile_x < lava.left + lava.span_width:
        screen.blit(lava.image, (lava_tile_x, lava.top))
        lava_tile_x += lava.width
    
    # Zeichne Level-Anzeige
    screen.draw.text(f"Level: {current_level + 1}", (20, 20), color=(255, 255, 255))


def update():
    global current_level, platforms, door, powerup, MOVE_SPEED, JUMP_SPEED, powerup_active_timer
    
    # Powerup-Timer aktualisieren
    if powerup_active_timer > 0:
        powerup_active_timer -= 1
    else:
        # Wenn Timer abgelaufen ist, Stats zurücksetzen
        MOVE_SPEED = original_move_speed
        JUMP_SPEED = original_jump_speed
    
    # x-Geschwindigkeit berechnen (Bewegung nach links/rechts)
    hero.vx = 0
    if keyboard.left:
        hero.vx = -MOVE_SPEED
    elif keyboard.right:
        hero.vx = MOVE_SPEED

    # y-Geschwindigkeit berechnen (Springen und Schwerkraft)
    if hero.on_ground and keyboard.space:
        hero.vy = -JUMP_SPEED

    hero.vy = min(hero.vy + GRAVITY, MAX_FALL_SPEED)

    # x-Bewegung ausführen
    hero.x += hero.vx

    # y-Bewegung nach unten ausführen
    if hero.vy >= 0:
        
        # Zielposition des Charakters (in der Luft)
        target_bottom = hero.bottom + hero.vy
        
        # niedrigst mögliche Landeposition (Boden oder Plattform)
        landing_bottom = HEIGHT
        
        # Plattformkollisionen überprüfen
        for platform in platforms:
            if (
                hero.right > platform.left
                and hero.left < platform.right
                and hero.bottom <= platform.top
            ):
                landing_bottom = min(landing_bottom, platform.top)

        if target_bottom >= landing_bottom:
            hero.bottom = landing_bottom
            hero.vy = 0
            hero.on_ground = True
        else:
            hero.bottom = target_bottom
            hero.on_ground = False
    # y-Bewegung nach oben ausführen
    else:
        hero.y += hero.vy
        hero.on_ground = False

    # Powerup-Kollision überprüfen
    if powerup.notactive and hero.colliderect(powerup):
        powerup.notactive = False
        powerup_active_timer = powerup_duration
        MOVE_SPEED = original_move_speed * 2  # Doppelte Geschwindigkeit
        JUMP_SPEED = original_jump_speed * 1.1  # 10% höher springen

    # Bei Berührung mit Lava zur Startposition zurücksetzen
    if (
        hero.right > lava.left
        and hero.left < lava.left + lava.span_width
        and hero.bottom >= lava.top
    ):
        hero.midbottom = (200, 100)
        hero.vx = 0
        hero.vy = 0
        hero.on_ground = False
        # Powerup wieder aktivieren beim Respawn
        powerup.notactive = True
        powerup_active_timer = 0
        MOVE_SPEED = original_move_speed
        JUMP_SPEED = original_jump_speed
    
    # Türkollision überprüfen - zum nächsten Level
    if hero.colliderect(door):
        # Zum nächsten Level wechseln
        current_level = (current_level + 1) % len(LEVELS)
        
        # Neue Plattformen, Tür und Powerup laden
        platforms = LEVELS[current_level]["platforms"]
        door = LEVELS[current_level]["door"]
        powerup = LEVELS[current_level]["powerup"]
        powerup.notactive = True
        
        # Charakter zur Startposition zurücksetzen
        hero.midbottom = (200, 100)
        hero.vx = 0
        hero.vy = 0
        hero.on_ground = False
        
        # Powerup deaktivieren
        powerup_active_timer = 0
        MOVE_SPEED = original_move_speed
        JUMP_SPEED = original_jump_speed
    
    # Aktualisiere das Charakterbild basierend auf der Bewegung
    if not hero.on_ground:
        hero.image = "red_hero_jump" if hero.vy < 0 else "red_hero_fall"
    elif hero.vx != 0:
        hero.image = "red_hero_run_1"
    else:
        hero.image = "red_hero_idle_1"

pgzrun.go()