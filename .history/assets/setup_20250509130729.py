from cx_Freeze import setup, Executable
import os

# Veritabanı dosyasının yolunu belirt
db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arge.db")

# Uygulama bilgileri
setup(
    name="Ar-Ge Takip",
    version="1.0",
    description="Ar-Ge Takip Uygulaması",
    options={
        'build_exe': {
            'include_files': [db_file]  # Veritabanı dosyasını dahil et
        }
    },
    executables=[Executable("main.py", base="Win32GUI", targetName="ArGe_Takip.exe", icon="C:/Users/aciog/Desktop/Kardökmak Ar-Ge/Ar-Ge-_App/arge.ico")]
)
