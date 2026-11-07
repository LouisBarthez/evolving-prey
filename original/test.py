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

def mechant():
    # Côté droit : boules rebondissant de haut en bas
    for _ in range(50):
        x = WIDTH - circle_diameter // 2  # Position collée au bord droit
        y = random.randint(circle_diameter // 2, HEIGHT - circle_diameter // 2)
        dx = 0  # Pas de mouvement horizontal
        dy = random.choice([-5, 5])  # Mouvement vertical
        circle = MovingCircle(canvas, x, y, circle_diameter, 'red', dx, dy, void, void)
        circles.append(circle)

    # Côté gauche : boules rebondissant de haut en bas
    for _ in range(50):
        x = circle_diameter // 2  # Position collée au bord gauche
        y = random.randint(circle_diameter // 2, HEIGHT - circle_diameter // 2)
        dx = 0  # Pas de mouvement horizontal
        dy = random.choice([-5, 5])  # Mouvement vertical
        circle = MovingCircle(canvas, x, y, circle_diameter, 'red', dx, dy, void, void)
        circles.append(circle)

    # Côté haut : boules rebondissant de gauche à droite
    for _ in range(50):
        x = random.randint(circle_diameter // 2, WIDTH - circle_diameter // 2)
        y = circle_diameter // 2  # Position collée au bord haut
        dx = random.choice([-5, 5])  # Mouvement horizontal
        dy = 0  # Pas de mouvement vertical
        circle = MovingCircle(canvas, x, y, circle_diameter, 'red', dx, dy, void, void)
        circles.append(circle)

    # Côté bas : boules rebondissant de gauche à droite
    for _ in range(50):
        x = random.randint(circle_diameter // 2, WIDTH - circle_diameter // 2)
        y = HEIGHT - circle_diameter // 2  # Position collée au bord bas
        dx = random.choice([-5, 5])  # Mouvement horizontal
        dy = 0  # Pas de mouvement vertical
        circle = MovingCircle(canvas, x, y, circle_diameter, 'red', dx, dy, void, void)
        circles.append(circle)


mechant()

proies = []
nbproie = 10

def createdicdic(nbproie):
    dicdic = {}
    for i in range(nbproie):
        dicdic[f"dict_{i}"] = {
                "taille" : random.randint(5,50),
                "vitesse" : random.randint(1, 10), 
            }
    return dicdic

dicdic = createdicdic(nbproie)


for i in range(nbproie): 
    taille = dicdic[f"dict_{i}"]["taille"]
    vitesse = dicdic[f"dict_{i}"]["vitesse"]
    sign = random.choice([-1, 1])
    angle = random.uniform(0, 2 * math.pi)
    dx = vitesse * math.cos(angle) * sign
    dy = vitesse * math.sin(angle) * sign
    proie = MovingCircle(canvas, 400, 300, taille, 'blue', dx, dy, dicdic[f"dict_{i}"], void)
    proie.afficher()
    proies.append(proie)


# Variable globale pour stocker l'identifiant du texte de pause
pause_text_id = None

def m_taille(liste):
    m = 0
    for elem in liste:
        m = m + elem.diameter
    m = m / len(liste)
    return m


def m_vitesse(liste):
    m = 0
    for elem in liste:
        m = m + math.sqrt(elem.dx ** 2 + elem.dy ** 2)
    m = m / len(liste)
    return m

def m_taillec(liste):
    m = 0
    c = 0
    for elem in liste:
        m = m + elem.dic["taille"] * elem.time ** 5
        c = c + elem.time ** 5
    m = m / c
    return m

def m_dxc(liste):
    m = 0
    c = 0
    for elem in liste:
        m = m + elem.dx * elem.time ** 5
        c = c + elem.time ** 5
    m = m / c
    return m

def m_dyc(liste):
    m = 0
    c = 0
    for elem in liste:
        m = m + elem.dy * elem.time ** 5
        c = c + elem.time ** 5
    m = m / c
    return m


classement = []
m_t =  0
m_v = 0
gen = 0

def update_circles(event=None):
    global update_circles_id, classement, proies
    start()
    for circle in circles:
        circle.move()
    for proie in proies:
        proie.afficher()
        proie.move()
    for circle in circles:
        for proie in proies:
            if math.sqrt((proie.x - circle.x) ** 2 + (proie.y - circle.y) ** 2) < (circle.diameter + proie.diameter) / 2:
                proie.cacher()
                proies.remove(proie)
                classement.append(proie)
                proie.time = elapsed()
                if not proies:
                    pause_simulation()
                    return 

    update_circles_id = root.after(5, update_circles)

def pause_simulation():
    global gen, pause_text_id, m_t, m_v, classement, proies

    stop()
    m_t = m_taille(classement) 
    m_v = m_vitesse(classement)
    gen += 1 

    pause_text_id = canvas.create_text(WIDTH / 2, HEIGHT / 2, text=f"Génération: {gen} \nTaille moyenne: {m_t} \nVitesse moyenne: {m_v} \nTemps: {elapsed()}", fill="white", font=("Helvetica", 24))

    # Arrête l'animation
    root.after_cancel(update_circles_id)

    # Lier la barre d'espace pour relancer la simulation
    root.bind("<space>", resume_simulation)

def resume_simulation(event=None):
    global pause_text_id, proies, classement, nbproie, gen, circles

    if pause_text_id is not None:
        canvas.delete(pause_text_id)
        pause_text_id = None
    
    for mechant in circles:
            print("oui")
            mechant.cacher()
            canvas.delete(mechant.circle_id)
    circles = []

    m_tc = m_taillec(classement)
    m_dx = m_dxc(classement)
    m_dy = m_dyc(classement)
    classement = []
    proies = []
    for i in range(nbproie):
        sign = random.choice([-1, 1])
        taille = m_tc +  random.expovariate(0.5 + gen / 50) * sign
        taille = max(taille, 5)
        dicdic[f"dict_{i}"]["taille"] = m_tc
        dx = m_dx  + random.expovariate(1 + gen/50)*sign
        dy = m_dy  + random.expovariate(1 + gen/50)*sign
        proie = MovingCircle(canvas, 400, 300, taille, 'blue', dx, dy, dicdic[f"dict_{i}"], void)
        proie.afficher()
        proies.append(proie)


    reset()
    start_animation()

def start_animation():
    global update_circles_id
    mechant()
    update_circles_id = root.after(1, update_circles)



start_animation()

root.mainloop()