from sys import argv
import pygame
from pygame import Vector2 as Pos

def draw_arrow(
        surface: pygame.Surface,
        start: pygame.Vector2,
        end: pygame.Vector2,
        color: pygame.Color,
        body_width: int = 3,
        head_width: int = 12,
        head_height: int = 12,
    ):
    """Draw an arrow between start and end with the arrow head at the end.

    Args:
        surface (pygame.Surface): The surface to draw on
        start (pygame.Vector2): Start position
        end (pygame.Vector2): End position
        color (pygame.Color): Color of the arrow
        body_width (int, optional): Defaults to 2.
        head_width (int, optional): Defaults to 4.
        head_height (float, optional): Defaults to 2.
    """
    arrow = start - end
    angle = arrow.angle_to(pygame.Vector2(0, -1))
    body_length = arrow.length() - head_height

    # Create the triangle head around the origin
    head_verts = [
        pygame.Vector2(0, head_height / 2),  # Center
        pygame.Vector2(head_width / 2, -head_height / 2),  # Bottomright
        pygame.Vector2(-head_width / 2, -head_height / 2),  # Bottomleft
    ]
    # Rotate and translate the head into place
    translation = pygame.Vector2(0, arrow.length() - (head_height / 2)).rotate(-angle)
    for i in range(len(head_verts)):
        head_verts[i].rotate_ip(-angle)
        head_verts[i] += translation
        head_verts[i] += start

    pygame.draw.polygon(surface, color, head_verts)

    # Stop weird shapes when the arrow is shorter than arrow head
    if arrow.length() >= head_height:
        # Calculate the body rect, rotate and translate into place
        body_verts = [
            pygame.Vector2(-body_width / 2, body_length / 2),  # Topleft
            pygame.Vector2(body_width / 2, body_length / 2),  # Topright
            pygame.Vector2(body_width / 2, -body_length / 2),  # Bottomright
            pygame.Vector2(-body_width / 2, -body_length / 2),  # Bottomleft
        ]
        translation = pygame.Vector2(0, body_length / 2).rotate(-angle)
        for i in range(len(body_verts)):
            body_verts[i].rotate_ip(-angle)
            body_verts[i] += translation
            body_verts[i] += start

        pygame.draw.polygon(surface, color, body_verts)

pygame.init()
font = pygame.font.Font('freesansbold.ttf', 16)
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

SIZE = 20
MODE_POS = Pos(SIZE + 10, SIZE + 10)
mode = 'p'

class Place:
    pos: Pos
    name: str
    nameSurf: pygame.surface
    tokens: int
    def __init__(self, pos: Pos, name: str):
        self.name = name
        self.nameSurf = font.render(name, True, 'blue')
        self.tokens = 0
        self.pos = pos
    def setName(self, name: str):
        self.name = name
        self.nameSurf = font.render(name, True, 'blue')

class Transition:
    pos: Pos
    name: str
    nameSurf: pygame.surface
    pre: list[Place]
    post: list[Place]
    def __init__(self, pos: Pos, name: str):
        self.name = name
        self.nameSurf = font.render(name, True, 'blue')
        self.pre = []
        self.post = []
        self.pos = pos
    def setName(self, name: str):
        self.name = name
        self.nameSurf = font.render(name, True, 'blue')
    def isActive(self):
        return all(p.tokens > 0 for p in self.pre)
    def fire(self):
        if not self.isActive():
            return
        for p in self.pre:
            p.tokens -= 1
        for p in self.post:
            p.tokens += 1

def export(places: list[Place], transitions: list[Transition], filename: str):
    result = ''
    for p in places:
        result += f'{p.name},{p.tokens},{int(p.pos.x)},{int(p.pos.y)};'
    result += '\n'
    for t in transitions:
        result += f'{t.name},{int(t.pos.x)},{int(t.pos.y)},'
        result += '|'.join(str(places.index(p)) for p in t.pre)
        result += ','
        result += '|'.join(str(places.index(p)) for p in t.post)
        result += ';'
    with open(filename, 'w') as fh:
        fh.write(result)

def tRect(p: Pos):
    return (p.x - SIZE, p.y - SIZE, SIZE * 2, SIZE * 2)

arcStart: Place | Transition | None = None
places: list[Place] = []
transitions: list[Transition] = []

