import tkinter as tk
import random
import math
import time

start_time = None
elapsed_time = 0

def start():
    global start_time
    if start_time is None:  # Démarre le chronomètre uniquement s'il n'est pas déjà en cours
        start_time = time.time()

def stop():
    global start_time, elapsed_time
    if start_time is not None:  # Arrête le chronomètre seulement s'il est en cours
        elapsed_time += time.time() - start_time
        start_time = None

def reset():
    global start_time, elapsed_time
    start_time = None
    elapsed_time = 0

def elapsed():
    if start_time is not None:
        return elapsed_time + (time.time() - start_time)
    return elapsed_time



class MovingCircle:
    def __init__(self, canvas, x, y, diameter, color, dx, dy, dic, time):
        self.canvas = canvas
        self.diameter = diameter
        self.color = color
        self.dx = dx
        self.dy = dy
        self.x = x
        self.y = y
        self.dic = dic
        self.time = time
        self.circle_id = canvas.create_oval(
            x - diameter // 2, y - diameter // 2,
            x + diameter // 2, y + diameter // 2,
            fill=color
        )
    
    def move(self):
        # Met à jour les coordonnées du cercle
        self.x += self.dx
        self.y += self.dy
        
        # Vérifie les collisions avec les bords de la fenêtre
        if self.x - self.diameter // 2 < 0 or self.x + self.diameter // 2 > WIDTH:
            self.dx = -self.dx
        if self.y - self.diameter // 2 < 0 or self.y + self.diameter // 2 > HEIGHT:
            self.dy = -self.dy
        
        # Déplace le cercle sur le canevas
        self.canvas.move(self.circle_id, self.dx, self.dy)

    def cacher(self):
        self.canvas.itemconfig(self.circle_id, state='hidden')

    def afficher(self):
        self.canvas.itemconfig(self.circle_id, state='normal')


# Création de la fenêtre principale
root = tk.Tk()
root.title('Cercles Mobiles avec Tkinter')

# Définir la taille de la fenêtre
WIDTH, HEIGHT = 800, 600
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='black')
canvas.pack()

# Créer une dizaine de cercles avec des positions, couleurs, et vitesses aléatoires
circles = []
circle_diameter = 20
void = {}


def mechant(nb):
    if nb != 0: 
        for mechant in circles:
            mechant.cacher()
            canvas.delete(mechant.circle_id)
        circles.clear()
        
    param = nb  # Le paramètre qui détermine quel type de mouvement générer

    if param == 1:  # Générer des boules qui partent du bord avec des directions aléatoires
        for _ in range(100):
            # Choisir aléatoirement un des 4 bords
            side = random.choice(['left', 'right', 'top', 'bottom'])
            if side == 'left':
                x, y = circle_diameter // 2, random.randint(circle_diameter // 2, HEIGHT - circle_diameter // 2)
                dx, dy = random.choice([1, -1]) * 5, random.choice([1, -1]) * 5
            elif side == 'right':
                x, y = WIDTH - circle_diameter // 2, random.randint(circle_diameter // 2, HEIGHT - circle_diameter // 2)
                dx, dy = random.choice([1, -1]) * 5, random.choice([1, -1]) * 5
            elif side == 'top':
                x, y = random.randint(circle_diameter // 2, WIDTH - circle_diameter // 2), circle_diameter // 2
                dx, dy = random.choice([1, -1]) * 5, random.choice([1, -1]) * 5
            elif side == 'bottom':
                x, y = random.randint(circle_diameter // 2, WIDTH - circle_diameter // 2), HEIGHT - circle_diameter // 2
                dx, dy = random.choice([1, -1]) * 5, random.choice([1, -1]) * 5

            circle = MovingCircle(canvas, x, y, circle_diameter, 'red', dx, dy, void, void)
            circles.append(circle)

    elif param == 2:  # Boules qui bougent le long des bords
        for _ in range(100):
            x = random.choice([circle_diameter // 2, WIDTH - circle_diameter // 2])
            y = random.choice([circle_diameter // 2, HEIGHT - circle_diameter // 2])
            if x == circle_diameter // 2 or x == WIDTH - circle_diameter // 2:
                dx = random.choice([-5, 5])
                dy = 0
            else:
                dx = 0
                dy = random.choice([-5, 5])

            circle = MovingCircle(canvas, x, y, circle_diameter, 'red', dx, dy, void, void)
            circles.append(circle)

    elif param == 3:  # Vague de boules de droite à gauche
        for _ in range(100):
            x = WIDTH - circle_diameter // 2
            y = random.randint(circle_diameter // 2, HEIGHT - circle_diameter // 2)
            dx = -5
            dy = 0
            circle = MovingCircle(canvas, x, y, circle_diameter, 'red', dx, dy, void, void)
            circles.append(circle)

    elif param == 4:  # Vague de boules de gauche à droite
        for _ in range(100):
            x = circle_diameter // 2
            y = random.randint(circle_diameter // 2, HEIGHT - circle_diameter // 2)
            dx = 5
            dy = 0
            circle = MovingCircle(canvas, x, y, circle_diameter, 'red', dx, dy, void, void)
            circles.append(circle)

    elif param == 5:  # Vague de boules de haut en bas
        for _ in range(100):
            x = random.randint(circle_diameter // 2, WIDTH - circle_diameter // 2)
            y = circle_diameter // 2
            dx = 0
            dy = 5
            circle = MovingCircle(canvas, x, y, circle_diameter, 'red', dx, dy, void, void)
            circles.append(circle)

    elif param == 6:  # Vague de boules de bas en haut
        for _ in range(100):
            x = random.randint(circle_diameter // 2, WIDTH - circle_diameter // 2)
            y = HEIGHT - circle_diameter // 2
            dx = 0
            dy = -5
            circle = MovingCircle(canvas, x, y, circle_diameter, 'red', dx, dy, void, void)
            circles.append(circle)

    elif param == 7:  # Attroupement de boules du coin gauche-bas au coin droit-haut
        for _ in range(100):
            x = circle_diameter // 2
            y = HEIGHT - circle_diameter // 2
            dx = 5
            dy = -5
            circle = MovingCircle(canvas, x, y, circle_diameter, 'red', dx, dy, void, void)
            circles.append(circle)

    elif param == 8:  # Boules en file indienne zigzagantes
        for _ in range(100):
            x = random.choice([circle_diameter // 2, WIDTH - circle_diameter // 2])
            y = random.randint(circle_diameter // 2, HEIGHT - circle_diameter // 2)
            dx = 5 if x == circle_diameter // 2 else -5
            dy = random.choice([-5, 5])
            circle = MovingCircle(canvas, x, y, circle_diameter, 'red', dx, dy, void, void)
            circles.append(circle)

    elif param == 9:  # Boules avec mouvement circulaire
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        radius = 200
        for i in range(100):
            angle = 2 * math.pi * i / 100
            x = center_x + int(radius * math.cos(angle))
            y = center_y + int(radius * math.sin(angle))
            dx = -5 * math.sin(angle)
            dy = 5 * math.cos(angle)
            circle = MovingCircle(canvas, x, y, circle_diameter, 'red', dx, dy, void, void)
            circles.append(circle)

mechant(9)

def update_circles(event=None):
    global update_circles_id
    start()
    for circle in circles:
        circle.move()
   
    update_circles_id = root.after(5, update_circles)


def start_animation():
    global update_circles_id
    update_circles_id = root.after(1, update_circles)



start_animation()




root.mainloop()