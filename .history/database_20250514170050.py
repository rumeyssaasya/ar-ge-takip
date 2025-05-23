# database.py
from tkinter import ttk, messagebox, filedialog
import sqlite3

def veritabani_baglantisi():
    """Veritabanı bağlantısı oluşturur ve (conn, cursor) döndürür"""
    try:
        conn = sqlite3.connect('arge.db')
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None, None




def create_tables():
    """Tüm tabloları oluşturur veya varsa kontrol eder"""
    conn, cursor = veritabani_baglantisi()
    if conn is None or cursor is None:
        print("Tablo oluşturulamadı: Bağlantı hatası")
        return False

    try:
        # Numuneler tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS numuneler (
                kod TEXT,
                proje_adi TEXT,
                ad TEXT,
                raf TEXT,
                miktar REAL,
                birim TEXT,
                geldiği_tarih TEXT,
                geldiği_yer TEXT
            )
        ''')
        # Malzemeler tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS malzemeler (
                kod TEXT,
                ad TEXT,
                raf TEXT,
                miktar REAL,
                birim TEXT,
                alındığı_tarih TEXT,
                alındığı_firma TEXT
            )
                ''')

        # Demirbaşlar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS demirbaslar (
                demirbas_kod TEXT UNIQUE,
                ad TEXT,
                marka TEXT,
                alim_tarihi TEXT,
                durum TEXT
            )
        ''')

        #Kontrol tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kontrol_loglari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tablo_adi TEXT,
                kayit_id INTEGER,
                islem_tipi TEXT,
                islem_detay TEXT,
                kullanici TEXT,
                tarih TEXT
            )
        ''')

        conn.commit()
        return True
    except Exception as e:
        print(f"Tablo oluşturma hatası: {e}")
        return False
    finally:
        conn.close()

