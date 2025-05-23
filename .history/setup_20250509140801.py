from cx_Freeze import setup, Executable
import os

# Veritabanı dosyasının yolunu belirt
db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), r"C:\Users\aciog\Desktop\Kardökmak Ar-Ge\Ar-Ge-_App\arge.db")
assets_dir = os.path.join(base_dir, "assets")
# Uygulama bilgileri
setup(
    name="Ar-Ge Takip",
    version="1.0",
    description="Ar-Ge Takip Uygulaması",
    options={
        'build_exe': {
            'include_files': [
                db_file,
                 (assets_dir, "assets")
                 ]  # Veritabanı dosyasını dahil et
        }
    },
    executables=[Executable("main.py", base="Win32GUI", target_name="Ar-Ge Takip.exe", icon=r"C:\Users\aciog\Desktop\Kardökmak Ar-Ge\Ar-Ge-_App\assets\arge.ico")]
)
