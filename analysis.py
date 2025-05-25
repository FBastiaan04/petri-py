from sys import argv

class Place:
    name: str
    tokens: int
    def __init__(self, name: str, tokens: int):
        self.name = name
        self.tokens = tokens
    def fromStr(s: str):
        (name, tokens, _, _) = s.split(',')
        return Place(name, int(tokens))
    def __repr__(self):
        return self.name

class Transition:
    name: str
    pre: list[Place]
    post: list[Place]
    hasFired: bool
    def __init__(self, name: str, pre: list[Place], post: list[Place]):
        self.name = name
        self.pre = pre
        self.post = post
        self.hasFired = False

    def isActive(self):
        return all(p.tokens > 0 for p in self.pre)
    def fire(self):
        if not self.isActive():
            raise RuntimeError("Cannot fire: inactive")
        self.hasFired = True
        for p in self.pre:
            p.tokens -= 1
        for p in self.post:
            p.tokens += 1
    def unfire(self):
        for p in self.pre:
            p.tokens += 1
        for p in self.post:
            p.tokens -= 1

    def __repr__(self):
        return self.name

places: list[Place] = []
transitions: list[Transition] = []

# file loading
if len(argv) != 2:
    print(f"usage: {argv[0]} <filename>")
    exit(1)

with open(argv[1]) as fh:
    [placesStr, transitionsStr] = fh.readlines()

places = [Place.fromStr(placeStr) for placeStr in placesStr.split(';')[:-1]]
transitions = []
for transitionStr in transitionsStr.split(';')[:-1]:
    (name, _, _, preStr, postStr) = transitionStr.split(',')
    pre = [places[int(pidx)] for pidx in preStr.split('|')] if preStr else []
    post = [places[int(pidx)] for pidx in postStr.split('|')] if postStr else []
    transitions.append(Transition(name, pre, post))

def stateToStr():
    return "{" + ", ".join(p.name if p.tokens == 1 else f"{p.tokens} {p.name}" for p in places if p.tokens > 0) + "}"

def stateToDict(state: str):
    result: dict[str, int] = {}
    for tokens in state[1:-1].split(', '):
        if ' ' in tokens:
            n, name = tokens.split(' ')
            result[name] = int(n)
        else:
            result[tokens] = 1
    return result

def compare(current: str, previous: str):
    if current == previous:
        return 'recurs'
    current = stateToDict(current)
    previous = stateToDict(previous)

    if all(k in current and current[k] >= v for k, v in previous.items()):
        return 'unbounded'
    return None

idx = 0

prevList:list[tuple[int,str]] = []


def reachability(depth=0):
    if depth > 12:#DEBUG
        print("STOPPED")
        return

    global idx
    myIdx = idx
    idx += 1

    state = stateToStr()

    for prevIdx, prev in prevList:
        if (c := compare(state, prev)) == 'unbounded':
            print(f's{myIdx}["{state}"]')
            print(f's{myIdx} --> unbounded')
            return
        elif c == 'recurs':
            print('s'+str(prevIdx))
            return
    
    print(f's{myIdx}["{state}"]')
    prevList.append((myIdx, state))

    deadlock = True
    for t in transitions:
        #print('\t' * depth + t.name)
        if t.isActive():
            t.fire()
            deadlock = False
            
            #print("\t" * depth + state)
            print(f's{myIdx} --> ', end='')
            reachability(depth+1)
            t.unfire()
    if deadlock:
        print("Deadlocks")

reachability()

for t in transitions:
    if not t.hasFired:
        print(f'{t} is dead')
else:
    print('no deadlocks')
