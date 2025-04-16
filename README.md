# Edge Pi Project

## Deployment Edge Impulse
Als je jouw model getraind en getest hebt in Edge Impulse Studio kun je in het tabblad Deployment je model exporteren. Gebruik daarvoor onderstaande achitectuur. 

![afbeelding](https://github.com/user-attachments/assets/1882c7b7-7f1a-4e60-947f-570e6e7920c7)

Hernoem het gedownloade naar: `rpi4-blokjes.eim`

## Overzicht
Dit project draait een objectdetectieproces op een Raspberry Pi (of Linux-systeem) met behulp van een Edge Impulse model en communiceert via MQTT. Bij elke detectie wordt een afbeelding gemaakt, geanalyseerd en het resultaat gepubliceerd. Resultaten worden opgeslagen, gelogd en visueel weergegeven.

## Functionaliteiten
- Trigger via MQTT
- Foto maken met USB-camera
- Inference via Edge Impulse `.eim` model
- Terugkoppeling via MQTT
- Retry-structuur bij lage confidence
- Logging naar bestand en console met logrotatie
- Viewer toont laatste gedetecteerde afbeelding
- Logviewer toont realtime systeemlogboek

## Projectstructuur

```
edge_pi_project/
├── config/
│   ├── config.ini              
│   └── config_example.ini      # Voorbeeldbestand, kopieer naar config.ini en vul zelf in (stap 4)
├── debug/                      # Opgeslagen afbeeldingresultaten met bounding box
├── images/                     # Tijdelijke camerabeelden
├── logs/                       # Logbestanden met automatische rotatie
├── model/
│   └── rpi4-blokjes.eim        # Edge Impulse modelbestand
├── scripts/
│   ├── camera_capture.py
│   ├── inference.py
│   ├── logger_setup.py
│   ├── logviewer.py
│   ├── main.py
│   ├── mqtt_handler.py
│   └── viewer.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Installatie

### 1. Clone de repository
```bash
git clone https://github.com/RTMA/edge-pi-project.git
cd edge-pi-project
```

### 2. Maak een virtuele omgeving aan
```bash
python3 -m venv ei_env
source ei_env/bin/activate
```

### 3. Installeer de dependencies
```bash
sudo apt install portaudio19-dev
pip install -r requirements.txt
```

### 4. Configureer MQTT-instellingen
```bash
cp config/config_example.ini config/config.ini
nano config/config.ini
```
Vul jouw informatie in in de config.ini

#### Model overzetten naar de Pi
Gebruik WinSCP of Visual Studio Remote SSH om het bestand `rpi4-model.eim` te kopieren naar je raspberry pi.
Plaatse deze in de `edge-pi-project/model` map 

#### Maak het model executable 
Om het model te kunnen gebruiken voor detectie moet het executable zijn. Dat kunnen met onderstaande commando uitvoeren. 
Ga naar model directory waar je net het model hebt geplaatst.
```
cd model
sudo chmod +x rpi4-blokjes.eim
```

#### Video kanaal
Het programma is zo ingesteld dat hij videokanaal 0 als standaard video probeert. Mocht jouw USB camera op een ander kanaal zitten (`ls /dev/video*`) dan kun je dit wijzigen op regel 19 van `scripts/main.py` 

## Gebruik van het programma
### Beeldscherm
Om het op een raspberry pi met beelden te werken is het het makkelijkste om een beeldschem via HDMI te verbinden met je Raspberry Pi en werk rechtstreeks op de Raspberry met een toetsenbord en muis. 
Andere optie is om via PiConnect verbinding te maken met je Raspberry en via je Laptop te werken. Voer onderstaande commandos dan uit in de PiConnect omgeving. 

### Start detectiesysteem
```bash
cd ~/edge-pi-project
source ei_env/bin/activate
python scripts/main.py
```

### Start viewer in aparte terminal
```bash
cd ~/edge-pi-project
source ei_env/bin/activate
cd scripts
python viewer.py
```

### Bekijk eventueel realtime systeemlogs in aparte terminal
```bash
cd edge-pi-project
python scripts/logviewer.py
```

## Troubleshooten
Als je de error: `Could not find the QT platform plugin 'wayland' ... ` krijgt. Kun je dit oplossen door onderstaande code onder de imports in viewer.py toe te voegen.
```python
import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

```

```
cd ~/~/edge-pi-project/scripts
nano viewer.py
```

## Retry-structuur
Bij detectie onder de confidence-drempel (0.7) wordt automatisch tot 5 keer opnieuw geprobeerd een afbeelding te maken en te analyseren. Indien nog steeds geen betrouwbare detectie → label `'onbekend'`. Aan te passen in main.py

## Opruimen van oude afbeeldingen
Afbeeldingen worden opgeslagen in `debug/`. 

## Logbestanden
Alle systeemactiviteiten worden gelogd in:
```
logs/detectie.log
```
- Dagelijkse rotatie via `TimedRotatingFileHandler`
- 30 dagen bewaartijd

