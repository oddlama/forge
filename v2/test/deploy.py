from simple_automation import this, host
from simple_automation.operations import local

print(f"[+] Run script {__file__} on host {host.name}")
local.script(name="Run script",
             script="deploy2.py")

if "desktops" in host.groups:
    print("is desktop")
