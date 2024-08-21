import pygame
import random
import json


pygame.font.init()


class Advancement:
    def __init__(self, name: str, description: str, *, x: int = 100, y: int = 100, size_x = 32, size_y: int = 32, active_time: int = 1500) -> None:
        self.name = name
        self.description = description
        self.done = False
        self.active = True
        self.font = pygame.font.Font(None, 16)
        self.len_name = len(name)
        self.len_description = len(description)
        self.pyRect = pygame.Rect(x, y, size_x, size_y)
        self.closeButton = pygame.Rect(((x + size_x) - 16), (y + 6), 8, 8)
        self.x = x
        self.y = y
        self.size_x = size_x
        self.size_y = size_y
        self.active_time = active_time
    
    def setDone(self, done: bool) -> None:
        self.done = done
    
    def setDescription(self, description: str) -> None:
        self.description = description
    
    def setName(self, name: str) -> None:
        self.name = name
    
    def render(self, screen: pygame.surface.Surface) -> None:
        if self.active:
            pygame.draw.rect(screen, (33, 33, 33), self.pyRect)
            nameRender = self.font.render(self.name, True, (255, 255, 255))
            descriptionRender = self.font.render(self.description, True, (255, 255, 255))
            closeRender = self.font.render("X", True, (255, 0, 0))
            screen.blit(nameRender, (self.x + 4, self.y + 4))
            screen.blit(descriptionRender, (self.x + 4, self.y + 16 + 2))
            screen.blit(closeRender, self.closeButton)
    
    def collision(self, mouse_pos: tuple[int, int], mouse_press: tuple[int, int, int]) -> None:
        mouse_rect = pygame.Rect(mouse_pos[0] - 4, mouse_pos[1] - 4, 8, 8)
        if self.closeButton.colliderect(mouse_rect):
            if mouse_press[0]:
                self.active = False
    
    def timer(self):
        if self.active_time <= 0:
            self.active = False
        self.active_time -= 1


class Advancements:
    def __init__(self, *, advancements: list[Advancement] = []) -> None:
        self.advancements = advancements
    
    def add(self, advancement: Advancement) -> None:
        self.advancements.append(advancement)
    
    def remove(self, advancement: Advancement) -> None:
        self.advancements.append(advancement)
    
    def list(self):
        return self.advancements

