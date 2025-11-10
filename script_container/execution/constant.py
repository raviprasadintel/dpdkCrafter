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
#                              Constant : COMMON FUNCTION ( START ) 
# --------------------------------------------------------------------------------------------------



class CommonFuntion:



    def check_os(self):
        """
        Retrieve operating system details and return them in a structured format.

        Returns:
            dict: A dictionary containing:
                - os_name (str): Name of the operating system (e.g., Linux, Windows)
                - version (str): OS version string
                - release (str): OS release information
                - detailed_info (str): Additional details from os.uname() if available
        """
        print("\n🔍 Checking Operating System Info...\n")

        # Method 1: Using platform module
        os_name = platform.system()       # e.g., 'Linux', 'Windows'
        os_version = platform.version()   # Detailed version info
        os_release = platform.release()   # Release number

        # Method 2: Using os.uname() (Linux/Unix only)
        detailed_info = None
        if hasattr(os, "uname"):
            detailed_info = str(os.uname())  # Convert uname object to string

        # Print details for user visibility
        print(f"🖥️ OS Name: {os_name}")
        print(f"📦 Version: {os_version}")
        print(f"📤 Release: {os_release}")
        if detailed_info:
            print(f"🧾 Detailed Info: {detailed_info}")

        # Return structured data
        return {
            "os_name": os_name,
            "version": os_version,
            "release": os_release,
            "detailed_info": detailed_info
        }

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
    
    def print_separator(self,val=""):
        
        print("\n\n" + "-" * 50 +str(val)+ "-"*50 + "\n\n")





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
            return None
    return wrapper

# For printing SEPARATOR
print_separator = lambda : print("\n\n\n\n" + "-" * 100 + "\n\n\n\n")