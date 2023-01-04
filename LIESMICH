####### Java SE Runtime und Maven Download #######
-> https://www.eclipse.org/downloads/packages/release/2018-09/r/eclipse-ide-java-developers

####### Ändern der Config Parameter #######
	0. Installiert Java (https://java.com/de/download/) auf euren Rechnern


####### Ändern der Config Parameter
    1. Ersetzt die Werte in properties.settings mit euren Account- und DB Daten


####### Anlegen einer virtuellen Umgebung (einmalig) #######
    1. Zum Projektordner navigieren -> cd /home/dbpXXX/block3/projekte/python/carSharer/
    2. python3 -m venv venv
    3. c

####### Installation der Dependencies (einmalig) #######
    pip install -r requirements.txt

####### Starten der Webanwendung #######
    Von der IDE PyCharm aus:
        Nur beim ERSTEN MAL:
            1. Wähle "Do not import settings" aus
            2. -> Open -> Car Sharer -> Settings -> Project Interpreter -> Add -> venv
            3. Unter existing environment: Wähle Interpreter /home/dbpXXX/block3/projekte/python/carSharer/venv/bin/python.
               Ersetze XXX mit eurer Gruppennummer

         Sonst führe das Skript app.py aus

    Von der Konsole aus:
        1. In das Projektverzeichnis wechseln (z.B. /home/dbpXXX/block3/projekte/python/carSharer)
        2. Aktiviere virtuelle Umgebung mit Anweisung: source venv/bin/activate
        3. python app.py ausführen

####### Um sich von außerhalb der Uni mit der DB zu verbinden: #######
Die Datei properties.settings überarbeiten.  Die Methode getExternalConnection() in DBUtil (in Skript-Datei connect.py) verwenden.

####### Troubleshooting für externe Connections: #######
1. db2start / db2stop auf dem remote Rechner ausführen
2. Überprüfe, ob der Port richtig gesetzt ist. Der Port müssete 50XXX sein, wobei XXX für eure Gruppennummer steht.
3. Überprüfe, ob der remote Rechner auf dem Port lauscht: db2 get dbm cfg | grep SVCE
