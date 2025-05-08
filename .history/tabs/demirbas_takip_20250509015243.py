# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from fpdf import FPDF
from tkcalendar import DateEntry
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import (veritabani_baglantisi, 
                     get_all_demirbaslar, 
                     add_demirbas, 
                     update_demirbas, 
                     delete_demirbas, 
                     search_demirbaslar)

class DemirbasTakipApp:
    def __init__(self, parent):
        self.parent = parent
        
        # Veritabanı bağlantısını başlat
        self.conn, self.cursor = veritabani_baglantisi()
        
        if self.conn is None or self.cursor is None:
            messagebox.showerror("Bağlantı Hatası", "Veritabanı bağlantısı kurulamadı.")
            return

        # Arayüzü oluştur
        self.create_widgets()
        
        # İlk tablo verilerini yükle
        self.refresh_table()

    def create_widgets(self):
        frame = tk.Frame(self.parent)
        frame.pack(pady=10)

        # Demirbaş Bilgileri
        tk.Label(frame, text="Demirbaş Kodu").grid(row=0, column=0)
        self.entry_no = tk.Entry(frame)
        self.entry_no.grid(row=0, column=1)

        tk.Label(frame, text="Demirbaş Adı").grid(row=1, column=0)
        self.entry_ad = tk.Entry(frame)
        self.entry_ad.grid(row=1, column=1)

        tk.Label(frame, text="Marka").grid(row=2, column=0)
        self.entry_marka = tk.Entry(frame)
        self.entry_marka.grid(row=2, column=1)

        tk.Label(frame, text="Alım Tarihi").grid(row=3, column=0)
        self.entry_alim_tarihi = DateEntry(frame, date_pattern="dd.mm.yyyy", locale='tr_TR')  # Türkçe için locales
        self.entry_alim_tarihi.grid(row=3, column=1)

        tk.Label(frame, text="Durum").grid(row=4, column=0)
        self.combo_durum = ttk.Combobox(frame, values=["Aktif", "Pasif", "Arızalı", "Hurda"], width=15)
        self.combo_durum.grid(row=4, column=1)
        self.combo_durum.current(0)

        # Arama Alanı
        tk.Label(frame, text="Arama (Kod/Ad/Marka)").grid(row=5, column=0)
        self.entry_arama = tk.Entry(frame)
        self.entry_arama.grid(row=5, column=1)
        
        btn_ara = tk.Button(frame, text="Ara", command=self.search_demirbas)
        btn_ara.grid(row=5, column=2)

        # Butonlar
        btn_frame = tk.Frame(self.parent)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Demirbaş Ekle", command=self.add_demirbas).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Güncelle", command=self.update_demirbas).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Sil", command=self.delete_demirbas).grid(row=0, column=2, padx=5)
        
        tk.Button(btn_frame, text="PDF Oluştur", command=self.export_pdf).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Tümünü PDF Yazdır", command=self.export_all_to_pdf).grid(row=0, column=4,padx=5)
        tk.Button(btn_frame, text="Tümünü Listele", command=self.list_all_demirbaslar).grid(row=0, column=5, padx=5)
        tk.Button(btn_frame, text="Detay", command=self.detay_goster).grid(row=0, column=6,padx=5)

        # Treeview
        self.tree = ttk.Treeview(self.parent, 
                                columns=("Kod", "Ad", "Marka", "Alım Tarihi", "Durum"),
                                show="headings")
        
        # Sütun başlıkları
        columns = [
            ("Kod", "Demirbaş Kod", 100),
            ("Ad", "Demirbaş Adı", 150),
            ("Marka", "Marka", 100),
            ("Alım Tarihi", "Alım Tarihi", 100), 
            ("Durum", "Durum", 80)
        ]
        
        for col_id, col_text, width in columns:
            self.tree.heading(col_id, text=col_text)
            self.tree.column(col_id, width=width)
            
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview seçim olayı
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item[0])
            values = item['values']
            
            # Seçili demirbaş bilgilerini form alanlarına doldur
            self.entry_no.delete(0, tk.END)
            self.entry_no.insert(0, values[0])
            
            self.entry_ad.delete(0, tk.END)
            self.entry_ad.insert(0, values[1])
            
            self.entry_marka.delete(0, tk.END)
            self.entry_marka.insert(0, values[2])
            
            self.entry_alim_tarihi.delete(0, tk.END)
            self.entry_alim_tarihi.insert(0, values[3])
            
            self.combo_durum.set(values[4])

    def clear_entries(self):
        """Tüm giriş alanlarını temizler"""
        self.entry_no.delete(0, tk.END)
        self.entry_ad.delete(0, tk.END)
        self.entry_marka.delete(0, tk.END)
        self.entry_alim_tarihi.delete(0, tk.END)
        self.combo_durum.current(0)

    def refresh_table(self):
        """Tabloyu veritabanındaki verilerle günceller"""
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        try:
            demirbaslar = get_all_demirbaslar()
            for demirbas in demirbaslar:
                self.tree.insert("", "end", values=demirbas)
        except Exception as e:
            messagebox.showerror("Hata", f"Veri yükleme hatası: {str(e)}")

    def add_demirbas(self):
        #"""Yeni demirbaş ekler"""
        # Form alanlarından verileri al
        demirbas_kod = self.entry_no.get().strip()
        ad = self.entry_ad.get().strip()
        marka = self.entry_marka.get().strip()
        alim_tarihi = self.entry_alim_tarihi.get().strip()
        durum = self.combo_durum.get().strip()

        # Zorunlu alan kontrolü
        if not all([ad, marka, alim_tarihi]):
            messagebox.showerror("Hata", "Lütfen zorunlu alanları doldurun!")
            return

        try:
            values = (demirbas_kod, ad, marka, alim_tarihi, durum)
            success, message = add_demirbas(values)  # Artık (başarı, mesaj) döndürüyor
            
            if success:
                self.refresh_table()
                self.clear_entries()
                messagebox.showinfo("Başarı", message)
            else:
                messagebox.showerror("Hata", message)
                
        except Exception as e:
            messagebox.showerror("Kritik Hata", f"Beklenmeyen sistem hatası: {str(e)}")

    def update_demirbas(self):
        """Demirbaş bilgilerini günceller"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Hata", "Lütfen güncellemek için bir demirbaş seçin!")
            return

        # Form alanlarından yeni verileri al
        demirbas_kod = self.entry_no.get().strip()
        ad = self.entry_ad.get().strip()
        marka = self.entry_marka.get().strip()
        alim_tarihi = self.entry_alim_tarihi.get().strip()
        durum = self.combo_durum.get().strip()

        # Zorunlu alan kontrolü
        if not all([demirbas_kod, ad, marka, alim_tarihi]):
            messagebox.showerror("Hata", "Lütfen zorunlu alanları doldurun!")
            return

        try:
            values = (demirbas_kod, ad, marka, alim_tarihi, durum,demirbas_kod)
            success = update_demirbas(values)
            
            if success:
                self.refresh_table()
                self.clear_entries()
                messagebox.showinfo("Başarı", "Demirbaş başarıyla güncellendi!")
            else:
                messagebox.showerror("Hata", "Demirbaş güncellenemedi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Demirbaş güncellenirken hata oluştu: {str(e)}")

    def delete_demirbas(self):
        """Demirbaş siler"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Hata", "Lütfen silmek için bir demirbaş seçin!")
            return

        demirbas_kod = self.tree.item(selected_item[0])['values'][0]
        
        cevap = messagebox.askyesno("Silme Onayı", 
                                   f"{demirbas_kod} numaralı demirbaşı silmek istediğinize emin misiniz?")
        if not cevap:
            return

        try:
            success = delete_demirbas(demirbas_kod)
            if success:
                self.refresh_table()
                self.clear_entries()
                messagebox.showinfo("Başarı", "Demirbaş başarıyla silindi!")
            else:
                messagebox.showerror("Hata", "Demirbaş silinemedi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Demirbaş silinirken hata oluştu: {str(e)}")

    def search_demirbas(self):
        """Demirbaş arama"""
        arama_metni = self.entry_arama.get().strip()
        
        if not arama_metni:
            messagebox.showerror("Hata", "Lütfen arama kriteri girin!")
            return

        try:
            results = search_demirbaslar(arama_metni)
            
            # Tabloyu temizle
            for row in self.tree.get_children():
                self.tree.delete(row)
                
            # Sonuçları ekle
            if results:
                for row in results:
                    self.tree.insert("", "end", values=row)
            else:
                messagebox.showinfo("Bilgi", "Arama kriterlerine uygun demirbaş bulunamadı!")
        except Exception as e:
            messagebox.showerror("Hata", f"Arama sırasında hata oluştu: {str(e)}")

    def list_all_demirbaslar(self):
        """Tüm demirbaşları listeler"""
        self.refresh_table()

    def export_pdf(self):
        """Seçili demirbaşları PDF olarak kaydeder"""
        selected_items = self.tree.selection()
        rows = [self.tree.item(item)["values"] for item in selected_items]
        if not selected_items:
            messagebox.showwarning("Uyarı", "PDF oluşturmak için en az bir demirbaş seçin!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="PDF Olarak Kaydet"
        )

        if not file_path:
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", style='B', size=16)
        pdf.cell(w=0, h=10, txt="Demirbas Listesi", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", size=10)
        # Sütun başlıkları
        headers = ["Kod", "Ad", "Marka", "Alim Tarihi", "Durum"]
        col_widths = [40, 40, 40, 40, 25]  # 5 sütun için
        pdf.set_font("Arial", size=10)
        # Başlık satırı
        for i in range(len(headers)):
            pdf.cell(col_widths[i], 10, headers[i], border=1, align='C')
        pdf.ln()

        # Seçili satırları yazdır
        for row in rows:
            for i in range(len(headers)):
                pdf.cell(col_widths[i], 10, str(row[i]), border=1, align='C')
            pdf.ln()

        pdf.output(file_path)
        messagebox.showinfo("Başarı", f"PDF başarıyla kaydedildi:\n{file_path}")


    def export_all_to_pdf(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not file_path:
            return

        samples = get_all_demirbaslar()
        if not samples:
            messagebox.showinfo("Bilgi", "Veritabanında kayıtlı demirbaş bulunamadı!")
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", style='B', size=16)
        pdf.cell(w=0, h=10, txt="Demirbas Listesi", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", size=10)
        headers = ["Kod", "Ad", "Marka", "Alim Tarihi", "Durum"]
        column_widths = [40, 40, 40, 40, 25]
        pdf.set_font("Arial", size=10)
        for i in range(len(headers)):
            pdf.cell(column_widths[i], 10, headers[i], border=1, align='C')
        pdf.ln()

        for row in samples:
            for i in range(len(row)):
                pdf.cell(column_widths[i], 10, str(row[i]), border=1, align='C')
            pdf.ln()

        pdf.output(file_path)
        messagebox.showinfo("Başarı", f"Tüm demirbaşlar PDF olarak kaydedildi: {file_path}")   

    def detay_goster(self):
        DOSYA_KLASORU = r"C:\Users\aciog\Desktop\proje"
        secilen = self.tree.focus()
        if not secilen:
            messagebox.showwarning("Uyarı", "Lütfen bir satır seçin.")
            return

        degerler = self.tree.item(secilen)["values"]
        kod = degerler[0]  # İlk sütun "Kod" ise

        dosya_yolu = os.path.join(DOSYA_KLASORU, f"{kod}.pdf")
        
        if os.path.exists(dosya_yolu):
            os.startfile(dosya_yolu)
        else:
            messagebox.showerror("Hata", f"{kod}.pdf dosyası bulunamadı!")

