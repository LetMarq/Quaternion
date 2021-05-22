# Developed by Letícia Marques Pinho Tiago
# Contact: leticia.marquespinho@gmail.com

import pyquaternion as pyq
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import csv
from QuatLibrary import euler_to_quaternion, newPosition, normalize
import seaborn as sns
import paho.mqtt.client as mqtt
import time

running = False
# Usar o popen para abrir e matar o "mosquitto"
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global running
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")
    running = True

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    return
    print(msg.topic+" "+str(msg.payload))

def main():
    #Lê-se os dados .txt dos parâmetros adquiridos por meio da inferface GUI (Tkinter.py)
    f = open("parameters.txt", 'r')
    d = {}
    for line in f:
        parameters = line.split(':') 
        d[parameters[0]]= parameters[1].replace('\n', '') #Cria um dicionário dos parâmetros adquiridos
    print(d)
    f.close()
    
    #Cria os sensores em quaternions
    sBraco = np.array([1.0, 0.0, 0.0, 0.0])
    sAntebraco = np.array([1.0, 0.0, 0.0, 0.0])

    #Calculas as distâncias respectivas, em que o primeiro nome é a origem e o segundo nome o destino (ponto final)
    esternoOmbro = int(d["Tronco horizontal"])/2
    ombroCotovelo = esternoOmbro + int(d["Braço"])
    cotoveloPulso = ombroCotovelo + int(d["Antebraço"])
    esternoPescoco = int(d["Pescoço"])
    esternoQuadril = int(d["Tronco vertical"])
    quadrilLateral = int(d["Quadril"])/2
    quadrilJoelho = esternoQuadril + int(d["Coxa"])
    joelhoTornozelo = quadrilJoelho + int(d["Perna"])

    #Cria cada ponto em relação as distâncias adquiridas acima
    pPulso = np.array([esternoOmbro,cotoveloPulso,-ombroCotovelo])
    pCotovelo = np.array([esternoOmbro,0,-ombroCotovelo])
    pOmbro = np.array([esternoOmbro,0,0])
    pEsterno = np.array([0,0,0])
    pOmbroesq = np.array([-esternoOmbro,0,0])
    pCotoveloesq = np.array([0,0,-ombroCotovelo])
    pPulsoesq = np.array([0,0,-cotoveloPulso])
    pHead = np.array([0,0,esternoPescoco])
    pQuadril = np.array([0,0,-esternoQuadril])
    pQuadrilesq = np.array([-quadrilLateral,0,-esternoQuadril])
    pQuadrildir = np.array([quadrilLateral,0,-esternoQuadril])
    pJoelhoesq = np.array([-quadrilLateral,0,-quadrilJoelho])
    pJoelhodir = np.array([quadrilLateral,0,-quadrilJoelho])
    pTornozesq = np.array([-quadrilLateral,0,-joelhoTornozelo])
    pTornozdir = np.array([quadrilLateral,0,-joelhoTornozelo])
    
    #Seleciona o estilo darkgrid
    sns.set(style = "darkgrid")
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1,projection='3d') #Seleciona figura como 3d
    ax.set_xlabel("X") #Adiciona o nome dos eixos
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_xlim([-130,130]) #Adiciona o limite dos eixos
    ax.set_ylim([-130,130])
    ax.set_zlim([-130,130])
    ax.view_init(elev=10, azim=60) #Seleciona o angulo de visão do plano 3d

    #Plota os pontos fixos do corpo
    ax.scatter(pOmbro[0],pOmbro[1],pOmbro[2],color='red')
    ax.scatter(pEsterno[0],pEsterno[1],pEsterno[2],color='blue')
    ax.scatter(pOmbroesq[0],pOmbroesq[1],pOmbroesq[2],color='red')
    ax.scatter(pHead[0],pHead[1],pHead[2],color='green')
    ax.scatter(pQuadril[0],pQuadril[1],pQuadril[2],color='black')
    ax.scatter(pJoelhodir[0],pJoelhodir[1],pJoelhodir[2],color='black')
    ax.scatter(pJoelhoesq[0],pJoelhoesq[1],pJoelhoesq[2],color='black')
    ax.scatter(pTornozdir[0],pTornozdir[1],pTornozdir[2],color='black')
    ax.scatter(pTornozesq[0],pTornozesq[1],pTornozesq[2],color='black')
    ax.scatter(pQuadrildir[0],pQuadrildir[1],pQuadrildir[2],color='black')
    ax.scatter(pQuadrilesq[0],pQuadrilesq[1],pQuadrilesq[2],color='black')

    #quaternions = read()

    #Seleciona um angulo de parâmetro
    angle = 100
    a=0
    b=0
    for i in range(0,angle,1):        
        if(a <= 20 and b == 0):
            angle_2 = a
            a = a+1
            print(a)
            if(a == 20):
                b=1
        else:
            angle_2 = a
            a = a-1
            print(a)
            if(a == -10):
                b=0
        
        if(i < 70):
            angle_3 = i-10
        else:
            angle_3 = 10
        
        if(i < 5):
            angle_4 = i
        else:
            angle_4 = 5

        angle_euler1 = np.array([0,0,0]) #Cria os ângulos de euler, phi,omega,psi, respectivamente (em radianos) para o quaterionion 1 e coloca em um array
        quat1 = euler_to_quaternion(angle_euler1) #Transforma os angulos de euler em quaternions
        quat_1 = normalize(quat1) #Normaliza o valor do quaternion

        angle_euler2 = np.array([math.radians(angle_2),0,0])
        quat2 = euler_to_quaternion(angle_euler2)
        quat_2 = normalize(quat2)

        angle_euler3 = np.array([0,math.radians(-angle_3),0])
        quat3 = euler_to_quaternion(angle_euler3)
        quat_3 = normalize(quat3)

        angle_euler4 = np.array([0,math.radians(-angle_3),math.radians(angle_4)])
        quat4 = euler_to_quaternion(angle_euler4)
        quat_4 = normalize(quat4)


        #save(quat_1,quat_2)

        final_1 = newPosition(pOmbro, pCotovelo, sBraco, quat_1) #Calcula os pontos em relação ao quat e o sensor de referêcia
        final_2 = newPosition(pOmbro, pPulso, sBraco, quat_2)
        final_3 = newPosition(final_1, final_2, sAntebraco, quat_2)

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        client.connect("127.0.0.1")
        np.set_printoptions(formatter={'float': lambda x: '{0:0.5f}'.format(x)})
        points = np.array2string(final_3, separator=',')
        
        i=0.0
        client.loop()
        if running:
            client.publish('harpy/coordinates', f'{points}'.encode('utf8'))
            #time.sleep(0.5) 

        # final_4 = newPosition(pOmbroesq, pCotoveloesq, sBraco, quat_3) 
        # final_5 = newPosition(pOmbroesq, pPulsoesq, sBraco, quat_3)
        # final_6 = newPosition(final_4, final_5, sAntebraco, quat_4)
        
        #Plota os pontos que estão se movendo
        point_1 = ax.scatter(final_1[0],final_1[1],final_1[2],color='yellow') #Pega o ponto final_1 e salva e plota como point_1
        point_3 = ax.scatter(final_3[0],final_3[1],final_3[2],color='purple')
        # point_4 = ax.scatter(final_4[0],final_4[1],final_4[2],color='yellow')
        # point_6 = ax.scatter(final_6[0],final_6[1],final_6[2],color='purple')

        # print(point_3)

        #Cria um vetor entre o ponto e o outro, no caso ponto final 1 e ombro
        ax.plot([final_1[0],pOmbro[0]],[final_1[1],pOmbro[1]],[final_1[2],pOmbro[2]],color='black') 
        ax.plot([final_1[0],final_3[0]],[final_1[1],final_3[1]],[final_1[2],final_3[2]],color='black')

        # ax.plot([final_4[0],pOmbroesq[0]],[final_4[1],pOmbroesq[1]],[final_4[2],pOmbroesq[2]],color='black')
        # ax.plot([final_4[0],final_6[0]],[final_4[1],final_6[1]],[final_4[2],final_6[2]],color='black')

        #Pontos fixos:
        ax.plot([pOmbroesq[0],pEsterno[0]],[pOmbroesq[1],pEsterno[1]],[pOmbroesq[2],pEsterno[2]],color='black')
        ax.plot([pOmbro[0],pEsterno[0]],[pOmbro[1],pEsterno[1]],[pOmbro[2],pEsterno[2]],color='black')
        ax.plot([pHead[0],pEsterno[0]],[pHead[1],pEsterno[1]],[pHead[2],pEsterno[2]],color='black')
        ax.plot([pQuadril[0],pEsterno[0]],[pQuadril[1],pEsterno[1]],[pQuadril[2],pEsterno[2]],color='black')
        ax.plot([pQuadril[0],pQuadrildir[0]],[pQuadril[1],pQuadrildir[1]],[pQuadril[2],pQuadrildir[2]],color='black')
        ax.plot([pQuadril[0],pQuadrilesq[0]],[pQuadril[1],pQuadrilesq[1]],[pQuadril[2],pQuadrilesq[2]],color='black')
        ax.plot([pQuadrildir[0],pJoelhodir[0]],[pQuadrildir[1],pJoelhodir[1]],[pQuadrildir[2],pJoelhodir[2]],color='black')
        ax.plot([pQuadrilesq[0],pJoelhoesq[0]],[pQuadrilesq[1],pJoelhoesq[1]],[pQuadrilesq[2],pJoelhoesq[2]],color='black')
        ax.plot([pTornozdir[0],pJoelhodir[0]],[pTornozdir[1],pJoelhodir[1]],[pTornozdir[2],pJoelhodir[2]],color='black')
        ax.plot([pTornozesq[0],pJoelhoesq[0]],[pTornozesq[1],pJoelhoesq[1]],[pTornozesq[2],pJoelhoesq[2]],color='black')




        
        point_3.remove()
        # point_4.remove()
        # point_6.remove()


        ax.lines[0].remove()
        plt.pause(0.02)
    
    
    
    plt.show()


   

if __name__ == '__main__':
    main()
