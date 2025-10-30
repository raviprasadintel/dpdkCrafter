import os
import platform
import subprocess
import traceback
from functools import wraps
# --------------------------------------------------------------------------------------------------
#                              Constant : COMMON FUNCTION ( START ) 
# --------------------------------------------------------------------------------------------------



class CommonClassExecution:


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

def check_os():
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


# For printing SEPARATOR
print_separator = lambda: print("\n\n\n\n" + "-" * 100 + "\n\n\n\n")