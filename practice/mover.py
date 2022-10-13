from vector import vector
from PyQt5.QtGui import QColor
from random import randint
 
class Mover:
    def __init__(self, x=0.0, y=0.0, mass = 1.0):
        self.location = vector(x,y)
        self.velocity = vector()
        self.acceleration = vector() 
 
        # 질량
        self.mass = mass
         
        self.G = 1.0
 
        self.color = QColor(randint(0,255), randint(0,255), randint(0,255), 128)        
 
    def applyForce(self, force):        
        # 뉴턴 운동 2법칙 (F=MA or A = F/M)
        force/=vector(self.mass, self.mass)
        self.acceleration += force
