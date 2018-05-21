# Import packages
import paramiko #SSH
import telnetlib # Telnet
import sys
from datetime import datetime
import time
import schedule
import os.path

# Gather Switch IPs
f = open("switches.txt", "r")
switches = f.read().split('\n')

# Create and configure SSH Client
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Empty Telnet Object ready for connecting
telnet = None

# SSHMode
sshMode = True      # Default mode is SSH
                    # Will switch if SSH fails and Telnet works
                    # Reverts once completed

def checkPorts():
                    
    # Update overview text files
    def updateOverviews(ip, trues, falses):
        # IF the file doesn't exist, create and add falses
        if not(os.path.exists("ports/" + ip + "/overview.txt")):
            f = open("ports/" + ip + "/overview.txt","w+")  # Open
            
            # Build file content
            falseList = ""
            for port in falses:
                falseList += port + "\n"
                
            f.write(falseList)                              # Write
            f.close                                         # Close
        # IF file exists, update based on trues and write
        else:
            # Open READ
            f = open("ports/" + ip + "/overview.txt","r")   # Open
            content = f.read()                              # Pull contents
            f.close                                         # Close

            # Strip ports that are no longer false
            for port in trues:
                content = content.replace(port + "\n", "")
                
            # Open WRITE
            f = open("ports/" + ip + "/overview.txt","w")   # Open
            f.write(content)                                # Write
            f.close                                         # Close
    
    # Run a command
    def gatherInfo(ip):
        gathered = False
        # Init list for port info
        rows = []
        # Init true list for overview checker
        trues = []
        falses = []

        # Execute the command
        global sshMode
        if (sshMode):
            #if (hasattr(client, "open_session")):
            stdin, stdout, stderr = client.exec_command("show int status")

            # Store command output into list
            for line in stdout:
                if (line != '\r\n'): # Scrape off fluff
                    rows.append(line) # Add line to list
            rows.pop(0) # Remove header entry
            gathered = True
        else:
            global telnet
            telnet.write("show int status\n".encode())
            telnet.write("exit\n".encode())

            results = (telnet.read_all()).decode()
            rows = results.splitlines()
            # Remove fluff rows
            if ('^' not in results):
                rows.pop(0)
                rows.pop(0)
                rows.pop(0)
                rows.pop(0)
                rows.pop(0)
                rows.pop()
                rows.pop()
                gathered = True
            else:
                print ("Data fetch failed due to 'Invalid input detected error'")
                gathered = False

        if (gathered):

            # Create any needed switch folders
            if not os.path.exists("ports/" + ip):
                os.makedirs("ports/" + ip)

            # Format each port entry in list and write to file
            for line in rows:
                # Extract and format port name for file name system
                port = line.split(" ")[0]
                port = port.replace("/", "_")

                # Extract connected status
                if "connected" in line:
                    status = True
                if "notconnect" in line:
                    status = False

                # Compile timestamp and connection status into string
                results = str(datetime.now()) + "\t" + str(status) + "\n"

                # Determine if the file exists or not
                # Then open file, write/append, close
                if not(os.path.exists("ports/" + ip + "/" + port + ".txt")):
                    f = open("ports/" + ip + "/" + port + ".txt","w+")
                    f.write(results)
                    f.close
                else:
                    f = open("ports/" + ip + "/" + port + ".txt","a+")
                    f.write(results)
                    f.close

                if status:
                    trues.append(port)
                else:
                    falses.append(port)

            print ("Updating overview...")
            updateOverviews(ip, trues, falses)

            print ("Check completed.")

    # Connect to switch
    def connect(ip):
        # Connection details
        port = 22
        username = '[username details]'
        password = '[password details]'

        # Connect via SSH
        print ("Attempting SSH...")
        try:
            client.connect(ip, port, username=username, password=password)
            print ("Connection successful.")
            return True
        except:
            print ("Connection failed.")
            # return False # Enable this line if you want to lock out Telnet connecting

        # Connect via Telnet
        print ("Attempting Telnet...")
        try:
            global telnet
            telnet = telnetlib.Telnet(ip)
            print("Telnet established.")
            telnet.read_until("Username: ".encode())
            telnet.write((username + "\n").encode())
            print("Username inputed.")
            telnet.read_until("Password: ".encode())
            telnet.write((password + "\n").encode())
            print("Password inputed.")
            global sshMode
            sshMode = False
            return True
        except:
            print ("Connection failed.\n")
            return False

    # Loop through all switch IPs
    for ip in switches:
        # Print connection time
        print (str(datetime.now()))
        # Connect and proceed if the connection is successful
        print ("Connecting to " + ip + "...")
        if connect(ip):
            # Check Ports
            print ("Checking ports...")
            gatherInfo(ip)

            # Close the connection
            client.close()
            print ("Closed the connection.\nWaiting for next check...\n")

            # Reset mode
            global sshMode
            sshMode = True

# Schedule the job
print("Scheduling job...")
schedule.every(30).minutes.do(checkPorts)
print("Job has been scheduled.\n")

# Start the schedule loop
checkPorts()
while True:
    schedule.run_pending()
    time.sleep(60) # wait one minute
