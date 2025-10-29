import re
import os
import time
import traceback
from script_container.execution.constant import CommonFuntion, handle_exceptions


class ExecutionCfgUpdate(CommonFuntion):
    """
    Handles reading, updating, and writing to the DTS execution configuration file.
    """

    def __init__(self, dts_path):
        """
        Initializes the ExecutionCfgUpdate class by setting the working directory and preparing the execution.cfg file.

        Args:
            dts_path (str): Path to the DTS directory.
        """
        try:
            path = dts_path.strip() + "/networking.dataplane.dpdk.dts.local.upstream"
            os.chdir(path)
            self.file_name = "execution.cfg"
            self.run_command(["chmod", "777", self.file_name], "Giving File Read Write Access")
            self.execution_data = self.read_file_data()
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            traceback.print_exc()
    
    @handle_exceptions
    def read_file_data(self):
        """
        Reads and returns the contents of the execution.cfg file.

        Returns:
            str: Contents of the file as a string, or error message if reading fails.
        """
        try:
            with open(self.file_name, 'r', encoding='utf-8') as file:
                data = file.read()
            return data
        except FileNotFoundError:
            print("❌ Error: File not found.")
            traceback.print_exc()
            return ""
        except IOError as e:
            print(f"❌ Error reading file: {e}")
            traceback.print_exc()
            return ""
        
    @handle_exceptions
    def write_crbs_config(self, pair_text):
        """
        Deletes the existing execution.cfg file and writes a new one with the provided CRB configuration.

        Args:
            pair_text (str): Text content to write into the execution.cfg file.
        """
        try:
            self.run_command(["pwd"], "Fetching Current Path")
            print("\n" + "-" * 100 + "\n")

            if os.path.exists(self.file_name):
                self.run_command(["chmod", "777", self.file_name], "Setting file access permissions")
                time.sleep(1)
                self.run_command(["rm", "-rf", self.file_name], f"Deleting existing file: {self.file_name}")

            with open(self.file_name, "w", encoding='utf-8') as f:
                f.write(pair_text)

            print(f"✅ File '{self.file_name}' has been created with the provided port configuration.")
        except Exception as e:
            print(f"❌ Error writing CRB config: {e}")
            traceback.print_exc()

    @handle_exceptions
    def update_execution_content(self, ip_address):
        """
        Updates the execution.cfg content by:
        - Filtering the 'test_suites' block to retain only 'hello_world' entries.
        - Replacing the CRB IP placeholder with the provided IP address.

        Args:
            ip_address (str): IP address to insert into the configuration.
        """
        try:
            file_data = self.execution_data

            for val in file_data.splitlines():
                print(val)

            print("execution .cfg",file_data)

            if not file_data:
                print("❌ No execution data available to update.")
                return

            # Match 'test_suites=' followed by any non-empty indented lines ending with a comma
            pattern = r'test_suites=\n(?:\s*\S+,\n?)+'
            match = re.search(pattern, file_data)

            if not match:
                print("⚠️ No 'test_suites' block found.")
                return

            block = match.group()
            lines = block.strip().splitlines()
            filtered = [line for line in lines if "hello_world" in line]

            cleaned_block = "test_suites=\n" + "\n".join(filtered)+"\n"

            # Replace the test_suites block
            updated_data = re.sub(pattern, cleaned_block, file_data)

            # Replace CRB IP placeholder
            updated_data = re.sub(r"crbs=&lt;CRB IP Address&gt;.*", f"crbs={ip_address}", updated_data)

            self.write_crbs_config(updated_data)
        except Exception as e:
            print(f"❌ Error while updating execution content: {e}")
            traceback.print_exc()
