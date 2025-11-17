import os
import platform
import subprocess
import traceback
from functools import wraps
# --------------------------------------------------------------------------------------------------
#                               Constant : dut_ports_config.py   (START)
# --------------------------------------------------------------------------------------------------

port_config_prompt_update = """# DUT Port Configuration
# [DUT IP]
# ports=
#     pci=Pci BDF,intf=Kernel interface;
#     pci=Pci BDF,mac=Mac address,peer=Tester Pci BDF,numa=Port Numa
#     pci=Pci BDF,peer=IXIA:card.port
#     pci=Pci BDF,peer=TREX:port
#     pci=Pci BDF,peer=Tester Pci BDF,tp_ip=$(IP),tp_path=$({{PERL_PATH}});
#     pci=Pci BDF,peer=Tester Pci BDF,sec_port=yes,first_port=Pci BDF;
# [VM NAME] virtual machine name; This section is for virtual scenario
# ports =
#     dev_idx=device index of ports info, peer=Tester Pci BDF
[{}]
ports =
{}
"""

port_config_auth_prompt = (
    "\n🔐 **Authentication Required**\n"
    "----------------------------------\n"
    "👤 Username : {username}\n"
    "🌐 IP Address : {ip}\n"
    "\n💬 Please enter your password to proceed...\n"
)
port_config_auth_confirm = (
    "\n🔐 **Authentication Confirmation**\n"
    "--------------------------------------\n"
    "👤 Username : {username}\n"
    "🌐 IP Address : {ip}\n"
    "\n🔁 Please re-enter your password to confirm...\n"
)
port_config_success = "\n✅ Password confirmed successfully!\n"
port_config_mismatch = "\n❌ Passwords do not match or are empty. Attempts left: {attempts_left}\n"
port_config_fail = "🚫 Maximum attempts reached. Authentication failed.\n"


# --------------------------------------------------------------------------------------------------
#                              Constant : dut_ports_config.py   (END)
# --------------------------------------------------------------------------------------------------




# --------------------------------------------------------------------------------------------------
#                              Constant : COMMON METHOD ( START ) 
# --------------------------------------------------------------------------------------------------



class CommonMethodExecution:

    def run_command(self, command, description="", check_output=False):
        """
        Executes a shell command.

        Args:
            command (list): Command and arguments as a list.
            description (str): Description for logging.
            check_output (bool): If True, returns command output.

        Returns:
            tuple: (success: bool, output: str)
        """
        try:
            print(f"\n🔧 Executing: {description}")
            if check_output:
                result = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
                return True, result
            else:
                subprocess.run(command, check=True)
                return True, ""
        except subprocess.CalledProcessError as e:
            print(f"❌ Error during '{description}': {e}")
            return False, str(e)
    









# Common Setup Check 

class CommonSetupCheck:

    @staticmethod
    def handle_exceptions(func):
        """
        Decorator to handle exceptions and print traceback for debugging.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"❌ Exception in '{func.__name__}': {e}")
                traceback.print_exc()
                return traceback.print_exc()
        return wrapper
    
    @staticmethod
    def check_os(self):
        """
        Retrieve operating system details and return them in a structured format.
        Returns:
            dict: A dictionary containing:
                - os_name (str): Linux distro name (e.g., Ubuntu, RHEL, openEuler) or generic OS name
                - version (str): OS version string
                - release (str): OS release information
                - detailed_info (str): Additional details from os.uname() if available
        """
        import os
        import platform
        try:
            print("\n🔍 Checking Operating System Info...\n")
            # Default values using platform
            os_name = platform.system()       # e.g., 'Linux', 'Windows'
            os_version = platform.version()   # Detailed version info
            os_release = platform.release()   # Release number
            detailed_info = None
            # Method 2: Using os.uname() (Linux/Unix only)
            if hasattr(os, "uname"):
                detailed_info = str(os.uname())
            # Method 3: Check /etc/os-release for Linux distro details
            distro_name = None
            distro_version = None
            if os_name.lower() == "linux" and os.path.exists("/etc/os-release"):
                with open("/etc/os-release") as f:
                    data = f.read()
                    for line in data.splitlines():
                        if line.startswith("NAME="):
                            distro_name = line.split("=")[1].strip('"')
                        if line.startswith("VERSION_ID="):
                            distro_version = line.split("=")[1].strip('"')
                # Override os_name with distro name if found
                if distro_name:
                    os_name = distro_name
                if distro_version:
                    os_version = distro_version
            # Print details for user visibility
            print(f"🖥️ OS Name: {os_name}")
            print(f"📦 Version: {os_version}")
            print(f"📤 Release: {os_release}")
            if detailed_info:
                print(f"🧾 Detailed Info: {detailed_info}")
            return {
                "os_name": os_name,
                "version": os_version,
                "release": os_release,
                "detailed_info": detailed_info
            }

        except Exception as x:
            print("UNABLE TO FETCH OS VERSION AND ALL THINGS")
            return {
                "os_name": "LINUX",
                "version": None,
                "release": None,
                "detailed_info": None
            }

    # For Adding Separator
    @staticmethod   
    def print_separator(self,val=""):
        print("\n\n" + "-" * 50 +str(val)+ "-"*50 + "\n\n")
        



