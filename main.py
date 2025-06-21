import numpy as np
import pygame

# Initialize Pygame
pygame.init()
# Set up the display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
# Set up the clock for frame rate control
clock = pygame.time.Clock()
# Set up colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# Set up the font
font = pygame.font.Font(None, 36)
# Main loop
running = True

factor = 1
frame_rate = 120*factor

dt = 1/frame_rate

class PHYS_HANDLER:
    def __init__(self):
        self.obj_list = []

    def add(self,element):
        self.obj_list.append(element)

    def remove(self,element):
        self.obj_list.remove(element)

    def update_all(self):
        for obj in self.obj_list:
            obj.update()
    
    def draw_all(self,surface,show_mass=False,show_collision_count=False):
        for obj in self.obj_list:
            obj.draw(surface,show_mass,show_collision_count)
    
    def handle_collision(self):
        n = len(self.obj_list)
        for i in range(n):
            for j in range(i+1,n):
                self.obj_list[i].collide(self.obj_list[j])

class phys_obj_2d:
    def __init__(self, pos, vel,mass,color=BLACK):
        self.pos = np.array(pos, dtype=np.float64)
        self.vel = np.array(vel, dtype=np.float64)
        self.mass=mass
        self.color=color

    def update(self):
        self.pos += self.vel*dt
        self.collide_wall()
    
    def draw(self, surface,show_mass=False):
        pygame.draw.circle(surface, self.color, self.pos.astype(int), 1)
        if(show_mass):
            text = font.render(str(self.mass), True, BLACK)
            text_rect = text.get_rect(center=self.pos.astype(int))
            surface.blit(text, text_rect)

    def collide_wall(self):
        if self.pos[0]<0:#no collision on right wall
            self.vel[0]*=-1
            self.collision_count+=1
        if self.pos[1]<0 or self.pos[1]>600:
            self.vel[1]*=-1
            self.collision_count+=1

class ball_2d(phys_obj_2d):
    def __init__(self,pos,vel,radius,mass,color=BLACK):
        phys_obj_2d.__init__(self,pos,vel,mass,color)
        self.radius = radius
        self.collision_count=0

    def draw(self,surface,show_mass=False,show_collision_count=False):
        pygame.draw.circle(surface, self.color, self.pos.astype(int), self.radius)
        if(show_mass):
            text = font.render(str(self.mass), True, BLACK)
            text_rect = text.get_rect(center=self.pos.astype(int))
            surface.blit(text, text_rect)
        if(show_collision_count):
            text = font.render(str(self.collision_count), True, BLACK)
            text_rect = text.get_rect(center=self.pos.astype(int))
            surface.blit(text, text_rect)

    def collides_with(self,other):
        if np.linalg.norm(self.pos-other.pos) < (self.radius+other.radius):
            return True
        else:
            return False
    
    def collide(self,other,coef=1):
        # if not self.collides_with(other):
        #     return
        
        # self.collision_count+=1
        # v_1, m_1 = self.vel, self.mass
        # v_2, m_2 = other.vel, other.mass
        # w_1 = (m_1 - m_2)*v_1/(m_1 + m_2) + 2*m_2*v_2/(m_1 + m_2)
        # w_2 = (m_2 - m_1)*v_2/(m_2 + m_1) + 2*m_1*v_1/(m_2 + m_1)
        
        # self.vel = coef*w_1
        # other.vel = coef*w_2
        if not self.collides_with(other):
            return
        self.collision_count+=1
        # Vector from other to self
        delta = self.pos - other.pos
        dist = np.linalg.norm(delta)
        if dist == 0:
            # Prevent division by zero
            return

        # Normalized direction
        n = delta / dist

        # Relative velocity
        rel_vel = self.vel - other.vel
        vel_along_n = np.dot(rel_vel, n)

        if vel_along_n > 0:
            # Balls are moving apart
            return

        # Calculate impulse scalar
        m1, m2 = self.mass, other.mass
        impulse = (-(1+coef) * vel_along_n) / (1/m1 + 1/m2)

        # Apply impulse to velocities
        self.vel += (impulse / m1) * n
        other.vel -= (impulse / m2) * n

        # Separate overlapping balls
        overlap = self.radius + other.radius - dist
        if overlap > 0:
            correction = n * (overlap / 2+ 1e-10)
            self.pos += correction
            other.pos -= correction



def rand_color():
    random = np.random.rand(3)*255
    r,g,b = random[0],random[1],random[2]
    return(r,g,b)

def spawn_random(n,handler):
    for _ in range(n): 
        pos = np.random.rand(2) * 400 + 100
        vel = 100 * (np.random.rand(2) - 0.5)
        radius = int(np.random.rand() * 20 + 10)
        mass = float(radius)*5
        handler.add(ball_2d(pos, vel, radius, mass, color=rand_color()))

def start_experiment(handler,mass_1,mass_2):
    pos_1 = np.array([100,400])
    vel_1 = np.array([0,0])
    radius_1 = np.sqrt(np.sqrt(mass_1))*5
    color_1 = (194, 89, 100)

    pos_2 = pos_1+np.array([100,0])
    vel_2 = np.array([-30*factor,0])
    radius_2 = np.sqrt(np.sqrt(mass_2))*5
    color_2 = (165, 227, 224)

    handler.add(ball_2d(pos_1,vel_1,radius_1,mass_1,color_1))
    handler.add(ball_2d(pos_2,vel_2,radius_2,mass_2,color_2))


def main():
    # Create a particle instance
    handler = PHYS_HANDLER()
    
    #spawn_random(10,handler)
    start_experiment(handler,1,100**1)

    # Main loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        handler.update_all()
        handler.handle_collision()



        # Fill the screen with white
        screen.fill((29, 28, 26))
        handler.draw_all(screen)

        text = font.render(str(handler.obj_list[0].collision_count), True, (238, 243, 246))
        text_rect = text.get_rect(center=(100,100))
        screen.blit(text, text_rect)

        # Update the display
        pygame.display.flip()
        # Cap the frame rate
        clock.tick(frame_rate)


if __name__ == "__main__":
    # Run the main loop
    main()