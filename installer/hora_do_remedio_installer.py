import os
import shutil
import subprocess
import sys
from pathlib import Path
from tkinter import Tk, messagebox


APP_NAME = "Hora do Remedio"
EXE_NAME = "HoraDoRemedio.exe"


def bundled_file(name: str) -> Path:
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_dir / name


def install_dir() -> Path:
    local_app_data = os.getenv("LOCALAPPDATA") or str(Path.home())
    return Path(local_app_data) / "Programs" / APP_NAME


def create_shortcuts(target: Path) -> None:
    script = f"""
$target = '{str(target).replace("'", "''")}'
$desktop = [Environment]::GetFolderPath('Desktop')
$programs = [Environment]::GetFolderPath('Programs')
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut((Join-Path $desktop 'Hora do Remedio.lnk'))
$shortcut.TargetPath = $target
$shortcut.WorkingDirectory = Split-Path $target
$shortcut.Save()
$folder = Join-Path $programs 'Hora do Remedio'
New-Item -ItemType Directory -Force -Path $folder | Out-Null
$shortcut = $shell.CreateShortcut((Join-Path $folder 'Hora do Remedio.lnk'))
$shortcut.TargetPath = $target
$shortcut.WorkingDirectory = Split-Path $target
$shortcut.Save()
"""
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        check=False,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def main() -> int:
    root = Tk()
    root.withdraw()

    try:
        source = bundled_file(EXE_NAME)
        destination_dir = install_dir()
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / EXE_NAME
        shutil.copy2(source, destination)
        create_shortcuts(destination)
        messagebox.showinfo(
            "Hora do Remédio",
            "Instalação concluída.\n\nUse o botão 'Configurar chave da API' dentro do aplicativo.",
        )
        subprocess.Popen([str(destination)], cwd=str(destination_dir))
        return 0
    except Exception as exc:
        messagebox.showerror("Erro na instalação", str(exc))
        return 1
    finally:
        root.destroy()


if __name__ == "__main__":
    raise SystemExit(main())
