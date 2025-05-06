import tkinter as tk
from tkinter import ttk
from database import get_loglar

class KontrolApp:
    def __init__(self, parent):
        self.parent = parent
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        # Filtreleme alanı
        filter_frame = tk.Frame(self.parent)
        filter_frame.pack(pady=10, fill="x")
        
        tk.Label(filter_frame, text="Tablo Adı:").pack(side="left", padx=5)
        self.tablo_filter = ttk.Combobox(filter_frame, values=["Tümü", "numuneler", "malzemeler",  "demirbaslar"])
        self.tablo_filter.pack(side="left", padx=5)
        self.tablo_filter.current(0)
        
        tk.Label(filter_frame, text="İşlem Tipi:").pack(side="left", padx=5)
        self.islem_filter = ttk.Combobox(filter_frame, values=["Tümü", "EKLEME", "GÜNCELLEME", "SİLME"])
        self.islem_filter.pack(side="left", padx=5)
        self.islem_filter.current(0)
        
        filter_btn = tk.Button(filter_frame, text="Filtrele", command=self.refresh_table)
        filter_btn.pack(side="left", padx=10)

        # Treeview
        self.tree = ttk.Treeview(self.parent, 
                                columns=("ID", "Tablo", "Kayıt ID", "İşlem", "Detay", "Kullanıcı", "Tarih"),
                                show="headings")
        
        # Sütun başlıkları
        columns = [
            ("ID", "ID", 50),
            ("Tablo", "Tablo Adı", 100),
            ("Kayıt ID", "Kayıt ID", 80),
            ("İşlem", "İşlem Tipi", 100),
            ("Detay", "İşlem Detayı", 200),
            ("Kullanıcı", "Kullanıcı", 120),
            ("Tarih", "Tarih", 150)
        ]
        
        for col_id, col_text, width in columns:
            self.tree.heading(col_id, text=col_text)
            self.tree.column(col_id, width=width)
            
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Yenile butonu
        refresh_btn = tk.Button(self.parent, text="Yenile", command=self.refresh_table)
        refresh_btn.pack(pady=10)

    def refresh_table(self):
        """Tabloyu filtre kriterlerine göre yeniler"""
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        tablo_adi = self.tablo_filter.get()
        islem_tipi = self.islem_filter.get()
        
        loglar = get_loglar()
        
        for log in loglar:
            log_id, tablo, kayit_id, islem, detay, kullanici, tarih = log
            
            # Filtreleme
            if tablo_adi != "Tümü" and tablo != tablo_adi:
                continue
                
            if islem_tipi != "Tümü" and islem != islem_tipi:
                continue
                
            self.tree.insert("", "end", values=(log_id, tablo, kayit_id, islem, detay, kullanici, tarih))