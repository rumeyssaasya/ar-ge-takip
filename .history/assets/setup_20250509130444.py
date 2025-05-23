from cx_Freeze import setup, Executable

# Uygulama bilgileri
setup(
    name="Ar-Ge Takip",
    version="1.0",
    description="Ar-Ge Takip Uygulaması",
    executables=[Executable("main.py", base="Win32GUI", targetName="ArGe_Takip.exe", icon="arge.ico")]
)
