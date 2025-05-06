# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
from database import create_tables
from tabs.numune_takip import NumuneTakipApp
from tabs.malzeme_takip import MalzemeTakipApp
from tabs.demirbas_takip import DemirbasTakipApp
from tabs.kontrol import KontrolApp
from assets import kardökmak1

# Veritabanı oluşturuluyor
create_tables()

def uygulamayi_baslat():
    giris_pencere.destroy()
    
    ana_pencere = tk.Tk()
    ana_pencere.title("Kardökmak Ar-Ge Takip Sistemi")
    
    sekmeler = ttk.Notebook(ana_pencere)
    
    # Numune Takip Sekmesi
    tab1 = ttk.Frame(sekmeler)
    sekmeler.add(tab1, text="Numune Takip")
    NumuneTakipApp(tab1)

    # Malzeme Takip Sekmesi
    tab2 = ttk.Frame(sekmeler)
    sekmeler.add(tab2, text="Malzeme Takip")
    MalzemeTakipApp(tab2)

    # Demirbaş takip sekmesi
    tab3 = ttk.Frame(sekmeler)
    sekmeler.add(tab3, text="Demirbaş Takip")
    DemirbasTakipApp(tab3)

    # Kontrol sekmesi
    tab4 = ttk.Frame(sekmeler)
    sekmeler.add(tab4, text="Kontrol")
    KontrolApp(tab4)
    
    sekmeler.pack(expand=1, fill="both")
    ana_pencere.mainloop()

# Giriş ekranı
giris_pencere = tk.Tk()
giris_pencere.title("Kardökmak Ar-Ge - Giriş")
giris_pencere.geometry("1281x484")  # Pencere boyutu eklendi

# Logo için global referans
logo_img = None

try:
    img = Image.open("assets/kardökmak1")
    #img = img.resize((300, 300))
    logo_img = ImageTk.PhotoImage(img)
    
    etiket = tk.Label(giris_pencere, image=logo_img)
    etiket.image = logo_img
    etiket.pack(pady=20)
    
    baslat_butonu = tk.Button(
        giris_pencere, 
        text="Uygulamayı Başlat", 
        command=uygulamayi_baslat,
        font=("Arial", 12),
        padx=20,
        pady=10,
        bg="#2c3e50",
        fg="white"
    )
    baslat_butonu.pack(pady=10)

except Exception as e:
    print(f"Logo yüklenirken hata oluştu: {e}")
    tk.Label(
        giris_pencere, 
        text="Kardökmak Ar-Ge Takip Sistemi", 
        font=("Arial", 16, "bold"),
        fg="#2c3e50"
    ).pack(pady=50)
    
    tk.Button(
        giris_pencere, 
        text="Uygulamayı Başlat", 
        command=uygulamayi_baslat,
        font=("Arial", 12),
        bg="#2c3e50",
        fg="white"
    ).pack()

giris_pencere.mainloop()