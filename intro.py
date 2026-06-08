import pgzrun

# Globale Variablen
WIDTH = 1934
HEIGHT = 972

MOVE_SPEED = 5
JUMP_SPEED = 20
GRAVITY = 0.8
MAX_FALL_SPEED = 15

# Charakter
LEVEL_START = (200, 100)
hero = Actor("red_hero_idle_1", anchor=("center", "bottom"))
hero.midbottom = LEVEL_START
hero.vx = 0
hero.vy = 0
hero.on_ground = False

# Fliegende Gegner-Figur
fly_frames = [f"fly_{i}" for i in range(1, 11)]
fly_frame_index = 0
fly_animation_timer = 0
fly_animation_speed = 5  # Frames bis zum Wechsel
fly_enemy = Actor(fly_frames[0], anchor=("center", "center"))
fly_enemy.pos = (WIDTH - 100, 250)
fly_enemy.vx = -3
fly_enemy.left_bound = 100
fly_enemy.right_bound = WIDTH - 100

# Fester Gegner im ersten Level
static_monster = Actor("fly_1", anchor=("center", "center"))
static_monster.pos = (1400, 400)

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
            Actor("platform_3", topleft=(1650, 300)),
            Actor("platform_3", topleft=(2000, 400)),
            Actor("platform_1", topleft=(2400, 350)),
            Actor("platform_3", topleft=(2800, 500)),
            Actor("platform_1", topleft=(3000, 300)),
            
            Actor("corner_platform", topleft=(3500, 400)),
        ],
        "door": Actor("door", bottomleft=(3550, 440)),
        "powerup": Actor("coin", anchor=("center", "center"), pos=(550, 380)),
    },
    {
        "platforms": [
            Actor("platform_2", topleft=(150, 250)),
            Actor("platform_1", topleft=(700, 400)),
            Actor("platform_3", topleft=(1200, 300)),
            Actor("platform_2", topleft=(1710, 480)),
            Actor("platform_1", topleft=(2010, 380)),
            Actor("platform_3", topleft=(2410, 280)),
            Actor("platform_2", topleft=(2810, 450)),
            Actor("platform_1", topleft=(3410, 300)),
            Actor("corner_platform", topleft=(3500, 100)),
        ],
        "door": Actor("door", bottomleft=(3550, 140)),
        "powerup": Actor("coin", anchor=("center", "center"), pos=(900, 350)),
        "ladder": Actor("ladder", topleft=(3350, 300)),
    },
    {
        "platforms": [
            Actor("platform_3", topleft=(150, 350)),
            Actor("platform_2", topleft=(600, 500)),
            Actor("platform_1", topleft=(1100, 300)),
            Actor("platform_1", topleft=(1100, 300)),
            Actor("platform_3", topleft=(1600, 400)),
            Actor("platform_1", topleft=(2000, 300)),
            Actor("platform_2", topleft=(2400, 300)),
            Actor("platform_1", topleft=(2800, 400)),
            Actor("platform_3", topleft=(3150, 350)),
            Actor("platform_1", topleft=(3410, 300)),
            Actor("platform_1", topleft=(3800, 270)),

            Actor("corner_platform", topleft=(4000, 450)),
        ],
        "door": Actor("door", bottomleft=(4000, 470)),
        "powerup": Actor("coin", anchor=("center", "center"), pos=(750, 450)),
    },
]

# Aktuelle Plattformen, Tür und Powerup
platforms = LEVELS[current_level]["platforms"]
door = LEVELS[current_level]["door"]
powerup = LEVELS[current_level]["powerup"]
powerup.notactive = True
ladder = LEVELS[current_level].get("ladder", None)

# Lava
lava = Actor("lava_top", topleft=(0, HEIGHT - 50))
lava.span_width = WIDTH

# Kamera / Weltgröße
camera_x = 0
level_width = WIDTH
moving_platforms = []

