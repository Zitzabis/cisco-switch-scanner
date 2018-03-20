# Cisco Catalyst Switch Scanner
A script that scans a list of network switches and determines active/inactive ports.

This is a Python driven script that allows network admins to determine which ports are active and inactive on a Cisco Catalyst switch.
The goal is to allow network admins to indentify inactive ports so that they can be unplugged to free up space for any new connections.

## Support
The script works with both:
- SSH
- Telnet

Note: Telnet is highly insecure and should be avoided. However certain systems still use switches that are running older OSs that do not support SSH. Due to this, support has been provided.

## Process
1. Pull all IPs from switches.txt.
2. Attempt to connect to each IP.
3. If SSH fails, retry with Telnet. If both fail, move to next switch.
4. If connection was successful, run `show int status` to show all switches and their status.
5. Extract data from command.
6. Format data.
7. Store data in correct files and .TXT files.
8. Move to next switch until list is done, and then repeat every 30 minutes.

## Overview Files
These files list all ports for an IP that have been `notconnect` since the start of the scanning process. If a port becomes active, then it will be removed from the list.