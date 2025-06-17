import os
import subprocess
import requests
import atexit

# Configuratie
REG_FILES = {
    "stopwu": {
        "filename": "stopwu.reg",
        "url": "https://github.com/VulcanoSoftware/windows-update-toggle/raw/refs/heads/main/stopwu.reg"
    },
    "startwu": {
        "filename": "startwu.reg",
        "url": "https://github.com/VulcanoSoftware/windows-update-toggle/raw/refs/heads/main/startwu.reg"
    }
}

def cleanup():
    """Verwijder alle REG-bestanden bij afsluiten"""
    for reg in REG_FILES.values():
        try:
            if os.path.exists(reg["filename"]):
                os.remove(reg["filename"])
        except Exception as e:
            print(f"Fout bij verwijderen van {reg['filename']}: {e}")

def download_reg_file(reg_key):
    """Download het REG-bestand van GitHub"""
    reg = REG_FILES[reg_key]
    try:
        response = requests.get(reg["url"])
        response.raise_for_status()
        
        with open(reg["filename"], 'wb') as f:
            f.write(response.content)
        
        print(f"{reg['filename']} is gedownload.")
        return True
    except Exception as e:
        print(f"Fout bij downloaden van {reg['filename']}: {e}")
        return False

def run_reg_file(reg_key):
    """Voer het REG-bestand uit"""
    reg = REG_FILES[reg_key]
    
    # Download als het bestand niet bestaat
    if not os.path.exists(reg["filename"]):
        if not download_reg_file(reg_key):
            return False
    
    try:
        # Voer het REG-bestand uit met regedit
        subprocess.run(["regedit.exe", "/s", reg["filename"]], check=True)
        print(f"'{reg['filename']}' is succesvol uitgevoerd. Registerwijzigingen zijn toegepast.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Fout bij uitvoeren van {reg['filename']}: {e}")
        return False
    except Exception as e:
        print(f"Onverwachte fout: {e}")
        return False

def check_admin():
    """Controleer of het script als administrator wordt uitgevoerd"""
    try:
        # Probeer een beheerderactie uit te voeren
        with open(os.path.join(os.getenv("SystemRoot"), "temp.txt"), 'w') as f:
            f.write("test")
        os.remove(os.path.join(os.getenv("SystemRoot"), "temp.txt"))
        return True
    except PermissionError:
        return False
    except Exception:
        return False

def main():
    # Registreer cleanup functie
    atexit.register(cleanup)
    
    # Controleer administrator rechten
    if not check_admin():
        print("Waarschuwing: Dit programma vereist administratorrechten.")
        print("Start het opnieuw op als administrator voor de juiste werking.")
    
    print("Windows Update Tool")
    print("=" * 30)
    print("Maak je computer minder irritant met deze tool.")
    print("-" * 30)
    print("1. Schakel Windows Update UIT (stopwu.reg)")
    print("2. Schakel Windows Update IN (startwu.reg)")
    print("3. Afsluiten")
    
    while True:
        choice = input("\nMaak uw keuze (1-3): ").strip()
        
        if choice == "1":
            if run_reg_file("stopwu"):
                print("Windows Update is nu uitgeschakeld.")
            break
        elif choice == "2":
            if run_reg_file("startwu"):
                print("Windows Update is nu ingeschakeld.")
            break
        elif choice == "3":
            print("Programma afgesloten.")
            break
        else:
            print("Ongeldige keuze. Voer 1, 2 of 3 in.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgramma door gebruiker afgebroken.")
    except Exception as e:
        print(f"Er is een fout opgetreden: {e}")
    finally:
        # Zorg dat cleanup wordt uitgevoerd
        input("Druk op Enter om af te sluiten...")
        cleanup()