def setup_dynamic_platforms():
    global moving_platforms
    moving_platforms = []
    if current_level == 0 and len(platforms) > 3:
        platform = platforms[3]
        moving_platforms.append(
            {
                "actor": platform,
                "target_y": platform.y + 200,
                "speed": 2,
                "active": False,
            }
        )
    elif current_level == 2 and len(platforms) > 3:
        for platform in (platforms[1], platforms[2]):
            moving_platforms.append(
                {
                    "actor": platform,
                    "dx": 2,
                    "left_bound": platform.x - 100,
                    "right_bound": platform.x + 100,
                    "active": True,
                }
            )

def compute_level_width():
    global level_width
    max_right = 0
    for p in platforms:
        max_right = max(max_right, p.right)
    max_right = max(max_right, door.right)
    try:
        max_right = max(max_right, powerup.right)
    except Exception:
        pass
    if current_level == 0:
        max_right = max(max_right, static_monster.right)
    # mindestens Bildschirmbreite
    level_width = max(max_right + 200, WIDTH)
    # Lava und Fliege anpassen
    lava.span_width = level_width
    fly_enemy.right_bound = level_width - 100
    fly_enemy.pos = (min(fly_enemy.x, fly_enemy.right_bound), fly_enemy.y)

# initiale Berechnung
compute_level_width()
setup_dynamic_platforms()

def draw():
    # Hintergrund (horizontal kachelnd, verschiebbar)
    bg_x = - (camera_x % WIDTH)
    screen.blit("background", (bg_x, 0))
    if bg_x + WIDTH < WIDTH:
        screen.blit("background", (bg_x + WIDTH, 0))

    # Hilfsfunktion: Actor relativ zur Kamera zeichnen
    def draw_actor_with_camera(a):
        ox, oy = a.x, a.y
        a.x = ox - camera_x
        a.draw()
        a.x, a.y = ox, oy

    # Zeichne Plattformen
    for platform in platforms:
        draw_actor_with_camera(platform)

    # Zeichne Tür
    draw_actor_with_camera(door)

    # Zeichne Leiter
    if ladder:
        draw_actor_with_camera(ladder)

    # Zeichne Powerup
    if powerup.notactive:
        draw_actor_with_camera(powerup)

    # Zeichne Fliegenden Gegner
    draw_actor_with_camera(fly_enemy)

    # Zeichne statischen Gegner im ersten Level
    if current_level == 0:
        static_monster.image = fly_enemy.image
        draw_actor_with_camera(static_monster)

    # Zeichne Charakter
    draw_actor_with_camera(hero)

    # Zeichne Lava (gekachelt über die Weltbreite)
    lava_tile_x = lava.left
    while lava_tile_x < lava.left + lava.span_width:
        screen.blit(lava.image, (lava_tile_x - camera_x, lava.top))
        lava_tile_x += lava.width
    
    # Zeichne Level-Anzeige
    screen.draw.text(f"Level: {current_level + 1}", (20, 20), color=(255, 255, 255))

