import pyquaternion as pyq
from QuatLibrary import euler_to_quaternion, newPosition, normalize
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import paho.mqtt.client as mqtt
import time

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
    acc_sens = 16384 / 16.4
    gyr_sens = 1
    return [
        np.array(list(map(lambda x: x / acc_sens, data_array[0:3]))), 
        np.array(list(map(lambda x: x / gyr_sens, data_array[3:6])))
        ]

def lines(file1, file2):
    return list(map(lambda line1, line2: 
            [
                separate_gyr_acc(read_array_from_line(line1)), 
                separate_gyr_acc(read_array_from_line(line2))
            ], 
        file1.readlines(), file2.readlines()))

def integrator(old_gyr_angle, new_gyr_angle, dt):
    return old_gyr_angle + new_gyr_angle * dt

def low_pass_filter(gyr_angle, acc_coord):
    return  0.98 * gyr_angle + 0.02 * acc_coord

def complementary_filter(old_gyr_angles, new_gyr_angles, acc_coords):
    dt = 0.02
    return list(map(lambda old_gyr_angle, new_gyr_angle, acc_coord: 
                        low_pass_filter(integrator(old_gyr_angle, new_gyr_angle, dt), acc_coord), 
                        old_gyr_angles, new_gyr_angles, acc_coords))

def double_complementary_filter(old_gyr_angles_1, gyr_angles_1, acc_coords_1, old_gyr_angles_2, gyr_angles_2, acc_coords_2):
    new_gyr_angles_1 = complementary_filter(old_gyr_angles_1, gyr_angles_1, acc_coords_1)
    new_gyr_angles_2 = complementary_filter(old_gyr_angles_2, gyr_angles_2, acc_coords_2)
    quat_1 = euler_to_quaternion(new_gyr_angles_1)
    quat_2 = euler_to_quaternion(new_gyr_angles_2)
    return [new_gyr_angles_1, new_gyr_angles_2, quat_1, quat_2]

def main(filename1, filename2):
    with open(filename1, 'r') as file1, open(filename2, 'r') as file2:
        old_gyr_angles_1 = np.array([0, 0, 0])
        old_gyr_angles_2 = np.array([0, 0, 0])
        pPulso = np.array([15,15,-15])
        pCotovelo = np.array([15,0,-15])
        pOmbro = np.array([15,0,0])
        pEsterno = np.array([0,0,0])

            #Seleciona o estilo darkgrid
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1,projection='3d') #Seleciona figura como 3d
        ax.set_xlabel("X") #Adiciona o nome dos eixos
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_xlim([-25,25]) #Adiciona o limite dos eixos
        ax.set_ylim([-25,25])
        ax.set_zlim([-25,25])
         #Seleciona o angulo de visão do plano 3d
        t = np.arange(0, 10, 10./280.)
        x = []
        y = []
        z = []
        axis = 1
        
        for [[acc_coords_1, new_gyr_angles_1], [acc_coords_2, new_gyr_angles_2]] in lines(file1, file2):
            [old_gyr_angles_1, old_gyr_angles_2, quat_1, quat_2] = double_complementary_filter(
                old_gyr_angles_1, new_gyr_angles_1, acc_coords_1, old_gyr_angles_2, new_gyr_angles_2, acc_coords_2)
            x.append(new_gyr_angles_2[axis])
            y.append(old_gyr_angles_2[axis])
            z.append(acc_coords_2[axis])
            final_1 = newPosition(pCotovelo, pPulso, quat_1, quat_2)
            ax.scatter(pCotovelo[0],pCotovelo[1],pCotovelo[2],color='red')
            ax.scatter(pOmbro[0],pOmbro[1],pOmbro[2],color='blue')
            point_1 = ax.scatter(final_1[0],final_1[1],final_1[2],color='yellow')
            ax.plot([final_1[0],pCotovelo[0]],[final_1[1],pCotovelo[1]],[final_1[2],pCotovelo[2]],color='black')
            ax.plot([pOmbro[0],pCotovelo[0]],[pOmbro[1],pCotovelo[1]],[pOmbro[2],pCotovelo[2]],color='black')
            ax.plot([pOmbro[0],pEsterno[0]],[pOmbro[1],pEsterno[1]],[pOmbro[2],pEsterno[2]],color='black')            
            plt.pause(0.035)
            point_1.remove()
            ax.lines[0].remove()
    
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
    main('parado_10s (1).txt', 'mexendo_2x_10s.txt')