def loadPlayerdata():
    try:
        with open("playerdata.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        new_data = {"Advancements": [{"name": "Catching the mile!","description": "Collected 25 points","done": False},{"name": "Getting the jump!","description": "Collected 50 points","done": False},{"name": "Gotta jump far!","description": "Collected 100 points","done": False},{"name": "Jump to the moon and beyond!","description": "Collected 200 points","done": False},{"name": "Jump breaker!","description": "Collected 500 points","done": False},{"name": "Broke the space bar!", "description": "Jump 10,000 times in one session of gameplay","done": False}]}
        with open("playerdata.json", "w") as file:
            json.dump(new_data, file, indent=4)
        with open("playerdata.json", "r") as file:
            return json.load(file)

def dumpPlayerdata(data: dict):
    with open("playerdata.json", "w") as file:
        json.dump(data, file, indent=4)

class App:
    def __init__(self) -> None:
        self.resolution = [600, 400]
        self.money = 0
        self.player_x = 80
        self.player_y = float(self.resolution[1] // 2)
        self.player_texture = pygame.image.load("data/player.png")
        self.obstacle_texture = pygame.image.load("data/obstacle.png")
        self.icon_texture = pygame.image.load("data/player.png")
        self.running = True
        self.max_space_bar_press_timer = 30
        self.max_apply_gravity_timer = 12
        self.clock = pygame.time.Clock()
        self.fps = 120
        self.screen = pygame.display.set_mode(self.resolution)
        self.jumpForce = 40
        self.gravity = 3.2
        self.obstacleMoveSpeed = 3
        self.obstacles = []
        self.max_obstacles = 32
        self.max_spawn_obstacle_counter = 80
        self.is_dead = False
        self.is_dead_one = False
        self.points = 0
        self.max_gravity_change_timer = 80
        self.playerdata = loadPlayerdata()
        self.font = pygame.font.Font(None, 32)
        self.total_jumps = 0
        self.total_deaths = 0
        self.max_achievement_timer = 280
        self.advancements = Advancements()
        pygame.display.set_caption("Rubber Bird")
        pygame.display.set_icon(self.icon_texture)
    
    def spawn_obstacle(self, direction: int) -> None:
        if len(self.obstacles) <= self.max_obstacles:
            if direction == 1:
                height = random.randint(-200, 0)
                obstacle = [self.resolution[0], height, 180, "pipe"]
            else:
                height = random.randint(self.resolution[1] - 200, self.resolution[1])
                obstacle = [self.resolution[0], height, 0, "pipe"]
            self.obstacles.append(obstacle)
    
    def point_up(self) -> None:
        obstacle = [self.resolution[0], 0, 0, "point"]
        self.obstacles.append(obstacle)
    
    def collide_with_obstacle(self, player: pygame.Rect, pipe: pygame.Rect, obstacle: str) -> None | str:
        if not self.is_dead:
            if pipe.colliderect(player):
                if obstacle == "pipe":
                    self.is_dead = True
                    self.is_dead_one = True
                    return "dead"
                if obstacle == "point":
                    self.points += 1
                    return "point"
        return None

    def restart_game(self) -> None:
        self.points = 0
        self.player_x = 80
        self.player_y = float(self.resolution[1] // 2)
        self.is_dead = False
        self.gravity = 3.2
        self.obstacles.clear()
        self.obstacleMoveSpeed = 3

    def run(self) -> None:
        space_bar_press_timer = 0
        apply_gravity_timer = 0
        spawn_obstacle_counter = 0
        gravity_change_timer = self.max_gravity_change_timer
        achievement_timer = self.max_achievement_timer
        
        while (self.running):
            self.clock.tick(self.fps)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r:
                        self.restart_game()
            
            keys = pygame.key.get_pressed()
            mouse_press = pygame.mouse.get_pressed()
            if keys[pygame.K_SPACE]:
                if space_bar_press_timer >= self.max_space_bar_press_timer:
                    space_bar_press_timer = 0
                    self.total_jumps += 1
                    gravity_change_timer = self.max_gravity_change_timer
                    self.player_y += -self.jumpForce
            if mouse_press[0]:
                if space_bar_press_timer >= self.max_space_bar_press_timer:
                    space_bar_press_timer = 0
                    self.total_jumps += 1
                    gravity_change_timer = self.max_gravity_change_timer
                    self.player_y += -self.jumpForce
            
            if self.is_dead:
                if self.is_dead_one:
                    self.total_deaths += 1
                self.is_dead_one = False
                fontRender = self.font.render("You are dead", True, (255, 0, 0))
                self.screen.blit(fontRender, ((self.resolution[0] // 2) - (len("You are dead") * 16) + 64 + 70, self.resolution[1] // 2))
                fontRender = self.font.render("Press 'R' to restart", True, (255, 0, 0))
                self.screen.blit(fontRender, ((self.resolution[0] // 2) - (len("Press 'R' to restart") * 16) + 160 + 70, (self.resolution[1] // 2) + 18))
            
            if apply_gravity_timer >= self.max_apply_gravity_timer:
                apply_gravity_timer = 0
                if gravity_change_timer > 0:
                    self.player_y += -self.gravity
                else:
                    self.player_y += self.gravity
            
            if gravity_change_timer <= 1:
                gravity_change_timer = 1
            
            for obstacle in self.obstacles:
                if obstacle[3] == "pipe":
                    self.screen.blit(pygame.transform.rotate(self.obstacle_texture, obstacle[2]), (obstacle[0], obstacle[1]))
                elif obstacle[3] == "point":
                    pass
                
                if obstacle[0] < 0:
                    num = self.obstacles.index(obstacle)
                    self.obstacles.pop(num)
                
                player = pygame.Rect(self.player_x, self.player_y, 32, 32)
                if obstacle[3] == "pipe":
                    pipe = pygame.Rect(obstacle[0], obstacle[1], 32, 200)
                elif obstacle[3] == "point":
                    pipe = pygame.Rect(obstacle[0], obstacle[1], 16, 400)
                result = self.collide_with_obstacle(player, pipe, obstacle[3])
                if result == "point":
                    num = self.obstacles.index(obstacle)
                    self.obstacles.pop(num)
                
                obstacle[0] += -self.obstacleMoveSpeed
            
            if spawn_obstacle_counter >= self.max_spawn_obstacle_counter:
                spawn_obstacle_counter = 0
                if random.randint(1, 3) == 3:
                    self.spawn_obstacle(1)
                    self.spawn_obstacle(2)
                    self.point_up()
            
            achievement_timer -= 1
            gravity_change_timer -= 1
            apply_gravity_timer += 1
            spawn_obstacle_counter += 1
            if not self.is_dead:
                space_bar_press_timer += 1
            if self.is_dead:
                self.gravity = 16
            
            if self.points > 50:
                self.obstacleMoveSpeed = 5
            elif self.points > 100:
                self.obstacleMoveSpeed = 7
            elif self.points > 150:
                self.obstacleMoveSpeed = 9
            elif self.points > 200:
                self.obstacleMoveSpeed = 11
            
            if self.points > 25:
                if not self.playerdata["Advancements"][0]["done"]:
                    adv = Advancement(self.playerdata["Advancements"][0]["name"], self.playerdata["Advancements"][0]["description"], x=self.resolution[0] - 150, y=self.resolution[1] - 32, size_x=150, active_time=200)
                    self.advancements.add(adv)
                    self.playerdata["Advancements"][0]["done"] = True
            if self.points > 50:
                if not self.playerdata["Advancements"][1]["done"]:
                    adv = Advancement(self.playerdata["Advancements"][1]["name"], self.playerdata["Advancements"][0]["description"], x=self.resolution[0] - 150, y=self.resolution[1] - 32, size_x=150, active_time=200)
                    self.advancements.add(adv)
                    self.playerdata["Advancements"][1]["done"] = True
            if self.points > 100:
                if not self.playerdata["Advancements"][2]["done"]:
                    adv = Advancement(self.playerdata["Advancements"][2]["name"], self.playerdata["Advancements"][0]["description"], x=self.resolution[0] - 150, y=self.resolution[1] - 32, size_x=150, active_time=200)
                    self.advancements.add(adv)
                    self.playerdata["Advancements"][2]["done"] = True
            if self.points > 200:
                if not self.playerdata["Advancements"][3]["done"]:
                    adv = Advancement(self.playerdata["Advancements"][3]["name"], self.playerdata["Advancements"][0]["description"], x=self.resolution[0] - 150, y=self.resolution[1] - 32, size_x=150, active_time=200)
                    self.advancements.add(adv)
                    self.playerdata["Advancements"][3]["done"] = True
            if self.points > 500:
                if not self.playerdata["Advancements"][4]["done"]:
                    adv = Advancement(self.playerdata["Advancements"][4]["name"], self.playerdata["Advancements"][0]["description"], x=self.resolution[0] - 150, y=self.resolution[1] - 32, size_x=150, active_time=200)
                    self.advancements.add(adv)
                    self.playerdata["Advancements"][4]["done"] = True
            if self.total_jumps > 10_000:
                if not self.playerdata["Advancements"][5]["done"]:
                    adv = Advancement(self.playerdata["Advancements"][5]["name"], self.playerdata["Advancements"][0]["description"], x=self.resolution[0] - 150, y=self.resolution[1] - 32, size_x=150, active_time=200)
                    self.advancements.add(adv)
                    self.playerdata["Advancements"][5]["done"] = True
            
            self.screen.blit(self.player_texture, (self.player_x, self.player_y))

            fontRender = self.font.render("{}".format(self.points), True, (0, 0, 0))
            self.screen.blit(fontRender, (self.resolution[0] // 2, 64))

            for advancement in self.advancements.list():
                advancement.render(self.screen)
                advancement.collision(pygame.mouse.get_pos(), pygame.mouse.get_pressed())
                advancement.timer()
            
            pygame.display.flip()
            self.screen.fill((0, 255, 255))
        dumpPlayerdata(self.playerdata)



app = App()
app.spawn_obstacle(1)
app.spawn_obstacle(2)
app.point_up()
app.run()