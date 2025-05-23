from cx_Freeze import setup, Executable
import os

# Uygulama dizinini ve asset dosyalarının yolunu dinamik olarak al
base_dir = os.path.dirname(os.path.abspath(__file__))

# Veritabanı ve görsel dosyasının dinamik yolları
db_file = os.path.join(base_dir, "assets", "arge.db")  # Veritabanı dosyasının yolu
assets_file = os.path.join(base_dir, "assets", "arge.jpg")  # Görsel dosyasının yolu
icon_file = os.path.join(base_dir, "assets", "arge.ico")  # İkon dosyasının yolu

# Uygulama bilgileri
setup(
    name="Ar-Ge Takip",
    version="1.0",
    description="Ar-Ge Takip Uygulaması",
    options={
        'build_exe': {
            'include_files': [
                db_file,  # Veritabanı dosyasını dahil et
                assets_file,  # Görsel dosyasını dahil et
                (os.path.join(base_dir, "assets"), "assets"),  # assets klasörünü dahil et
            ],
        }
    },
    executables=[Executable("main.py", base="Win32GUI", target_name="Ar-Ge Takip.exe", icon=icon_file)]
)
