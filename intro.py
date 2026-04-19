import pgzrun

# Globale Variablen
WIDTH = 1280
HEIGHT = 700

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

# Plattformen
platforms = [
    Actor("platform_1", topleft=(100, 300)),
    Actor("platform_2", topleft=(500, 450)),
    Actor("platform_3", topleft=(1000, 350)),
]

# Lava
lava = Actor("lava_top", topleft=(0, HEIGHT - 50))
lava.span_width = WIDTH

def draw():
    # Zeichne Hintergrund
    screen.blit("background", (0, 0))

    # Zeichne Plattformen
    for platform in platforms:
        platform.draw()

    # Zeichne Charakter
    hero.draw()

    # Zeichne Lava
    lava_tile_x = lava.left
    while lava_tile_x < lava.left + lava.span_width:
        screen.blit(lava.image, (lava_tile_x, lava.top))
        lava_tile_x += lava.width


def update():
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
    
    # Aktualisiere das Charakterbild basierend auf der Bewegung
    if not hero.on_ground:
        hero.image = "red_hero_jump" if hero.vy < 0 else "red_hero_fall"
    elif hero.vx != 0:
        hero.image = "red_hero_run_1"
    else:
        hero.image = "red_hero_idle_1"

pgzrun.go()