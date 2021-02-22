# Developed by Letícia Marques Pinho Tiago
# Contact: leticia.marquespinho@gmail.com

import pyquaternion as pyq
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import csv


def euler_to_quaternion(euler):
    phi,omega,psi = euler

    phi_2 = phi/2
    omega_2 = omega/2
    psi_2 = psi/2

    cos_phi_2 = np.cos(phi_2)
    cos_omega_2 = np.cos(omega_2)
    cos_psi_2 = np.cos(psi_2)
    
    sen_phi_2 = np.sin(phi_2)
    sen_omega_2 = np.sin(omega_2)
    sen_psi_2 = np.sin(psi_2)
    
    qw = cos_phi_2*cos_omega_2*cos_psi_2 + sen_phi_2*sen_omega_2*sen_psi_2
    qx = sen_phi_2*cos_omega_2*cos_psi_2 - cos_phi_2*sen_omega_2*sen_psi_2
    qy = cos_phi_2*sen_omega_2*cos_psi_2 + sen_phi_2*cos_omega_2*sen_psi_2
    qz = cos_phi_2*cos_omega_2*sen_psi_2 - sen_phi_2*sen_omega_2*cos_psi_2
    
    return [qw, qx, qy, qz]

def rotQuat(quat):
    w,x,y,z = normalize(quat)
    #print(w,x,y,z)

    R = np.array([[ 1 - 2*y*y - 2*z*z,  2*x*y + 2*w*z,      2*x*z - 2*w*y],
                  [ 2*x*y - 2*w*z,      1 - 2*x*x - 2*z*z,  2*y*z + 2*w*z],
                  [ 2*x*z + 2*w*y,      2*y*z - 2*w*x,      1 - 2*x*x - 2*y*y]])
    return R

def normalize(quat):
    w,x,y,z = quat
    norm = np.sqrt(w*w + x*x + y*y + z*z)
    return np.array(list(map(lambda x: x/norm, quat)))

def quaternion_to_euler(qd):
    phi   = math.atan2( 2 * (qd.w * qd.x + qd.y * qd.z), 1 - 2 * (qd.x**2 + qd.y**2) )
    theta = math.asin ( 2 * (qd.w * qd.y - qd.z * qd.x) )
    psi   = math.atan2( 2 * (qd.w * qd.z + qd.x * qd.y), 1 - 2 * (qd.y**2 + qd.z**2) )
    return np.array([phi,theta,psi])

def newPosition(origin, pontomovel, q_upper, q_lower):
    
    q_upper_2 = pyq.Quaternion(q_upper)
    q_lower_1 = pyq.Quaternion(q_lower)
    qd = q_upper_2.conjugate * q_lower_1
    R = rotQuat(qd)
    final = np.dot(R, pontomovel - origin) + origin
    return final

def save(quat1,quat2):
    with open('quat_row.csv', 'a') as arquivo_csv:
        escrever = csv.writer(arquivo_csv, delimiter=',', lineterminator='\n')
        escrever.writerow([str(quat1),str(quat2)])
    return

def rowCount():
    with open('quat.csv', 'r') as arquivo_csv:
        ler = csv.reader(arquivo_csv, delimiter=',')
        row_count = sum(1 for row in ler)
    return row_count

def read():
    with open('quat.csv', 'r') as arquivo_csv:
        ler = csv.reader(arquivo_csv, delimiter=',')
        row = rowCount()
        print(row)
        arquivo = []
        
        print(arquivo)

        aux = 0
        for str in ler:
            str1 = str[0].replace(']','').replace('[','')
            str2 = str[1].replace(']','').replace('[','')
            
            a = str1.replace('"','').split(",")    
            b = str2.replace('"','').split(",")
            a = a[0].split(" ")
            b = b[0].split(" ")
            result_a = [A for A in a if A != ""]
            result_b = [B for B in b if B != ""]            
            
            result_a = [float(i) for i in result_a]
            result_b = [float(i) for i in result_b]
            arquivo.append([result_a,result_b])
                        
            aux = aux + 1         
        print(arquivo)    
        return arquivo


def main():
    
    sBraco = np.array([1.0, 0.0, 0.0, 0.0])
    sAntebraco = np.array([1.0, 0.0, 0.0, 0.0])

    pPulso = np.array([0,0,10])
    pCotovelo = np.array([28,0,10])
    pOmbro = np.array([62,0,10])
    pEsterno = np.array([78,0,10])


    fig = plt.figure()
    ax = fig.add_subplot(1,1,1,projection='3d')

    ax.set_xlim([-20,90])
    ax.set_ylim([-35,45])
    ax.set_zlim([-20, 60])
    ax.scatter(pOmbro[0],pOmbro[1],pOmbro[2],color='red')
    ax.scatter(pEsterno[0],pEsterno[1],pEsterno[2],color='blue')

    #quaternions = read()


    angle = 60
    for i in range(0,angle):
        angle_1 = -i
        angle_2 = i

        if(i < 10):
            angle_2 = i
        else:
            angle_2 = 10

        angle_euler1 = np.array([0,math.radians(-i),0])
        quat1 = euler_to_quaternion(angle_euler1)
        quat_1 = normalize(quat1)

        angle_euler2 = np.array([0,math.radians(angle_1),math.radians(angle_2)])
        quat2 = euler_to_quaternion(angle_euler2)
        quat_2 = normalize(quat2)

        #save(quat_1,quat_2)

        final_1 = newPosition(pOmbro, pCotovelo, sBraco, quat_1)
        final_2 = newPosition(pOmbro, pPulso, sBraco, quat_1)
        final_3 = newPosition(final_1, final_2, sAntebraco, quat_2)
        
        point_1 = ax.scatter(final_1[0],final_1[1],final_1[2],color='yellow')
        point_3 = ax.scatter(final_3[0],final_3[1],final_3[2],color='purple')

        ax.plot([final_1[0],pOmbro[0]],[final_1[1],pOmbro[1]],[final_1[2],pOmbro[2]],color='black')
        ax.plot([final_1[0],final_3[0]],[final_1[1],final_3[1]],[final_1[2],final_3[2]],color='black')



        ax.plot([pOmbro[0],pEsterno[0]],[pOmbro[1],pEsterno[1]],[pOmbro[2],pEsterno[2]],color='black')

        plt.pause(0.02)

        point_1.remove()
        point_3.remove()

        ax.lines[0].remove()
    
    
    
    plt.show()


   

if __name__ == '__main__':
    main()
