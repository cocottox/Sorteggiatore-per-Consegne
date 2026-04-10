# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 10:15:00 2026

@author: Matteo Senn
"""
# Una volta ho letto "Un buon gesto è come la musica, risuona meglio se condiviso"
# Che questo piccolo pezzo di logica possa aiutare il più possibile e adempiere a ciò
# per cui è stato scritto.

import tkinter as tk
from interfaccia import AppIndirizzi

if __name__ == "__main__":
    
    root = tk.Tk()
    
    app = AppIndirizzi(root)
    
    root.mainloop()