# Developed by Letícia Marques Pinho Tiago
# Contact: leticia.marquespinho@gmail.com


import pyquaternion as pyq
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import csv


# def save(quat1,quat2):
#     with open('quat.csv', 'a') as arquivo_csv:
#         escrever = csv.writer(arquivo_csv, delimiter=',', lineterminator='\n')
#         escrever.writerow([str(quat1),str(quat2)])
#     return

def save(point_mao,point_cotovelo,point_ombro, point_esterno):
    with open('vector_row.csv', 'a') as arquivo_csv:
        escrever = csv.writer(arquivo_csv, delimiter=',', lineterminator='\n')
        escrever.writerow([str(point_mao),str(point_cotovelo),str(point_ombro),str(point_esterno)])
    return

def rowCount():
    with open('quat2.csv', 'r') as arquivo_csv:
        ler = csv.reader(arquivo_csv, delimiter=',')
        row_count = sum(1 for row in ler)
    return row_count

def read():
    with open('quat_row.csv', 'r') as arquivo_csv:
        ler = csv.reader(arquivo_csv, delimiter=',')
        row = rowCount()
        arquivo = []

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
        return arquivo

def newPosition(origin, pontomovel, q_upper, q_lower):
    
    q_upper_2 = pyq.Quaternion(q_upper)
    q_lower_1 = pyq.Quaternion(q_lower)
    qd = q_upper_2.conjugate * q_lower_1
    R = rotQuat(qd)
    final = np.dot(R, pontomovel - origin) + origin
    return final

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

    quaternions = read()

    for quaternion in quaternions:
 
        final_1 = newPosition(pOmbro, pCotovelo, sBraco, quaternion[0])
        final_2 = newPosition(pOmbro, pPulso, sBraco, quaternion[0])
        final_3 = newPosition(final_1, final_2, sAntebraco, quaternion[1])

        #print(quaternion[0],quaternion[1])
        
        point_1 = ax.scatter(final_1[0],final_1[1],final_1[2],color='yellow') #Cotovelo
        point_3 = ax.scatter(final_3[0],final_3[1],final_3[2],color='purple') #Mão  
        
        ax.plot([final_1[0],pOmbro[0]],[final_1[1],pOmbro[1]],[final_1[2],pOmbro[2]],color='black')
        ax.plot([final_1[0],final_3[0]],[final_1[1],final_3[1]],[final_1[2],final_3[2]],color='black')

        ax.plot([pOmbro[0],pEsterno[0]],[pOmbro[1],pEsterno[1]],[pOmbro[2],pEsterno[2]],color='black')

        #save(final_3,final_1,pOmbro,pEsterno)

        plt.pause(0.02)
        point_1.remove()
        point_3.remove()
        ax.lines[0].remove() 
    
    plt.show()


if __name__ == '__main__':
    main()