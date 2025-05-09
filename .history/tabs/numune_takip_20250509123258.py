# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
from fpdf import FPDF
import sys
import os
import glob
from tkinter import messagebox
from tkcalendar import DateEntry

from datetime import datetime
# Add parent directory to path to import database module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import veritabani_baglantisi, get_all_samples, add_sample, update_sample, delete_sample, search_samples,log_ekle
class NumuneTakipApp:

    def __init__(self, parent):
        self.parent = parent

        # Veritabanı bağlantısını başlat
        self.conn, self.cursor = veritabani_baglantisi()

        if self.conn is None:
            messagebox.showerror("Bağlantı Hatası", "Veritabanı bağlantısı kurulamadı.")
            return

        # Arayüzü oluştur
        self.create_widgets()

        # İlk tablo verilerini yükle
        self.refresh_table()


    def create_widgets(self):
        frame = tk.Frame(self.parent)
        frame.pack(pady=10)

        tk.Label(frame, text="Numune Kodu").grid(row=0, column=0)
        self.entry_kod = tk.Entry(frame)
        self.entry_kod.grid(row=0, column=1)
         
        tk.Label(frame, text="Proje Adı").grid(row=1, column=0)
        self.entry_proje_adi = tk.Entry(frame)
        self.entry_proje_adi.grid(row=1, column=1)

        tk.Label(frame, text="Numune Adı").grid(row=2, column=0)
        self.entry_ad = tk.Entry(frame)
        self.entry_ad.grid(row=2, column=1)

        tk.Label(frame, text="Bulunduğu Raf").grid(row=3, column=0)
        self.entry_raf = tk.Entry(frame)
        self.entry_raf.grid(row=3, column=1)

        tk.Label(frame, text="Miktar - Birim").grid(row=4, column=0)
        self.entry_miktar = tk.Entry(frame, width=10)
        self.entry_miktar.grid(row=4, column=1, sticky="w")

        self.combo_birim = ttk.Combobox(frame, values=["g", "kg", "ton", "adet", "L"], width=5)
        self.combo_birim.grid(row=4, column=1, sticky="e")
        self.combo_birim.current(0)

        tk.Label(frame, text="Geldiği Tarih").grid(row=5, column=0)
        self.entry_tarih = DateEntry(frame, date_pattern="dd.mm.yyyy", locale='tr_TR')  # Türkçe için locale
        self.entry_tarih.grid(row=5, column=1)

        tk.Label(frame, text="Geldiği Yer").grid(row=6, column=0)
        self.entry_yer = tk.Entry(frame)
        self.entry_yer.grid(row=6, column=1)

        tk.Label(frame, text="Kod/Ad Ara").grid(row=7, column=0)
        self.entry_ara = tk.Entry(frame)
        self.entry_ara.grid(row=7, column=1)

        btn_ara = tk.Button(frame, text="Ara", command=self.search_sample)
        btn_ara.grid(row=7, column=2)

        btn_frame = tk.Frame(self.parent)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Numune Ekle", command=self.add_sample).grid(row=0, column=0,padx=5)
        tk.Button(btn_frame, text="Numune Güncelle", command=self.update_sample).grid(row=0, column=1,padx=5)
        tk.Button(btn_frame, text="Numune Sil", command=self.delete_sample).grid(row=0, column=2,padx=5)
        tk.Button(btn_frame, text="PDF Yazdır", command=self.export_pdf).grid(row=0, column=3,padx=5)
        tk.Button(btn_frame, text="Tümünü PDF Yazdır", command=self.export_all_to_pdf).grid(row=0, column=4,padx=5)
        tk.Button(btn_frame, text="Tüm Numuneleri Listele", command=self.list_all_samples).grid(row=0, column=5,padx=5)
        tk.Button(btn_frame, text="Detay", command=self.detay_goster).grid(row=0, column=6,padx=5)

        column_defs = [
            ("Kod", 80),
            ("Proje Adı", 150),
            ("Ad", 120),
            ("Raf", 60),
            ("Miktar", 70),
            ("Birim", 60),
            ("Tarih", 100),
            ("Yer", 120)
        ]

        self.tree = ttk.Treeview(self.parent, columns=[col[0] for col in column_defs], show="headings")
        self.tree.pack(pady=7, fill="x")

        for col_name, width in column_defs:
            self.tree.heading(col_name, text=col_name)
            self.tree.column(col_name, width=width, anchor="w")  # anchor="w" sola hizalar

            # Treeview seçim olayı
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item[0])
            values = item['values']
            
            self.entry_kod.delete(0, tk.END)
            self.entry_kod.insert(0, values[0])

            self.entry_proje_adi.delete(0, tk.END)
            self.entry_proje_adi.insert(0, values[1])

            self.entry_ad.delete(0, tk.END)
            self.entry_ad.insert(0, values[2])

            self.entry_raf.delete(0, tk.END)
            self.entry_raf.insert(0, values[3])

            self.entry_miktar.delete(0, tk.END)
            self.entry_miktar.insert(0, values[4])

            self.combo_birim.set(values[5])

            self.entry_tarih.delete(0, tk.END)
            self.entry_tarih.insert(0, values[6])

            self.entry_yer.delete(0, tk.END)
            self.entry_yer.insert(0, values[7])

    def clear_entries(self):
        """Tüm giriş alanlarını temizler"""
        self.entry_kod.delete(0, tk.END)
        self.entry_proje_adi.delete(0, tk.END)
        self.entry_ad.delete(0, tk.END)
        self.entry_raf.delete(0, tk.END)
        self.entry_miktar.delete(0, tk.END)
        self.combo_birim.current(0)
        self.entry_tarih.delete(0, tk.END)
        self.entry_yer.delete(0, tk.END)

    def refresh_table(self):
        """Tabloyu veritabanındaki verilerle günceller"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            samples = get_all_samples()
            for sample in samples:
                self.tree.insert("", "end", values=sample)
        except Exception as e:
            messagebox.showerror("Hata", f"Veri yükleme hatası: {str(e)}")

    def format_date(self, event=None):
        date_str = self.entry_tarih.get()
        date_str = re.sub(r'[^0-9]', '', date_str)  # Keep only digits

        if len(date_str) == 8:  # Format as DD.MM.YYYY
            formatted_date = f"{date_str[:2]}.{date_str[2:4]}.{date_str[4:]}"
            self.entry_tarih.delete(0, tk.END)
            self.entry_tarih.insert(0, formatted_date)

    def add_sample(self):
        try:
            kod = self.entry_kod.get().strip()
            proje_adi=self.entry_proje_adi.get().strip()
            ad = self.entry_ad.get().strip()
            raf = self.entry_raf.get().strip()
            miktar = self.entry_miktar.get().strip().replace(',', '.')
            birim = self.combo_birim.get().strip()
            tarih = self.entry_tarih.get().strip()
            yer = self.entry_yer.get().strip()

            if not all([kod, proje_adi, ad, raf, miktar, birim, tarih, yer]):
                messagebox.showerror("Hata", "Lütfen tüm alanları doldurun!")
                return

            miktar = float(miktar)


            values = (kod, proje_adi, ad, raf, miktar, birim, tarih, yer)
            success, message = add_sample(values)  # Burada success ve message'ı yakalıyoruz

            if success:
                log_ekle("numuneler", kod, "EKLEME", f"Yeni numune eklendi: {kod}")
                self.refresh_table()
                self.clear_entries()
                messagebox.showinfo("Başarı", message)
            else:
                messagebox.showerror("Hata", message)  # Veritabanından gelen hata mesajını göster

        except ValueError:
            messagebox.showerror("Hata", "Miktar geçersiz, sayı giriniz!")
        except Exception as e:
            messagebox.showerror("Hata", f"Beklenmeyen hata: {str(e)}")

    def update_sample(self):
        try:
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showerror("Hata", "Lütfen bir numune seçin!")
                return

            # Mevcut kodu al
            kod = self.entry_kod.get().strip()
            proje_adi=self.entry_proje_adi.get().strip()
            ad = self.entry_ad.get().strip()
            raf = self.entry_raf.get().strip()
            miktar = self.entry_miktar.get().strip()
            birim = self.combo_birim.get().strip()
            tarih = self.entry_tarih.get().strip()
            yer = self.entry_yer.get().strip()

            if not all([kod, proje_adi, ad, raf, miktar, birim, tarih, yer]):
                messagebox.showerror("Hata", "Lütfen tüm alanları doldurun!")
                return

            miktar = float(miktar)

            
            values = (kod, proje_adi, ad, raf, miktar, birim, tarih, yer, kod)

            if update_sample(values):
                log_ekle("numuneler", kod, "GÜNCELLEME", f"Numune güncellendi: {kod}")
                self.refresh_table()
                self.clear_entries()
                messagebox.showinfo("Başarı", "Numune başarıyla güncellendi!")
            else:
                messagebox.showerror("Hata", "Numune güncellenemedi!")

        except ValueError:
            messagebox.showerror("Hata", "Miktar geçersiz, sayı giriniz!")
        except Exception as e:
            messagebox.showerror("Hata", f"Beklenmeyen hata: {str(e)}")

    def delete_sample(self):
        try:
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showerror("Hata", "Lütfen bir numune seçin!")
                return

            kod = self.tree.item(selected_item[0])['values'][0]

            if messagebox.askyesno("Onay", f"{kod} numaralı numuneyi silmek istediğinize emin misiniz?"):
                if delete_sample(kod):
                    log_ekle("numuneler", kod, "SİLME", f"Numune silindi: {kod}")
                    self.refresh_table()
                    messagebox.showinfo("Başarı", "Numune başarıyla silindi!")
                else:
                    messagebox.showerror("Hata", "Numune silinemedi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Silme işlemi sırasında hata: {str(e)}")


    def clear_entries(self):
        """Clear all input fields"""
        self.entry_kod.delete(0, tk.END)
        self.entry_proje_adi.delete(0,tk.END)
        self.entry_ad.delete(0, tk.END)
        self.entry_raf.delete(0, tk.END)
        self.entry_miktar.delete(0, tk.END)
        self.entry_tarih.delete(0, tk.END)
        self.entry_yer.delete(0, tk.END)
        self.combo_birim.current(0)

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if not hasattr(self, 'conn') or self.conn is None:
            self.conn = veritabani_baglantisi()  # Bağlantıyı yeniden oluştur

        try:
            if self.conn:  # Bağlantı var mı kontrolü
                cursor = self.conn.cursor()
                cursor.execute("SELECT kod, proje_adi, ad, raf, miktar, birim, geldiği_tarih, geldiği_yer FROM numuneler")
                samples = cursor.fetchall()

                for sample in samples:
                    self.tree.insert("", "end", values=sample)
            else:
                messagebox.showerror("Hata", "Veritabanı bağlantısı kurulamadı!")
        except Exception as e:
            messagebox.showerror("Hata", f"Veri yükleme hatası: {str(e)}")

    def search_sample(self):
        search_text = self.entry_ara.get().strip()

        if not search_text:
            messagebox.showerror("Hata", "Lütfen arama kriteri girin!")
            return

        try:
            results = search_samples(self.conn, search_text)

            for row in self.tree.get_children():
                self.tree.delete(row)

            if results:
                for row in results:
                    self.tree.insert("", tk.END, values=row)
            else:
                messagebox.showinfo("Bilgi", "Aranan kriterlere uygun numune bulunamadı!")

        except Exception as e:
            messagebox.showerror("Hata", f"Arama sırasında hata oluştu:\n{e}")

    def export_pdf(self):
        
    #"""Seçili numuneleri PDF olarak kaydeder"""
        selected_items = self.tree.selection()  # Sadece seçili satırları al
        rows = [self.tree.item(item)["values"] for item in selected_items]

        if not rows:
            messagebox.showwarning("Uyarı", "PDF oluşturmak için bir satır seçmelisiniz!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Dosyası", "*.pdf")],
            title="PDF Olarak Kaydet"
        )
        if not file_path:
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", style='B', size=16)
        pdf.cell(w=0, h=10, txt="Numune Listesi", ln=True, align='C')
        pdf.ln(10)

        headers = ["Kod","Proje Adi", "Ad", "Raf", "Miktar", "Birim", "Tarih", "Yer"]
        column_widths = [30, 35, 35, 15, 15, 10, 20, 30]
        pdf.set_font("Arial", size=10)
        # Başlık satırı
        for i in range(len(headers)):
            pdf.cell(column_widths[i], 10, headers[i], border=1, align='C')
        pdf.ln()

        # Seçilen satırları yaz
        for row in rows:
            for i in range(len(headers)):
                pdf.cell(column_widths[i], 10, str(row[i]), border=1, align='C')
            pdf.ln()

        pdf.output(file_path)
        messagebox.showinfo("Başarı", f"PDF başarıyla kaydedildi:\n{file_path}")


    def export_all_to_pdf(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not file_path:
            return

        # Eğer get_all_samples fonksiyonu parametre almıyorsa bu satırı değiştirin
        samples = get_all_samples()  # Veya get_all_samples(self.conn) değilse
        if not samples:
            messagebox.showinfo("Bilgi", "Veritabanında kayıtlı numune bulunamadı!")
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", style='B', size=20)
        pdf.cell(w=0, h=10, txt="Numune Listesi", ln=True, align='C')
        pdf.ln(10)
        
        headers = ["Kod","Proje Adi", "Ad", "Raf", "Miktar", "Birim", "Tarih", "Yer"]
        column_widths = [30, 35, 35, 15, 15, 10, 20, 30]

        pdf.set_font("Arial", style='B',size=12)
        for i in range(len(headers)):
            pdf.cell(column_widths[i], 10, headers[i], border=1, align='C')
        pdf.ln()
        pdf.set_font("Arial", size=10)
        for row in samples:
            for i in range(len(row)):
                pdf.cell(column_widths[i], 10, str(row[i]), border=1, align='C')
            pdf.ln()

        pdf.output(file_path)
        messagebox.showinfo("Başarı", f"PDF başarıyla kaydedildi: {file_path}")

    def list_all_samples(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        samples = get_all_samples()
        if samples:
            for sample in samples:
                self.tree.insert("", tk.END, values=sample)
        else:
            messagebox.showinfo("Bilgi", "Veritabanında numune bulunamadı!")

    def detay_goster(self):
        DOSYA_KLASORU = r"C:\Users\aciog\Desktop\proje" 
        # Y:\Uniteler\ARGE\Ar-Ge Envanter Takip Sistemi\Numuneler"
        secilen = self.tree.focus()
        if not secilen:
            messagebox.showwarning("Uyarı", "Lütfen bir satır seçin.")
            return

        degerler = self.tree.item(secilen)["values"]
        kod = degerler[0]  # İlk sütun "Kod" ise

        arama_deseni = os.path.join(DOSYA_KLASORU, "**", f"{kod}.pdf")
        eslesen_dosyalar = glob.glob(arama_deseni, recursive=True)

        if eslesen_dosyalar:
            dosya_yolu = eslesen_dosyalar[0]
            klasor_yolu = os.path.dirname(dosya_yolu)
            os.startfile(klasor_yolu)
        else:
            messagebox.showerror("Hata", f"{kod}.pdf dosyası bulunamadı!")
