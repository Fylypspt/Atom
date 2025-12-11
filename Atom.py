import math
import random
import pygame as pg

class Vector:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
    def __mul__(self, s):
        return Vector(self.x * s, self.y * s, self.z * s)
    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    def normalize(self):
        l = self.length()
        if l==0: return Vector(0,0,0)
        return self*(1/l)

ELEMENTS = {"H":1,"He":2,"Li":3,"Be":4,"C":6,"N":7,"O":8}

class Nucleus:
    def __init__(self, pos, symbol):
        self.pos = pos
        self.symbol = symbol
        self.Z = ELEMENTS[symbol]
        self.electrons = []

class Electron:
    def __init__(self, nucleus, shell_index=1, orbital="s"):
        self.nucleus = nucleus
        self.shell = shell_index #níveis de energia
        self.orbital = orbital
        self.pos = Vector()
        self.trail = []

    def sample_radius(self, a0_pixels, shell_multiplier=1):
        a0 = a0_pixels * shell_multiplier #Bohr radius
        r_max = 5*a0 #if more than 5*a0, probability is negligible at a far distance
        proposal_scale = a0/2
        while True:
            r = -proposal_scale*math.log(random.random()) #Electron prob: Very high near nucleus, Drops fast with distance
            if r > r_max: continue
            accept_prob = (r/r_max)**2 #radial probability density function
            if random.random() < accept_prob: return r

    def sample_angle(self):
        theta = math.acos(random.uniform(-1,1)) #Prevents clustering near the poles, isso acontece pq sen(theta) é menor perto dos polos
        phi = random.uniform(0, 2*math.pi)
        return theta, phi

    def update(self, a0_pixels):
        r = self.sample_radius(a0_pixels, self.shell) #Get random distance from nucleus, Depends on shell number
        theta, phi = self.sample_angle() #Get random direction
        
        #Visual approximation of orbital shapes
        if self.orbital == "p": 
            theta += math.pi/2; phi += math.pi/8
        if self.orbital == "d": 
            theta += math.pi/4; phi += math.pi/4

        #Convert spherical to cartesian
        x = r*math.sin(theta)*math.cos(phi)
        y = r*math.sin(theta)*math.sin(phi)
        z = r*math.cos(theta)

        self.pos = Vector(self.nucleus.pos.x + x, self.nucleus.pos.y + y, z) #upd pos
        self.trail.append((self.pos.x, self.pos.y)) #We need to store the trail because we redraw everything each frame
        if len(self.trail) > 10: 
            self.trail.pop(0)

def electron_shells_for_Z(Z): #how many electrons go in each nivel
    shells = []
    remaining = Z
    capacities = [2, 8, 18] #max number of electrons per shell
    i = 0
    while remaining > 0: #until all electrons are placed
        cap = capacities[i] if i < len(capacities) else capacities[-1] #Gets shell capacity, repeats last if needed
        fill = min(cap, remaining) #How many electrons to place in this shell, can't exceed remaining
        shells.append(fill)
        remaining -= fill
        i += 1 #next shell
    return shells

def create_atom(symbol, pos):
    nucleus = Nucleus(pos, symbol)
    a0_pixels = 40.0 / max(1, ELEMENTS[symbol])
    shells = electron_shells_for_Z(ELEMENTS[symbol])
    electrons = []
    orbitals_sequence = ["s", "s", "p", "p", "p", "d", "d", "d"]
    for shell_index, count in enumerate(shells, start=1):
        for i in range(count):
            orbital = orbitals_sequence[i] if i < len(orbitals_sequence) else "s"
            electrons.append(Electron(nucleus, shell_index, orbital))
    nucleus.electrons = electrons
    return nucleus, electrons, a0_pixels

pg.init()
screen = pg.display.set_mode((1100, 700))
clock = pg.time.Clock()

nucleus, electrons, a0 = create_atom("H", Vector(550, 350))
nucleus2, electrons2, a02 = create_atom("C", Vector(700, 450))
nucleus3, electrons3, a03 = create_atom("O", Vector(400, 450))

running = True
while running:
    clock.tick(60)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    for el in electrons:
        el.update(a0)

    for el in electrons2:
        el.update(a02)

    for el in electrons3:
        el.update(a03)

    screen.fill((0, 0, 0))

    pg.draw.circle(screen, (255, 50, 50), (int(nucleus.pos.x), int(nucleus.pos.y)), 10) #atom
    pg.draw.circle(screen, (50, 255, 50), (int(nucleus2.pos.x), int(nucleus2.pos.y)), 10) #atom 2
    pg.draw.circle(screen, (50, 50, 255), (int(nucleus3.pos.x), int(nucleus3.pos.y)), 10) #atom 3

    font = pg.font.SysFont(None, 18) #element symbol

    txt = font.render(nucleus.symbol, True, (255, 255, 255))
    txt2 = font.render(nucleus2.symbol, True, (255, 255, 255))
    txt3 = font.render(nucleus3.symbol, True, (255, 255, 255))

    screen.blit(txt, (int(nucleus.pos.x) + 12, int(nucleus.pos.y) - 10)) # electrons and trails
    screen.blit(txt2, (int(nucleus2.pos.x) + 12, int(nucleus2.pos.y) - 10))
    screen.blit(txt3, (int(nucleus3.pos.x) + 12, int(nucleus3.pos.y) - 10))

    for el in electrons:
        for i, pos in enumerate(el.trail):
            alpha = max(30, 255 - i * 25)
            color = (alpha, alpha, alpha)
            pg.draw.circle(screen, color, (int(pos[0]), int(pos[1])), 2)

    for el in electrons2:
        for i, pos in enumerate(el.trail):
            alpha = max(30, 255 - i * 25)
            color = (alpha, alpha, alpha)
            pg.draw.circle(screen, color, (int(pos[0]), int(pos[1])), 2)

    for el in electrons3:
        for i, pos in enumerate(el.trail):
            alpha = max(30, 255 - i * 25)
            color = (alpha, alpha, alpha)
            pg.draw.circle(screen, color, (int(pos[0]), int(pos[1])), 2)

    pg.display.flip()

pg.quit()