# file loading
if len(argv) == 2:
    with open(argv[1]) as fh:
        [placesStr, transitionsStr] = fh.readlines()
    for placeStr in placesStr.split(';')[:-1]:
        (name, tokens, x, y) = placeStr.split(',')
        p = Place(Pos(int(x),int(y)), name)
        p.tokens = int(tokens)
        places.append(p)
    for transitionStr in transitionsStr.split(';')[:-1]:
        (name, x, y, pre, post) = transitionStr.split(',')
        t = Transition(Pos(int(x),int(y)), name)
        t.pre = [places[int(pidx)] for pidx in pre.split('|')] if pre else []
        t.post = [places[int(pidx)] for pidx in post.split('|')] if post else []
        transitions.append(t)

while running:
    newPos = Pos(pygame.mouse.get_pos())
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_p:
                    mode = 'p'
                case pygame.K_t:
                    mode = 't'
                case pygame.K_a:
                    mode = 'a'
                    arcStart = None
                case pygame.K_i:
                    mode = 'i'
                case pygame.K_d:
                    mode = 'd'
                case pygame.K_s:
                    mode = 's'
                case pygame.K_n:
                    mode = 'n'
                case pygame.K_f:
                    mode = 'f'
                case pygame.K_w:
                    # Write to file
                    export(places, transitions, input("filename: "))
        if event.type == pygame.MOUSEBUTTONUP:
            canPlace = True
            selected: Transition | Place | None = None
            for o in places + transitions:
                if o.pos.distance_squared_to(newPos) < SIZE**2:
                    canPlace = False
                    selected = o
                    break
                if o.pos.distance_squared_to(newPos) < (SIZE * 2)**2:
                    canPlace = False
                    break
            
            match mode:
                case 't' | 'p' if selected:
                    if type(selected) == Place:
                        places.remove(selected)
                        for t in transitions:
                            if selected in t.pre:
                                t.pre.remove(selected)
                            if selected in t.post:
                                t.post.remove(selected)
                    else:
                        transitions.remove(selected)
                case 'p' if canPlace:
                    places.append(Place(newPos, "p" + str(len(places) + 1)))
                case 't' if canPlace:
                    transitions.append(Transition(newPos, "t" + str(len(transitions) + 1)))
                case 'a' if selected:
                    if arcStart and type(arcStart) != type(selected):
                        if type(selected) == Transition:
                            if arcStart in selected.pre:
                                selected.pre.remove(arcStart)
                            else:
                                selected.pre.append(arcStart)
                        else:
                            if selected in arcStart.post:
                                arcStart.post.remove(selected)
                            else:
                                arcStart.post.append(selected)
                        arcStart = None
                    else:
                        arcStart = selected
                case 'a':
                    arcStart = None
                case 'i' if selected and type(selected) == Place:
                    selected.tokens += 1
                case 'd' if selected and type(selected) == Place and selected.tokens > 0:
                    selected.tokens -= 1
                case 's' if selected and type(selected) == Place:
                    selected.tokens = int(input(f'set tokens for {selected.name}:'))
                case 'n' if selected:
                    selected.setName(input(f'set new name for {selected.name}:'))
                case 'f' if selected and type(selected) == Transition:
                    selected.fire()

    screen.fill("purple")

    # Display mode
    pygame.draw.rect(screen, 'black', (0, 0, 60, 60))
    match mode:
        case 'p':
            pygame.draw.circle(screen, 'white', MODE_POS, SIZE)
        case 't':
            pygame.draw.rect(screen, 'white', tRect(MODE_POS), SIZE)
        case 'a':
            draw_arrow(screen, Pos(10,50), Pos(50,10), 'white')

    # Display graph
    for t in transitions:
        pygame.draw.rect(screen, 'red' if t.isActive() else 'white', tRect(t.pos))
        screen.blit(t.nameSurf, t.pos + Pos(-t.nameSurf.get_width() // 2, SIZE + 3))
        for place in t.pre:
            draw_arrow(screen, place.pos, t.pos.move_towards(place.pos, SIZE), 'black')
        for place in t.post:
            draw_arrow(screen, t.pos.move_towards(place.pos, SIZE), place.pos.move_towards(t.pos, SIZE), 'black')
    
    for p in places:
        pygame.draw.circle(screen, 'white', p.pos, SIZE)
        screen.blit(p.nameSurf, p.pos + Pos(-p.nameSurf.get_width() // 2, SIZE + 3))
        if p.tokens > 0:
            nTokensStr = str(p.tokens)
            text = font.render(nTokensStr, True, 'black')
            screen.blit(text, p.pos - Pos(1 + 4 * len(nTokensStr), 8))

    # Display arrow
    if mode == 'a' and arcStart:
        draw_arrow(screen, arcStart.pos, newPos, 'red')

    pygame.display.update()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
