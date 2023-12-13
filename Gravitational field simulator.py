import pygame
import sys
import random
import math

pygame.init()

#pygame constants
WIDTH, HEIGHT = 900, 600            #Screen size
FPS = 60                            #Frames per second - Increase for more smoothness

#defining colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

#Particle class - Randomly moving particles
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((3, 3))     #Particle size
        self.image.fill(WHITE)                  #Particle colour
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.mass = 1                           #Initial mass
        self.intensity = 1                      #Initial intensity
        self.vel = pygame.Vector2(random.uniform(-1,1), random.uniform(-1,1)).normalize()*random.uniform(1,3)
        self.revolve_center = None
        self.revolve_radius = 0

    def update(self, masses):
        Grav_constant = 0.002                   #Gravitational constant value according to the simulation
        for mass in masses:
            dx = mass.rect.x - self.rect.x      #Identifying slope of trajectory instantenously using differential calculus
            dy = mass.rect.y - self.rect.y
            distance = max(1, math.sqrt(dx**2+dy**2))
            angle = math.atan2(dy, dx)
            force = Grav_constant*mass.mass/(distance**2)*mass.intensity    #Newton's law of Gravitation: g = Gm₁m₂/r²
            self.vel += force * pygame.Vector2(math.cos(angle), math.sin(angle))

        self.rect.move_ip(self.vel)

        if not pygame.Rect(0, 0, WIDTH, HEIGHT).colliderect(self.rect):
            self.rect.center = (random.randint(0, WIDTH), random.randint(0, HEIGHT))

        if self.revolve_center:
            # Rotate the particle around the center if the particle is in the vicinity of a strong gravitational field
            angle = math.atan2(self.rect.centery - self.revolve_center[1], self.rect.centerx - self.revolve_center[0])
            self.rect.centerx = self.revolve_center[0] + int(self.revolve_radius * 1.2 * math.cos(angle))
            self.rect.centery = self.revolve_center[1] + int(self.revolve_radius * 1.2 * math.sin(angle))

# Mass class to represent masses
class Mass(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLUE, (20, 20), 20)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.mass = 1                           # Initial mass
        self.intensity = 1                      # Initial intensity
        self.strength = 1                       # Initial strength

    def grow(self):
        self.mass += 1
        self.intensity += 1.75
        self.strength += 1
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLUE, (20, 20), 20)

# GravitationalField class
class GravitationalField:
    def __init__(self):
        self.particles = pygame.sprite.Group()
        self.masses = pygame.sprite.Group()

    def add_particle(self, particle):
        self.particles.add(particle)

    def add_mass(self, mass):
        self.masses.add(mass)

    def clear_particles(self):
        self.particles.empty()

    def apply_gravitational_field(self):
        for particle in self.particles:
            for mass in self.masses:
                dx = mass.rect.x - particle.rect.x
                dy = mass.rect.y - particle.rect.y
                distance = max(1, math.sqrt(dx ** 2 + dy ** 2))
                angle = math.atan2(dy, dx)
                force = mass.mass/(distance**2)*Grav_constant*mass.intensity
                particle.vel += force * pygame.Vector2(math.cos(angle), math.sin(angle))

            # Check if the particle is close to a strong field and make it revolve around it
            strong_fields = [mass for mass in self.masses if mass.strength > 15]
            for strong_field in strong_fields:
                dx = strong_field.rect.x - particle.rect.x
                dy = strong_field.rect.y - particle.rect.y
                distance = math.sqrt(dx ** 2 + dy ** 2)

                if distance < 50:
                    particle.revolve_center = strong_field.rect.center + 100
                    particle.revolve_radius = 50

                else:
                    particle.revolve_center = None

    def generate_random_particles(self, num_particles):
        self.particle_generation_timer += 1  # Increment the timer

        # Check if enough time has passed to generate new particles
        if self.particle_generation_timer >= self.particle_generation_interval:
            particle_spawn_region = pygame.Rect(100, 100, WIDTH - 200, HEIGHT - 200)
            random_particles = [
                Particle(random.randint(particle_spawn_region.left, particle_spawn_region.right),
                         random.randint(particle_spawn_region.top, particle_spawn_region.bottom)) for _ in range(num_particles/4)
            ]
            self.particles.add(random_particles)
            self.particle_generation_timer = 0

gravitational_field = GravitationalField()                              #Create GravitationalField instance
num_particles = 100                                                     #Create random particles
random_particles = pygame.sprite.Group([Particle(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(num_particles)])
screen = pygame.display.set_mode((WIDTH, HEIGHT))                       #Initialize screen
pygame.display.set_caption("Gravitational Field Simulation")
clock = pygame.time.Clock()

# Main loop
running = True
placing_mass = False

while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button clicked
            placing_mass = True
            mass = Mass(event.pos[0], event.pos[1])
            gravitational_field.add_mass(mass)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left mouse button released
            placing_mass = False

    if placing_mass:
        # Check if there's already a mass at the current position
        existing_masses = pygame.sprite.spritecollide(mass, gravitational_field.masses, False)
        if existing_masses:
            # Grow the existing masses
            for existing_mass in existing_masses:
                existing_mass.grow()
        else:
            gravitational_field.add_mass(mass)

    # Update random particles
    random_particles.update(gravitational_field.masses)

    # Update particles
    gravitational_field.apply_gravitational_field()
    gravitational_field.particles.update()

    # Draw random particles
    random_particles.draw(screen)

    # Draw masses with strength indicator and particle numbers
    for mass in gravitational_field.masses:
        # Increase the size of particles based on powers of 10
        size = int(4 * math.ceil(math.log10(mass.mass + 1)))

        pygame.draw.circle(screen, BLUE, mass.rect.center, size)
        font = pygame.font.Font(None, size)
        text = font.render(str(mass.strength), True, WHITE)
        screen.blit(text, mass.rect.center)

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