def update():
    global current_level, platforms, door, powerup, MOVE_SPEED, JUMP_SPEED, powerup_active_timer, fly_frame_index, fly_animation_timer, camera_x, level_width, ladder
    
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

    # Klettern auf der Leiter
    on_ladder = False
    if ladder and hero.colliderect(ladder):
        on_ladder = True
        hero.vx = 0
        if keyboard.up:
            hero.vy = -3
            hero.image = f"greenhero_climb_{(fly_animation_timer // 3) % 15 + 1}"
        elif keyboard.down:
            hero.vy = 3
            hero.image = f"greenhero_climb_{(fly_animation_timer // 3) % 15 + 1}"
        else:
            hero.vy = 0
            hero.on_ground = False

    # y-Geschwindigkeit berechnen (Springen und Schwerkraft)
    if not on_ladder:
        if hero.on_ground and keyboard.space:
            if current_level == 0 and len(platforms) > 3:
                platform3 = platforms[2]
                if (
                    hero.right > platform3.left
                    and hero.left < platform3.right
                    and hero.bottom == platform3.top
                ):
                    for mp in moving_platforms:
                        mp["active"] = True
            hero.vy = -JUMP_SPEED

        hero.vy = min(hero.vy + GRAVITY, MAX_FALL_SPEED)

    # x-Bewegung ausführen
    hero.x += hero.vx

    # Kamera-Offset berechnen (folgt dem Spieler, zentriert)
    max_scroll = max(level_width - WIDTH, 0)
    target_cam = hero.x - WIDTH / 2
    camera_x = max(0, min(target_cam, max_scroll))

    # y-Bewegung nach unten ausführen
    if not on_ladder and hero.vy >= 0:
        
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
    elif not on_ladder:
        hero.y += hero.vy
        hero.on_ground = False
    elif on_ladder:
        hero.y += hero.vy

    # Powerup-Kollision überprüfen
    if powerup.notactive and hero.colliderect(powerup):
        powerup.notactive = False
        powerup_active_timer = powerup_duration
        MOVE_SPEED = original_move_speed * 2  # Doppelte Geschwindigkeit
        JUMP_SPEED = original_jump_speed * 1.1  # 10% höher springen

    # Dynamische Plattformen aktualisieren
    for mp in moving_platforms:
        if not mp["active"]:
            continue
        actor = mp["actor"]
        if "target_y" in mp:
            if actor.y < mp["target_y"]:
                actor.y = min(actor.y + mp["speed"], mp["target_y"])
            else:
                mp["active"] = False
        else:
            actor.x += mp["dx"]
            if actor.x < mp["left_bound"] or actor.x > mp["right_bound"]:
                mp["dx"] = -mp["dx"]
                actor.x += mp["dx"]

    # Fliegenden Gegner bewegen
    fly_enemy.x += fly_enemy.vx
    fly_animation_timer += 1
    if fly_animation_timer >= fly_animation_speed:
        fly_animation_timer = 0
        fly_frame_index = (fly_frame_index + 1) % len(fly_frames)
        fly_enemy.image = fly_frames[fly_frame_index]

    if fly_enemy.right < fly_enemy.left_bound:
        fly_enemy.left = fly_enemy.right_bound

    # Berührung mit der Fliege führt zurück zum Levelstart
    if hero.colliderect(fly_enemy):
        hero.midbottom = LEVEL_START
        hero.vx = 0
        hero.vy = 0
        hero.on_ground = False
        powerup.notactive = True
        powerup_active_timer = 0
        MOVE_SPEED = original_move_speed
        JUMP_SPEED = original_jump_speed

    # Berührung mit dem statischen Gegner im ersten Level führt ebenfalls zurück
    if current_level == 0 and hero.colliderect(static_monster):
        hero.midbottom = LEVEL_START
        hero.vx = 0
        hero.vy = 0
        hero.on_ground = False
        powerup.notactive = True
        powerup_active_timer = 0
        MOVE_SPEED = original_move_speed
        JUMP_SPEED = original_jump_speed

    # Bei Berührung mit Lava zur Startposition zurücksetzen
    if (
        hero.right > lava.left
        and hero.left < lava.left + lava.span_width
        and hero.bottom >= lava.top
    ):
        hero.midbottom = LEVEL_START
        hero.vx = 0
        hero.vy = 0
        hero.on_ground = False
        # Powerup wieder aktivieren beim Respawn
        powerup.notactive = True
        powerup_active_timer = 0
        MOVE_SPEED = original_move_speed
        JUMP_SPEED = original_jump_speed
    
    # Türkollision überprüfen - zum nächsten Level
    if hero.colliderect(door) or keyboard.k:
        # Zum nächsten Level wechseln
        current_level = (current_level + 1) % len(LEVELS)
        
        # Neue Plattformen, Tür und Powerup laden
        platforms = LEVELS[current_level]["platforms"]
        door = LEVELS[current_level]["door"]
        powerup = LEVELS[current_level]["powerup"]
        ladder = LEVELS[current_level].get("ladder", None)
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
        setup_dynamic_platforms()
        compute_level_width()
    
    # Aktualisiere das Charakterbild basierend auf der Bewegung
    if not hero.on_ground:
        hero.image = "red_hero_jump" if hero.vy < 0 else "red_hero_fall"
    elif hero.vx != 0:
        hero.image = "red_hero_run_1"
    else:
        hero.image = "red_hero_idle_1"

pgzrun.go()
