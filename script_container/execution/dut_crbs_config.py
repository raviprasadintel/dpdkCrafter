import re
import os
import time
from script_container.execution.constant import CommonFuntion



class DutCrbsConfig(CommonFuntion):

    def __init__(self,dts_path):
        path = dts_path.strip() + "/networking.dataplane.dpdk.dts.local.upstream/conf"
        os.chdir(path)
        self.filter_crbs_data = self.read_file_data() # Filter crbs data to be updated 

    def read_file_data(self,file_path="crbs.cfg"):
        """
        Reads and returns the contents of a file.

        Parameters:
        file_path (str): The path to the file to be read.

        Returns:
        str: Contents of the file as a string.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = file.read()
            self.crbs_data = data
        except FileNotFoundError:
            self.crbs_data = "Error: File not found."
        except IOError as e:
            self.crbs_data =  f"Error reading file: {e}"
        
    def updating_crbs_file(self, dut_ip = "", dut_user = "", dut_passwd = "", tester_ip = "",tester_passwd = ""):
        """
        Extract and update the first DUT block from crbs_data.
        All other DUT blocks are ignored. Updates username and password if provided.
        """

        crbs_data =self.crbs_data  if self.crbs_data  else "Ravi Prasad"
        filter_crbs_data = ""
        filter_status = 0

        # 🔍 Step 1: Iterate through lines to find the first DUT block
        for line in crbs_data.splitlines():
            # Match either [DUT IPx] or [IPv4]
            matches = re.findall(r"\[DUT IP\d+\]|\[\d{1,3}(?:\.\d{1,3}){3}\]", line)
            if matches:
                filter_status += 1
               
            if filter_status > 1:
                # Stop collecting after the first DUT block ends
                break
            filter_crbs_data += (line+"\n")

        # 🛠️ Step 2: Update fields if username and password are provided
        if dut_user:
            filter_crbs_data = re.sub(r"dut_user=.*", f"dut_user={dut_user}", filter_crbs_data)
        if dut_ip:
            filter_crbs_data = re.sub(r"[DUT IP1].*", f"[{dut_user}]", filter_crbs_data)
            filter_crbs_data = re.sub(r"dut_ip=.*",f"dut_ip={dut_ip}",filter_crbs_data)
        if dut_passwd:
            filter_crbs_data = re.sub(r"dut_passwd=.*", f"dut_passwd={dut_passwd}", filter_crbs_data)
        if tester_passwd:
            filter_crbs_data = re.sub(r"tester_passwd=.*", f"tester_passwd={tester_passwd}", filter_crbs_data)
        if tester_ip:
            filter_crbs_data = re.sub(r"tester_ip=.*",f"tester_ip={tester_ip}", filter_crbs_data)
        # 📄 Step 3: Display the updated block
        print("📝 Updated DUT Configuration Block:\n")
        for line in filter_crbs_data.splitlines():
            print(line)

        # 😴 Step 5: Pause briefly to allow user to verify
        print("\n\n😴 Sleeping for 3 seconds to allow verification of the updated configuration...\n")
        time.sleep(3)
        # ✅ Step 6: Resume process
        print("✅ Awake and starting interface pairing check!\n")
        
        self.write_crbs_config(filter_crbs_data)

    
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




# --------------------------------------------------------------------------------------------------


