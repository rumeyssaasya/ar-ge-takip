from cx_Freeze import setup, Executable
import os

# Veritabanı dosyasının ve assets klasörünün yolunu belirt
db_file = r"C:\Users\aciog\Desktop\Kardökmak Ar-Ge\Ar-Ge-_App\arge.db"
assets_file = os.path.join(base_dir, r"C:\Users\aciog\Desktop\Kardökmak Ar-Ge\Ar-Ge-_App\assets\arge.jpg")

# Uygulama bilgileri
setup(
    name="Ar-Ge Takip",
    version="1.0",
    description="Ar-Ge Takip Uygulaması",
    options={
        'build_exe': {
            'include_files': [
                db_file,  # Veritabanı dosyasını dahil et
                assets_file # assets klasörünü dahil et
            ]
        }
    },
    executables=[Executable("main.py", base="Win32GUI", target_name="Ar-Ge Takip.exe", icon=r"C:\Users\aciog\Desktop\Kardökmak Ar-Ge\Ar-Ge-_App\assets\arge.ico")]
)
