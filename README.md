# Edge Pi Project

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
pip install -r requirements.txt
```

### 4. Configureer MQTT-instellingen
```bash
cp config/config_example.ini config/config.ini
nano config/config.ini
```
Vul jouw informatie in in de config.ini
Het is het makkelijkste als je jouw dezelfde naam geeft als dat in het project is gebruikt: `model/rpi4-blokjes.eim`

## Gebruik

### Start detectiesysteem
```bash
source ei_env/bin/activate
python scripts/main.py
```

### Start viewer in aparte terminal
```bash
python scripts/viewer.py
```

### Bekijk eventueel realtime systeemlogs in aparte terminal
```bash
python scripts/logviewer.py
```

## Retry-structuur
Bij detectie onder de confidence-drempel (0.7) wordt automatisch tot 5 keer opnieuw geprobeerd een afbeelding te maken en te analyseren. Indien nog steeds geen betrouwbare detectie → label `'onbekend'`. Aan te passen in main.py

## Opruimen van oude afbeeldingen
Afbeeldingen worden opgeslagen in `debug/`. Voeg een cleanup-script of cronjob toe om bestanden ouder dan 7 dagen automatisch te verwijderen.

## Logbestanden
Alle systeemactiviteiten worden gelogd in:
```
logs/detectie.log
```
- Dagelijkse rotatie via `TimedRotatingFileHandler`
- 30 dagen bewaartijd

