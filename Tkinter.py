import tkinter as tk
import numpy as np

root = tk.Tk()
root.configure(bg='#231F20')
f = open('parameters.txt', 'w+')

def onClick(limb):
    print(limb)
    aux = int(textbox[limb].get())    
    buttons[limb].configure(state= tk.DISABLED)
    f.write(buttons[limb]["text"]+':'+str(aux)+'\n')

def onQuit(root,f):
    f.close()
    root.quit()

antebraco = 0
braco = 0
tronco = 0
pescoco = 0
perna = 0
coxa = 0
quadril = 0

limbs = ['Antebraço', 'Braço', 'Tronco vertical', 'Tronco horizontal', 'Pescoço', 'Quadril', 'Perna', 'Coxa']
buttons = {}
textbox = {}
i=0
quitProgram = tk.Button(root, text = "Fechar", command = lambda:onQuit(root,f), bg = '#BB4430', fg = '#EFE6DD')
for limb in limbs:
    buttons[limb] = tk.Button(root, text = limb, command = lambda text = limb: onClick(text), width = 15, bg = '#F3DFA2', fg = '#231F20')
    textbox[limb] = tk.Entry(root, bg = '#7EBDC2', fg = 'black', width = 15)
    textbox[limb].grid(row = i, column = 0)
    buttons[limb].grid(row = i, column = 2)
    tk.Label(text = '', height = 2, bg = '#231F20').grid(row = i+1, column = 2)
    tk.Label(text = '', height = 2, bg = '#231F20').grid(row = i+1, column = 0)

    i=1+i
    
quitProgram.grid(row = i+1, column = 2)

root.mainloop()
f.close()
#Tamanho do antebraço, braço, tronco, pescoço, perna, quadril, e coxa