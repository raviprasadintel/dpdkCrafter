import re
import os
import time
from script_container.execution.constant import CommonFuntion


class ExecutionCfgUpdate(CommonFuntion):

    def __init__(self,dts_path):
        path = dts_path.strip() + "/networking.dataplane.dpdk.dts.local.upstream"
        os.chdir(path)
        file_name = "execution.cfg"
        self.file_name = file_name
        
        self.run_command(["chmod","777", file_name],"Giving File Read Write Access")
    

    def read_file_data(self):
        """
        Reads and returns the contents of a file.

        Parameters:
        file_path (str): The path to the file to be read.

        Returns:
        str: Contents of the file as a string.
        """
        try:
            
            with open(self.file_name, 'r', encoding='utf-8') as file:
                data = file.read()
            self.crbs_data = data
        except FileNotFoundError:
            self.crbs_data = "Error: File not found."
        except IOError as e:
            self.crbs_data =  f"Error reading file: {e}"

    def write_crbs_config(self,pair_text, file_name="crbs.cfg"):
        # 📁 Step 4: Navigate to the configuration directory
        
        self.run_command(["pwd"],"Fecthing Current Path\n")
        
        # Adding line break 
        print("\n--------------------------------------------------------------------------------------------------\n")

        if os.path.exists(file_name):
            self.run_command(["chmod","777",file_name],"giving a file access for READ, WRITE and DELETE")
            time.sleep(1)
            self.run_command(["rm","-rf",file_name],f"Deleting existing File name  :=> {file_name}")
        

        # Creating crbs.cfg File

        with open(file_name, "w") as f:
            f.write(pair_text)
        print(f"✅ File '{file_name}' has been created with the provided port configuration.")


    
    def UpdatingExecutionContent(self):

        pass

