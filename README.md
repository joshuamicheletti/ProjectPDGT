# ProjectPDGT

Nome: Joshua Micheletti

Matricola: 283507

Pubblicato sotto licenza GNU GPLv3

Questa web API fornisce metodi per la gestione di utenti, gestione di server (bucket) e gestione di file all'interno di server (bucket).
Ogni comunicazione con il servizio viene fatta tramite richieste HTTP.
Queste funzionalità consentono il trasferimento controllato di file tra utenti, suddividendo i file tra server, accessibili tramite password.

Il servizio è hostato sul server "https://projectpdgt.herokuapp.com".

L'API funziona tramite Node.js, utilizzando le seguenti librerie:
- express
- js-sha256
- cookie-parser
- multer
- minio

I file vengono salvati in un server Minio (servizio di blob storage), utilizzato tramite API Minio per Node.js.

I server Minio disponibili a cui il servizio può fare riferimento sono:
- mathorgadaorc.ddns.net:9000
- solidgallium.ddns.net:9000
- solidgallium.ddns.net:9002
- solidgallium.ddns.net:9004

# Metodi

Il servizio mette a disposizione i seguenti metodi HTTP:
- Login: GET /login, richiete header "Authorization: Basic", consente di eseguire il login con il nome utente e password forniti nell'header Authorization.
- Login cookie: POST /login, richiede header "Authorization: Basic" o "Cookie", consente di effettuare il login ed ottenere un cookie
- Register: POST /users, richiede header "Authorization: Basic", consente di creare un nuovo utente
- Delete: DELETE /users, richiede header "Authorization: Basic", consente di eliminare un utente

- List servers: GET /servers, ritorna la lista di server disponibili
- Login server: GET /servers, richiede header "Authorization: Basic" e query "serverName" e "serverPassword", consente di effettuare il login in un server
- Create server: POST /servers, richiede header "Authorization: Basic" e query "serverName" e "serverPassowrd", consente di creare un nuovo server. L'utente che ha creato il server sarà il proprietario del server
- Delete server: DELETE /servers, richiede header "Authorization: Basic" e query "serverName" e "serverPassword", consente di eliminare un server, disponibile solo al proprietario del server

- Check files: GET /upload, richiede query "serverName" e "serverPassword", ritorna la lista di file presenti in un server
- Upload file: POST /upload, richiede header "Authorization: Basic", "Content-Type", "Content-Length", "Content-Disposition", "filename" e query "serverName" e "serverPassword". Consente di caricare un file, disponibile solo al proprietario del server
- Download file: GET /download, richiede header "Authorization: Basic" e query "serverName", "serverPassword" e "fileName". Consente di scaricare un file da un server
- Delete file: DELETE /upload, richiede header "Authorization: Basic" e query "serverName", "serverPassword" e "fileName". Consente di eliminare un file da un server, disponibile solo per il proprietario del server.

- Change Minio Server: POST /minio, richiede query "serverAddress" e "serverPort". Consente di cambiare server minio (i file non sono condivisi tra server)

Oltre all'API è disponibile un client per l'utilizzo dei metodi forniti dal servizio.

Questo client é scritto interamente in Python e sfrutta le seguenti librerie:
- requests
- base64
- re
- os
- keyboard
- sys
- stdiomask
- time
- termcolor
- tkinter
- termos (ubuntu) / msvcrt (windows)

Di seguito riportate sono le tre schermate principali del client che consentono rispettivamente la gestione di utenti, la gestione di server e la gestione di file all'interno del server:

![img1](https://ibb.co/yPGV2w6)
![img2](https://ibb.co/M77wMtL)
![img3](https://ibb.co/KjHwKGw)


Per installare il client sono disponibili script di installazione per Windows 10 e Ubuntu 20.04.

# Installazione

Windows 10:

- Scaricare la repository (da github o tramite "git clone https://github.com/joshuamicheletti/ProjectPDGT.git)
- Recarsi alla directory ProjectPDGT\client\installWindows
- Per eseguire questo programma serve Python. Python é disponibile nel Microsoft Store. Il file "installPython.bat" ricondurrà alla pagina per scaricare Python in caso non sia presentw nel dispositivo
- Eseguire lo script "install.bat"
- Il programma é installato! Per eseguirlo, recarsi presso PrpjectPDGT\client ed eseguire lo script "launch.bat"


Ubuntu 20.04:

- Scaricare la repository (da github o tramite "git clone https://github.com/joshuamicheletti/ProjectPDGT.git)
- Recarsi alla directory ProjectPDG/client/installUbuntu
- Eseguire lo script "install.sh"
- Il programma é installato! Per eseguirlo, recarsi presso PrpjectPDGT/client ed eseguire lo script "launch.sh"


# Disinstallazione

Windows 10:

Questa procedura rimuoverà tutte le dipendenze mecessarie per il funzionamento del client (requests, keyboard, stdiomask, termcolor)
Se si desidera mantenere una qualsiasi di questi programmi, declinare il processo di disinistallazione quando viene richiesta la conferma.

- Entra nella directory ProjectPDGT\client\installWindows
- Esegui lo script "uninstall.bat"
- Decidi cosa tenere e cosa eliminare quando viene chiesta la conferma
- Se si desidera disinstallare python, recarsi presso il Microsoft Store e disinstallare dalla pagina corriapondente (la stessa pagina usata per l'installazione)


Ubuntu 20.04:

Questa procedura rimuoverà tutte le dipendenze mecessarie per il funzionamento del client (keyboard, stdiomask, termcolor, python3-tk, pip, python3-setuptools)
Se si desidera mantenere una qualsiasi di questi programmi, declinare il processo di disinistallazione quando viene richiesta la conferma.

- Entra nella directory ProjectPDGT/client/installUbuntu
- Esegui lo script "uninstall.sh"
- Decidi cosa tenere e cosa eliminare quando viene chiesta la conferma