def log_ekle(tablo_adi, kayit_id, islem_tipi, islem_detay, kullanici="Sistem"):
    """Log kaydı ekler"""
    from datetime import datetime
    conn, cursor = veritabani_baglantisi()
    if conn is None or cursor is None:
        return False

    try:
        tarih = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        cursor.execute('''
            INSERT INTO kontrol_loglari 
            (tablo_adi, kayit_id, islem_tipi, islem_detay, kullanici, tarih)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tablo_adi, kayit_id, islem_tipi, islem_detay, kullanici, tarih))
        conn.commit()
        return True
    except Exception as e:
        print(f"Log ekleme hatası: {e}")
        return False
    finally:
        conn.close()

def get_loglar():
    """Tüm log kayıtlarını en güncel tarihten eskiye doğru getirir (dd.mm.yyyy hh:mm:ss görünümünü koruyarak)"""
    conn, cursor = veritabani_baglantisi()
    if conn is None or cursor is None:
        return []

    try:
        cursor.execute('''
            SELECT * FROM kontrol_loglari 
            ORDER BY 
                substr(tarih, 7, 4) || '-' || substr(tarih, 4, 2) || '-' || substr(tarih, 1, 2) || ' ' || substr(tarih, 12, 8) DESC
        ''')
        return cursor.fetchall()
    except Exception as e:
        print(f"Log getirme hatası: {e}")
        return []
    finally:
        conn.close()


def add_sample(values):
    """Yeni numune ekler"""
    conn, cursor = veritabani_baglantisi()
    if conn is None or cursor is None:
        return False, "Veritabanı bağlantı hatası"
    
    kod = values[0]
    
    try:
        # Önce kodun varlığını kontrol et
        cursor.execute("SELECT 1 FROM numuneler WHERE kod=?", (kod,))
        if cursor.fetchone():
            return False, f"'{kod}' kodu zaten kayıtlı!"
        
        # Yeni numuneyi ekle
        cursor.execute('''
            INSERT INTO numuneler (kod, proje_adi, ad, raf, miktar, birim, geldiği_tarih, geldiği_yer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', values)
        conn.commit()
        return True, f"'{kod}' kodlu numune başarıyla eklendi"
        
    except sqlite3.IntegrityError as e:
        error_msg = str(e)
        if "UNIQUE" in error_msg:
            return False, f"'{kod}' kodu zaten mevcut!"
        return False, f"Veritabanı hatası: {error_msg}"
        
    except Exception as e:
        return False, f"Sistem hatası: {str(e)}"
        
    finally:
        if conn:
            conn.close()

def update_sample(values):
    """Numune bilgilerini günceller"""
    conn, cursor = veritabani_baglantisi()
    if conn is None or cursor is None:
        return False

    try:
        cursor.execute('''
            UPDATE numuneler
            SET kod=?, proje_adi=?, ad=?, raf=?, miktar=?, birim=?, geldiği_tarih=?, geldiği_yer=?
            WHERE kod=?
        ''', values)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Güncelleme hatası: {e}")
        return False
    finally:
        conn.close()

def delete_sample(kod):
    """Numune siler"""
    conn, cursor = veritabani_baglantisi()
    if conn is None or cursor is None:
        return False

    try:
        cursor.execute('DELETE FROM numuneler WHERE kod=?', (kod,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Silme hatası: {e}")
        return False
    finally:
        conn.close()

def search_samples(conn, search_text):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT kod, proje_adi, ad, raf, miktar, birim, geldiği_tarih, geldiği_yer
        FROM numuneler
        WHERE kod LIKE ?
           OR ad LIKE ?
           OR proje_adi LIKE ?
    ''', (f"%{search_text}%", f"%{search_text}%"), f"%{search_text}%")
    return cursor.fetchall()


def get_all_samples():
    """Tüm numuneleri getirir (proje adına göre alfabetik sıralı)"""
    conn, cursor = veritabani_baglantisi()
    if conn is None or cursor is None:
        return []

    try:
        cursor.execute('''
            SELECT kod, proje_adi, ad, raf, miktar, birim, geldiği_tarih, geldiği_yer 
            FROM numuneler
            ORDER BY proje_adi ASC
        ''')
        return cursor.fetchall()
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return []
    finally:
        conn.close()


##########        MALZEME İŞLEMLERİ

def add_material(values):
    """Yeni malzeme ekler"""
    conn, cursor = veritabani_baglantisi()
    if conn is None or cursor is None:
        return False, "Veritabanı bağlantı hatası"

    kod = values[0]

    try:
        # Önce kodun varlığını kontrol et
        cursor.execute("SELECT 1 FROM malzemeler WHERE kod=?", (kod,))
        if cursor.fetchone():
            return False, f"'{kod}' kodu zaten kayıtlı!"

        # Yeni malzemeyi ekle
        cursor.execute('''
            INSERT INTO malzemeler (kod, ad, raf, miktar, birim, alındığı_tarih, alındığı_firma)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', values)
        conn.commit()
        return True, f"'{kod}' kodlu malzeme başarıyla eklendi"

    except sqlite3.IntegrityError as e:
        error_msg = str(e)
        if "UNIQUE" in error_msg:
            return False, f"'{kod}' kodu zaten mevcut!"
        return False, f"Veritabanı hatası: {error_msg}"

    except Exception as e:
        return False, f"Sistem hatası: {str(e)}"

    finally:
        if conn:
            conn.close()


def update_material(values):
            """Malzeme bilgilerini günceller"""
            conn, cursor = veritabani_baglantisi()
            if conn is None or cursor is None:
                return False

            try:
                cursor.execute('''
                    UPDATE malzemeler
                    SET kod=?, ad=?, raf=?, miktar=?, birim=?, alındığı_tarih=?, alındığı_firma=?
                    WHERE kod=?
                ''', values)
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                print(f"Güncelleme hatası: {e}")
                return False
            finally:
                conn.close()

def delete_material(kod):
            """Malzeme siler"""
            conn, cursor = veritabani_baglantisi()
            if conn is None or cursor is None:
                return False

            try:
                cursor.execute('DELETE FROM malzemeler WHERE kod=?', (kod,))
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                print(f"Silme hatası: {e}")
                return False
            finally:
                conn.close()

def search_materials(conn, search_text):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT kod, ad, raf, miktar, birim, alındığı_tarih, alındığı_firma
        FROM malzemeler
        WHERE kod LIKE ?
           OR ad LIKE ?
    ''', (f"%{search_text}%", f"%{search_text}%"))
    return cursor.fetchall()

def get_all_materials():
    """Tüm malzemeleri getirir"""
    conn, cursor = veritabani_baglantisi()
    if conn is None or cursor is None:
        return []

    try:
        cursor.execute('''
            SELECT kod, ad, raf, miktar, birim, alındığı_tarih, alındığı_firma 
            FROM malzemeler
        ''')
        return cursor.fetchall()
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return []
    finally:
        conn.close()




        # DEMİRBAŞ İŞLEMLERİ


def add_demirbas(values):
    """Yeni demirbaş ekler ve (başarı_durumu, mesaj) döndürür"""
    conn, cursor = veritabani_baglantisi()
    if conn is None:
        return False, "Veritabanı bağlantı hatası"

    demirbas_kod = values[0]

    try:
        cursor.execute("SELECT 1 FROM demirbaslar WHERE demirbas_kod=?", (demirbas_kod,))
        if cursor.fetchone():
            return False, f"Demirbaş kodu zaten kayıtlı!"

        cursor.execute('''
            INSERT INTO demirbaslar (demirbas_kod, ad, marka, alim_tarihi, durum)
            VALUES (?, ?, ?, ?, ?)
        ''', values)
        conn.commit()

        # 🔽 Log ekle
        log_ekle("demirbaslar", demirbas_kod, "EKLEME", f"{demirbas_kod} kodlu demirbaş eklendi")

        return True, f"'{demirbas_kod}' kodlu demirbaş başarıyla eklendi"

    except sqlite3.IntegrityError as e:
        return False, format_error_message(e)

    except Exception as e:
        return False, format_error_message(e)

    finally:
        if conn:
            conn.close()

def update_demirbas(values):
    """Demirbaş bilgilerini günceller"""
    conn, cursor = veritabani_baglantisi()
    if conn is None or cursor is None:
        return False

    try:
        cursor.execute('''
            UPDATE demirbaslar
            SET demirbas_kod=?, ad=?, marka=?, alim_tarihi=?, durum=?
            WHERE demirbas_kod=?
        ''', values)
        conn.commit()

        if cursor.rowcount > 0:
            log_ekle("demirbaslar", values[0], "GÜNCELLEME", f"{values[0]} kodlu demirbaş güncellendi")

        return cursor.rowcount > 0
    except Exception as e:
        print(f"Demirbaş güncelleme hatası: {e}")
        return False
    finally:
        conn.close()


def delete_demirbas(demirbas_kod):
    """Demirbaş siler"""
    conn, cursor = veritabani_baglantisi()
    if conn is None or cursor is None:
        return False

    try:
        cursor.execute('DELETE FROM demirbaslar WHERE demirbas_kod=?', (demirbas_kod,))
        conn.commit()

        if cursor.rowcount > 0:
            log_ekle("demirbaslar", demirbas_kod, "SİLME", f"{demirbas_kod} kodlu demirbaş silindi")

        return cursor.rowcount > 0
    except Exception as e:
        print(f"Demirbaş silme hatası: {e}")
        return False
    finally:
        conn.close()

def search_demirbaslar(arama_metni):
    """Demirbaşları kod, ad ve marka'ya göre arar"""
    conn, cursor = veritabani_baglantisi()
    if conn is None or cursor is None:
        return []

    try:
        cursor.execute('''
            SELECT demirbas_kod, ad, marka, alim_tarihi, durum
            FROM demirbaslar 
            WHERE demirbas_kod LIKE ? OR ad LIKE ? OR marka LIKE ?
        ''', (f"%{arama_metni}%", f"%{arama_metni}%", f"%{arama_metni}%"))
        return cursor.fetchall()
    except Exception as e:
        print(f"Demirbaş arama hatası: {e}")
        return []
    finally:
        conn.close()


def get_all_demirbaslar():
    """Tüm demirbaşları getirir"""
    conn, cursor = veritabani_baglantisi()
    if conn is None or cursor is None:
        return []

    try:
        cursor.execute('SELECT * FROM demirbaslar')
        return cursor.fetchall()
    except Exception as e:
        print(f"Demirbaş listeleme hatası: {e}")
        return []
    finally:
        conn.close()
# Hata mesajları sözlüğü
HATA_MESAJLARI = {
    # SQLite hataları
    "UNIQUE constraint failed: demirbaslar.demirbas_kod": "Bu demirbaş kodu zaten sistemde kayıtlı!",
    "FOREIGN KEY constraint failed": "Geçersiz referans değeri!",
    "NOT NULL constraint failed": "Zorunlu alanlar boş bırakılamaz!",
    
    # Özel hatalar
    "DB_CONNECTION_ERROR": "Veritabanı bağlantı hatası oluştu",
    "DUPLICATE_CODE": "Bu demirbaş kodu zaten mevcut",
    
    # Genel hatalar
    "DEFAULT": "İşlem sırasında bir hata oluştu"
}

def format_error_message(error):
    """Hata mesajlarını kullanıcı dostu hale getirir"""
    error_str = str(error)
    
    # Hata mesajını sözlükte ara
    for key, message in HATA_MESAJLARI.items():
        if key in error_str:
            return message
    
    # Eşleşme yoksa genel hata mesajı dön
    return HATA_MESAJLARI["DEFAULT"]        