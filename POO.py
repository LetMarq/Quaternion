import pyquaternion as pyq
import math
import numpy as np
from QuatLibrary import euler_to_quaternion, newPosition, normalize, dictionary_from_file, normalized_convertion
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import paho.mqtt.client as mqtt
import time
import sys




class ParteDoCorpo:
    def __init__(self, nome, posicao):
        self.nome = nome
        self.posicao = posicao

class SimetriaCorporal:
    def __init__(self, nome, posicao_esq, posicao_dir, posicao_centro = None):
        self.esquerda = ParteDoCorpo(nome, posicao_esq)
        self.direita = ParteDoCorpo(nome, posicao_dir)
        self.centro = ParteDoCorpo(nome, posicao_centro)

class Body:
    def __init__(self, dicionario):
        esternoOmbro, ombroCotovelo, cotoveloPulso, esternoPescoco, esternoQuadril, quadrilLateral, quadrilJoelho, joelhoTornozelo = self.calculos_distancias(dicionario)
        self.pulsos = SimetriaCorporal('Pulso', np.array([0,0,-cotoveloPulso]), np.array([esternoOmbro,cotoveloPulso,-ombroCotovelo]))
        self.cotovelos = SimetriaCorporal('Cotovelo',np.array([0,0,-ombroCotovelo]), np.array([esternoOmbro,0,-ombroCotovelo]))
        self.ombros = SimetriaCorporal('Ombro', np.array([-esternoOmbro,0,0]), np.array([esternoOmbro,0,0]))
        self.esterno = ParteDoCorpo('Esterno', np.array([0,0,0]))
        self.cabeca = ParteDoCorpo('Cabeça',np.array([0,0,esternoPescoco]))
        self.quadris = SimetriaCorporal('Quadril', np.array([-quadrilLateral,0,-esternoQuadril]), np.array([quadrilLateral,0,-esternoQuadril]), np.array([0,0,-esternoQuadril]))
        self.joelhos = SimetriaCorporal('Joelho', np.array([-quadrilLateral,0,-quadrilJoelho]), np.array([quadrilLateral,0,-quadrilJoelho]))
        self.tornozelos = SimetriaCorporal('Tornozelo', np.array([-quadrilLateral,0,-joelhoTornozelo]), np.array([quadrilLateral,0,-joelhoTornozelo])) 
    
    def calculos_distancias(self, dicionario):
        esternoOmbro = int(dicionario["Tronco horizontal"])/2
        ombroCotovelo = esternoOmbro + int(dicionario["Braço"])
        cotoveloPulso = ombroCotovelo + int(dicionario["Antebraço"])
        esternoPescoco = int(dicionario["Pescoço"])
        esternoQuadril = int(dicionario["Tronco vertical"])
        quadrilLateral = int(dicionario["Quadril"])/2
        quadrilJoelho = esternoQuadril + int(dicionario["Coxa"])
        joelhoTornozelo = quadrilJoelho + int(dicionario["Perna"])
        return esternoOmbro, ombroCotovelo, cotoveloPulso, esternoPescoco, esternoQuadril, quadrilLateral, quadrilJoelho, joelhoTornozelo

class Animation():
    def __init__(self, window, file, angle):
        d = dictionary_from_file(file)
        self.angle = angle
        self.maxFrame = angle
        self.actualFrame = 0
        self.window = window
        self.esqueleto = Body(d)
        self.lastPts = None
        self.sBraco = np.array([1.0, 0.0, 0.0, 0.0])
        self.sAntebraco = np.array([1.0, 0.0, 0.0, 0.0])
        self.show_screen()
        self.plot_static_points()

    def show_screen(self):
        self.window.opts['distance'] = 400
        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-100, 0, 0)
        gx.setSize(x=200, y=200, z=0)
        gx.setSpacing(x=20, y=20, z=0)
        self.window.addItem(gx)
        gy = gl.GLGridItem()
        gy.rotate(90, 100, 0, 0)
        gy.translate(0, -100, 0)
        gy.setSize(x=200, y=200, z=0)
        gy.setSpacing(x=20, y=20, z=0)
        self.window.addItem(gy)
        gz = gl.GLGridItem()
        gz.translate(0, 0, -100)
        gz.setSize(x=200, y=200, z=200)
        gz.setSpacing(x=20, y=20, z=20)
        self.window.addItem(gz)
        self.window.show()

    def plot_static_points(self):
        for posicao in [
            self.esqueleto.pulsos.direita.posicao,
            # self.esqueleto.pulsos.esquerda.posicao,
            self.esqueleto.cotovelos.direita.posicao,
            # self.esqueleto.cotovelos.esquerda.posicao,
            self.esqueleto.ombros.direita.posicao,
            # self.esqueleto.ombros.esquerda.posicao,
            self.esqueleto.quadris.direita.posicao,
            # self.esqueleto.quadris.centro.posicao,
            # self.esqueleto.quadris.esquerda.posicao,
            self.esqueleto.joelhos.direita.posicao,
            # self.esqueleto.joelhos.esquerda.posicao,
            self.esqueleto.tornozelos.direita.posicao,
            # self.esqueleto.tornozelos.esquerda.posicao,
            self.esqueleto.esterno.posicao,
            self.esqueleto.cabeca.posicao]:
            plot_pts = gl.GLScatterPlotItem(pos = posicao, color = (1,1,1,1))
            self.window.addItem(plot_pts)

    def next_frame(self):
        if self.actualFrame > self.maxFrame:
            self.actualFrame = 0
            return

        angle_2 = self.actualFrame
        angle_3 = self.actualFrame if (self.actualFrame < 70) else 10

        quat_1 = normalized_convertion([0,0,0])
        quat_2 = normalized_convertion([0,0,math.radians(angle_2)])
        quat_3 = normalized_convertion([0,0,0])

        final_1 = newPosition(self.esqueleto.ombros.direita.posicao, self.esqueleto.cotovelos.direita.posicao, self.sBraco, quat_3) #Calcula os pontos em relação ao quat e o sensor de referêcia
        final_2 = newPosition(self.esqueleto.ombros.direita.posicao, self.esqueleto.pulsos.direita.posicao, self.sBraco, quat_2)
        final_3 = newPosition(final_1, final_2, self.sAntebraco, quat_2)        

        pts = np.array([final_3[0], final_3[1], final_3[2]])
        plot_pts = gl.GLScatterPlotItem(pos = pts, color = (1,1,1,1))

        if self.lastPts:
            self.window.removeItem(self.lastPts)

        self.window.addItem(plot_pts)

        self.lastPts = plot_pts
        self.actualFrame += 1
   
def main():
    app = QtGui.QApplication([])
    window = gl.GLViewWidget()
    frame = Animation(window = window, file = "parameters.txt", angle = 30)
    timer = QtCore.QTimer()
    timer.timeout.connect(frame.next_frame)
    timer.start(50)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

if __name__ == '__main__':
    main()