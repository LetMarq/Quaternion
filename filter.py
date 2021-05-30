import pyquaternion as pyq
from QuatLibrary import euler_to_quaternion, newPosition, normalize
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import paho.mqtt.client as mqtt
import time
import math

running = False
def on_connect(client, userdata, flags, rc):
    global running
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")
    running = True

def on_message(client, userdata, msg):
    return
    print(msg.topic+" "+str(msg.payload))

def read_array_from_line(line):
    return np.array(list(map(float, line.replace('[', '').replace(']', '').strip().split(','))))

def separate_gyr_acc(data_array):
    acc_sens = 16384
    gyr_sens = 131
    return [
        np.array(list(map(lambda x: x / acc_sens, data_array[0:3]))), 
        np.array(list(map(lambda x: x / gyr_sens, data_array[3:6])))
        ]


def lines(file1, file2): 
    return list(map(lambda line1, line2: 
            [
                separate_gyr_acc(read_array_from_line(line1)), #Chama a função para seperar e retorna os files
                separate_gyr_acc(read_array_from_line(line2))
            ], 
        file1.readlines(), file2.readlines()))

def accangles(AccData):
    [Ax,Ay,Az] = AccData 
    ro = np.arctan2(Ax, math.sqrt(Ay**2 + Az**2))   # Calcula os valores dos ângulos dos sensores do
    phi = np.arctan2(Ay, math.sqrt(Ax**2 + Az**2))  # acelerômetro
    tetha = np.arctan2(math.sqrt(Ax**2 + Ay**2), Az)
    return [ro,phi,tetha]

def integrator(old_gyr_angle, new_gyr_angle, dt): 
    return old_gyr_angle + new_gyr_angle * dt #Calcula a integral pelo valor novo e valor antigo * dt

def filters(gyr_angle, acc_coord): 
    return  0.98 * gyr_angle + 0.02 * acc_coord #Calcula os filtros HPF e LPF

def complementary_filter(old_gyr_angles, new_gyr_angles, acc_coords):
    dt = 10./386.
    return list(map(lambda old_gyr_angle, new_gyr_angle, acc_coord: 
                        filters(integrator(old_gyr_angle, new_gyr_angle, dt), acc_coord), 
                        old_gyr_angles, new_gyr_angles, acc_coords)) #Chama os filtros

def double_complementary_filter(old_angles_1, gyr_angles_1, acc_coords_1, old_angles_2, gyr_angles_2, acc_coords_2):
    new_angles_1 = complementary_filter(old_angles_1, gyr_angles_1, acc_coords_1)
    new_angles_2 = complementary_filter(old_angles_2, gyr_angles_2, acc_coords_2)
    # print('Angle parado:',new_angles_1, 'Angle movimento:', new_angles_2)
    quat_1 = euler_to_quaternion(new_angles_1)
    quat_2 = euler_to_quaternion(new_angles_2)
    return [new_angles_1, new_angles_2, quat_1, quat_2]

def rotation_matrix(angles):
    [roll, pitch, yaw] = angles
    sin_roll = math.sin(roll)
    sin_pitch = math.sin(pitch)
    sin_yaw = math.sin(yaw)

    cos_roll = math.cos(roll)
    cos_pitch = math.cos(pitch)
    cos_yaw = math.cos(yaw)

    matrix = np.array([[cos_yaw*cos_pitch,  cos_yaw*sin_pitch*sin_roll - sin_yaw*cos_roll,  cos_yaw*sin_pitch*cos_roll + sin_yaw*cos_roll],
                       [sin_yaw*cos_pitch,  sin_yaw*sin_pitch*sin_roll + cos_yaw*cos_roll,  sin_yaw*sin_pitch*cos_roll - cos_yaw*cos_roll],
                       [-sin_pitch,         cos_pitch*sin_roll,                             cos_pitch*cos_roll                           ]])
    return matrix

def movement(angles, origin, move_point):
    R = rotation_matrix(angles)
    final = np.dot(R, move_point - origin) + origin

    return final



def main(filename1, filename2):
    with open(filename1, 'r') as file1, open(filename2, 'r') as file2:
        old_angles_1 = False
        old_angles_2 = False
        pPulso = np.array([15,15,-15])
        pCotovelo = np.array([15,0,-15])
        pOmbro = np.array([15,0,0])
        pEsterno = np.array([0,0,0])

    
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1,projection='3d') #Seleciona figura como 3d
        ax.set_xlabel("X") #Adiciona o nome dos eixos
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_xlim([-25,25]) #Adiciona o limite dos eixos
        ax.set_ylim([-25,25])
        ax.set_zlim([-25,25])
         #Seleciona o angulo de visão do plano 3d
        t = np.arange(0, 10, 10./910.)
        x = []
        y = []
        z = []
        axis = 2
        
        for [[file_acc_coords_1, file_gyr_angles_1], [file_acc_coords_2, file_gyr_angles_2]] in lines(file1, file2):
            if not old_angles_1 or not old_angles_2:
                old_angles_1 = file_gyr_angles_1
                old_angles_2 = file_gyr_angles_2
                pass
            [old_angles_1, old_angles_2, quat_1, quat_2] = double_complementary_filter(
                old_angles_1, file_gyr_angles_1, file_acc_coords_1, old_angles_2, file_gyr_angles_2, file_acc_coords_2)
                
            x.append(file_gyr_angles_1[axis])
            y.append(old_angles_1[axis])
            z.append(file_acc_coords_1[axis])
            new_point = movement(old_angles_1, pCotovelo, pPulso)
            ax.scatter(pCotovelo[0],pCotovelo[1],pCotovelo[2],color='red')
            ax.scatter(pOmbro[0],pOmbro[1],pOmbro[2],color='blue')
            point_1 = ax.scatter(new_point[0],new_point[1],new_point[2],color='yellow')
            ax.plot([new_point[0],pCotovelo[0]],[new_point[1],pCotovelo[1]],[new_point[2],pCotovelo[2]],color='black')
            # ax.plot([pOmbro[0],pCotovelo[0]],[pOmbro[1],pCotovelo[1]],[pOmbro[2],pCotovelo[2]],color='black')
            # ax.plot([pOmbro[0],pEsterno[0]],[pOmbro[1],pEsterno[1]],[pOmbro[2],pEsterno[2]],color='black')            
            # plt.pause(0.035)
            # point_1.remove()
            # ax.lines[0].remove()
    
           #client = mqtt.Client()
           #client.on_connect = on_connect
           #client.on_message = on_message

           #client.connect("127.0.0.1")
           #np.set_printoptions(formatter={'float': lambda x: '{0:0.5f}'.format(x)})
           #points = np.array2string(np.concatenate([pOmbro, pCotovelo, final_1]), separator=',')
        
           #i=0.0
           #client.loop()
           #if running:
           #    client.publish('harpy/coordinates', f'{points}'.encode('utf8'))
        plt.plot(t, np.array(z), c = 'r')
        plt.plot(t, np.array(y), c = 'g')
        plt.plot(t, np.array(x), c = 'b')
        plt.show()

if __name__ == '__main__':
    main('parado_27_maio.txt', 'movendo_parabaixo_2x_27_maio.txt')