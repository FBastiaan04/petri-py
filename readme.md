# ui:
upper left: current mode indicator (only for modes p, t and a so far)
white square: inactive transition
red square: active transition
circle: place with 0 tokens
circle with number n: place with n tokens
arrow: arc

# controls:
w: write to file

## modes:
p: Places
    click an empty spot to create a place. Click a place or transition to delete it.
t: Transitions
    click an empty spot to create a transition. Click a place or transition to delete it.
a: Arcs/Arrows
    click a place, then click a transition, or vice versa.
i: Increment tokens
    click a place to add a token
d: Decrement tokens
    click a place to remove a token
s: Set 
    click a place to enter a number of tokens in the terminal
n: Naming
    click a place or transition to enter a new name in the terminal
f: Firing
    click a transition to attempt to fire it.