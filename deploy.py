from simple_automation import host
from simple_automation.operations import local

somedefault = 134

#print(f"[+] Run script {__file__} on host {host.name}")
#files.directory(name="Create a temporary directory",
#                path="/tmp/abc_700",
#                mode="700")
local.script(name="Run script",
             script="deploy2.py")

if "desktops" in host.groups:
    print("is desktop")
