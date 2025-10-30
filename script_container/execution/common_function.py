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

# For printing SEPARATOR
print_separator = lambda: print("\n\n\n\n" + "-" * 100 + "\n\n\n\n")