#######################################################################################
# Yourname:
# Your student ID:
# Your GitHub Repo: 

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import os
import time
import json
import requests
from dotenv import load_dotenv
from restconf_final import create, delete, enable, disable, status

#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.

load_dotenv()  # โหลดค่าจากไฟล์ .env (ถ้ามี)
WEBEX_TOKEN = os.getenv("WEBEX_TOKEN")

if not WEBEX_TOKEN:
    raise SystemExit("ไม่พบ WEBEX_TOKEN ใน environment/.env")

ACCESS_TOKEN = f"Bearer {WEBEX_TOKEN}"

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = os.getenv("WEBEX_ROOM_ID")
if not roomIdToGetMessages:
    raise SystemExit("ไม่พบ WEBEX_ROOM_ID ใน .env")

while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is the ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    getParameters = {"roomId": roomIdToGetMessages, "max": 1}

    # the Webex Teams HTTP header, including the Authoriztion
    getHTTPHeader = {"Authorization": ACCESS_TOKEN}

# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
    
    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
        )

    # get the JSON formatted returned data
    json_data = r.json()

    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # store the array of messages
    messages = json_data["items"]
    
    # store the text of the first message in the array
    message = messages[0]["text"]
    print("Received message: " + message)

    # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
    #  e.g.  "/66070123 create"
    if message.startswith("/66070273 "):

        # extract the command
        command = message.split(" ")[1].strip()
        print("Command:", command)

# 5. Complete the logic for each command

        if command == "create":
            responseMessage = create()
            if responseMessage == "ok":
                responseMessage = "Interface loopback 66070273 is created successfully"
            else:
                responseMessage = "Cannot create: Interface loopback 66070273"

        elif command == "delete":
            responseMessage = delete()
            if responseMessage == "ok":
                responseMessage = "Interface loopback 66070273 is deleted successfully"
            else:
                responseMessage = "Cannot delete: Interface loopback 66070273"

        elif command == "enable":
            responseMessage = enable()
            if responseMessage == "ok":
                responseMessage = "Interface loopback 66070273 is enabled successfully"
            else:
                responseMessage = "Cannot enable: Interface loopback 66070273"

        elif command == "disable":
            responseMessage = disable()
            if responseMessage == "ok":
                responseMessage = "Interface loopback 66070273 is shutdowned successfully"
            else:
                responseMessage = "Cannot shutdown: Interface loopback 66070273"

        elif command == "status":
            responseMessage = status()

        else:
            responseMessage = "Error: No command or unknown command"
        
# 6. Complete the code to post the message to the Webex Teams room.

        # The Webex Teams POST JSON data for command showrun
        # - "roomId" is is ID of the selected room
        # - "text": is always "show running config"
        # - "files": is a tuple of filename, fileobject, and filetype.

        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        
        # Prepare postData and HTTPHeaders for command showrun
        # Need to attach file if responseMessage is 'ok'; 
        # Read Send a Message with Attachments Local File Attachments
        # https://developer.webex.com/docs/basics for more detail
        if command == "showrun" and responseMessage == 'ok':
            # ตั้งชื่อไฟล์ show run ที่ต้องการส่งกลับ
            filename = "showrun.txt"  # หรือระบุ path เช่น "./showrun.txt"

            # เปิดไฟล์ในโหมด binary
            fileobject = open(filename, "rb")

            # กำหนดประเภทไฟล์
            filetype = "text/plain"

            # เตรียมข้อมูลที่จะส่งไป Webex (roomId, ข้อความ, และไฟล์แนบ)
            postData = {
                "roomId": roomIdToGetMessages,
                "text": "show running config",
                "files": (filename, fileobject, filetype),
            }

            # แปลงข้อมูลให้เป็น Multipart form
            postData = MultipartEncoder(postData)

            # Header ที่ใช้ Bearer Token และ Content-Type แบบ Multipart
            HTTPHeaders = {
                "Authorization": ACCESS_TOKEN,
                "Content-Type": postData.content_type,
            }
        # other commands only send text, or no attached file.
        else:
            postData = {"roomId": roomIdToGetMessages, "text": responseMessage}
            postData = json.dumps(postData)

            # the Webex Teams HTTP headers, including the Authorization and Content-Type
            HTTPHeaders = {
                "Authorization": ACCESS_TOKEN,
                "Content-Type": "application/json"
            }
        # Post the call to the Webex Teams message API.
        r = requests.post(
            "https://webexapis.com/v1/messages",
            data=postData,
            headers=HTTPHeaders,
        )
        if not r.status_code == 200:
            raise Exception(
                f"Incorrect reply from Webex Teams API. Status code: {r.status_code}"
            )
        else:
            print("Message sent successfully!")