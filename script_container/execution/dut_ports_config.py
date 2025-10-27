import os
import re
import time
import socket
import platform
import subprocess

from script_container.execution.constant import (port_config_prompt_update, 
                      port_config_auth_prompt, port_config_auth_confirm,
                      port_config_success, port_config_fail, 
                      port_config_mismatch)

# Importing Common Method :
from dpdkCrafter.script_container.execution.constant import CommonFuntion


class DutPortConfig(CommonFuntion):
    def __init__(self,dts_path):
        self.dts_setup_path = dts_path 
        # Initialize configuration
        self.ip_address = self.get_ipv4_address()
        self.username = os.getlogin()
        self.password = "tester" #self.get_password()

    def get_ipv4_address(self):
        """
        Fetches the current IPv4 address of the system.

        Returns:
            str: The IPv4 address as a string, or None if not found.
        """
        try:
            # Create a socket and connect to an external host (Google DNS)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Doesn't actually send data
            ip_address = s.getsockname()[0]
            s.close()
            print(f"🌐 Current IPv4 Address: {ip_address}")
            return ip_address
        except Exception as e:
            print(f"❌ Error fetching IPv4 address: {e}")
            return None
        
    def get_password(self):
        """
        Prompt the user to enter and confirm their password for authentication.

        This method displays a formatted message including the username and IP address,
        then securely collects the password input twice. If the passwords do not match
        or are empty, the user is given up to 3 attempts to enter matching passwords.

        Returns:
            str: The confirmed password if matched within allowed attempts.
            None: If the user fails to provide matching passwords.
        """
        max_attempts = 3
        attempt = 0

        while attempt < max_attempts:
            # Prompt user for the initial password input
            password = input(port_config_auth_prompt.format(
                username=self.username, ip=self.ip_address))

            # Prompt user to re-enter the password for confirmation
            re_enter_password = input(port_config_auth_confirm.format(
                username=self.username, ip=self.ip_address))

            # Check if both passwords match and are not empty
            if password and password == re_enter_password:
                print(port_config_success)
                return password
            else:
                attempt += 1
                print(port_config_mismatch.format(attempts_left=max_attempts - attempt))

        print(port_config_fail)
        return None


    def write_ports_config(self,pair_text, file_name="ports.cfg"):
        """
        Write the given pair_text content to a configuration file.

        Args:
            pair_text (str): The formatted port configuration text.
            file_name (str): The name of the file to write to (default is 'ports.cfg').
        """
       
        
        # Removing Exiting file if File is available
        
        if os.path.exists(file_name):
            self.run_command(
            ["chmod", "777", file_name],
            f"\n\n🔧 Allowing READ, WRITE, and EXECUTE permissions for all users on ➡️ {file_name}"
            )
            self.run_command(
            ["rm", "-rf", file_name],
            f"\n\n🔧 Removing Existing file : ➡️ {file_name}"
            )

        with open(file_name, "w") as f:
            f.write(pair_text)
        print(f"✅ File '{file_name}' has been created with the provided port configuration.")


        # 🔐 Step 1: Set full permissions on the configuration file
        self.run_command(
            ["chmod", "777", file_name],
            f"\n\n🔧 Allowing READ, WRITE, and EXECUTE permissions for all users on ➡️ {file_name}"
        )

        # 🌐 Step 2: Retrieve brief interface details
        self.run_command(
            ["ip", "-br", "a"],
            "\n\n📡 Fetching brief interface details..."
        )

        # 🧠 Step 3: Get detailed network hardware info with bus mapping
        self.run_command(
            ["lshw", "-c", "network", "-businfo"],
            "\n\n🔍 Fetching detailed bus information for network interfaces..."
        )

        # 📄 Step 4: Display the updated configuration file for verification
        self.run_command(
            ["cat", file_name],
            "\n\n📑 Showing contents of the updated configuration file for double verification..."
        )

        # 😴 Step 5: Pause briefly to allow user to verify
        print("\n\n😴 Sleeping for 3 seconds to allow verification of the updated configuration...\n")
        time.sleep(3)

        # ✅ Step 6: Resume process
        print("✅ Awake and starting interface pairing check!\n")

        return file_name


    def update_ports(self, interfaceDetails):
        """
        Update the DUT port configuration file based on provided interface details.

        Args:
            interfaceDetails (dict): Dictionary containing mapped_pair data.
        """
        # 🧩 Step 1: Validate input
        if 'mapped_pair' not in interfaceDetails:
            print("⚠️ Ports info not found in the provided interface details.\n")
            return

        mapped_pair = interfaceDetails['mapped_pair']

        # 🛠️ Step 2: Generate port configuration lines
        pair_text = "\n".join([
            f"    pci={info['bus_info'][0]},peer={info['bus_info'][1]};"
            for info in mapped_pair
        ])

        # 🧾 Step 3: Format the full configuration text
        updated_text = port_config_prompt_update.format(self.ip_address, pair_text)

        # 📁 Step 4: Navigate to the configuration directory
        path = self.dts_setup_path.strip() + "networking.dataplane.dpdk.dts.local.upstream/conf"
        os.chdir(path)
       
        # 📍 Step 5: Confirm current working directory
        current_path = self.run_command(["pwd"], description="📂 Fetching current working directory", check_output=True)
        print(f"📍 Current Path: {current_path}\n")

        # 📝 Step 6: Write the configuration to file
        file_name = self.write_ports_config(updated_text)

        # 📦 Step 7: Set file permissions
        self.run_command(["chmod", "777", file_name], f"🔧 Setting full permissions on ➡️ {file_name}")

        # 🌐 Step 8: Get network interface details
        self.run_command(["ip", "-br", "a"], "📡 Retrieving network interface details")

        # 🧠 Step 9: Fetch bus information
        self.run_command(["lshw", "-c", "network", "-businfo"], "🔍 Fetching bus information for network interfaces")

        # 📄 Step 10: Display the updated configuration file
        self.run_command(["cat", file_name], "📑 Displaying updated configuration file for verification")

        # 😴 Step 11: Pause for verification
        print("😴 Sleeping for 3 seconds to allow verification...\n")
        time.sleep(3)

        # ✅ Step 12: Resume process
        print("✅ Awake and starting interface pairing check!\n")
# --------------------------------------------------------------------------------------------------

# if __name__ == "__main__":
   
#     print("Starting -> Port Updating Process")
#     dts_path = "/root/testing/dts_setup/"
#     ports_config_obj = DutPortConfig(dts_path)
    
#     # Display the loaded configuration details

#     # Example Showing Interface Deatails    
#     interfaceDetails = {   'bus_info': [{'bus': 'pci@0000:17:00.0', 'device': 'ens260f0np0', 'description': 'Ethernet Controller X710 for 10GBASE-T'}, 
#                   {'bus': 'pci@0000:17:00.1', 'device': 'ens260f1np1', 'description': 'Ethernet Controller X710 for 10GBASE-T'}, 
#                   {'bus': 'pci@0000:31:00.0', 'device': 'ens786f0', 'description': 'I350 Gigabit Network Connection'}, 
#                   {'bus': 'pci@0000:31:00.1', 'device': 'ens786f1', 'description': 'I350 Gigabit Network Connection'}, 
#                   {'bus': 'pci@0000:31:00.2', 'device': 'ens786f2', 'description': 'I350 Gigabit Network Connection'}, 
#                   {'bus': 'pci@0000:31:00.3', 'device': 'ens786f3', 'description': 'I350 Gigabit Network Connection'}, 
#                   {'bus': 'pci@0000:4b:00.0', 'device': 'ens785f0np0', 'description': 'Ethernet Controller E810-C for QSFP'}, 
#                   {'bus': 'pci@0000:4b:00.1', 'device': 'ens785f1np1', 'description': 'Ethernet Controller E810-C for QSFP'}, 
#                   {'bus': 'pci@0000:b1:00.0', 'device': 'ens801f0np0', 'description': 'Ethernet Controller E810-C for QSFP'}, 
#                   {'bus': 'pci@0000:b1:00.1', 'device': 'ens801f1np1', 'description': 'Ethernet Controller E810-C for QSFP'}, 
#                   {'bus': 'pci@0000:ca:00.0', 'device': 'ens802f0np0', 'description': 'Ethernet Controller E810-C for QSFP'}, 
#                   {'bus': 'pci@0000:ca:00.1', 'device': 'ens802f1np1', 'description': 'Ethernet Controller E810-C for QSFP'}],
#         'interface_connection': [['ens802f0np0', 'ens801f0np0'], ['ens802f1np1', 'ens801f1np1']], 
#         'mapped_pair': [{'interface': ['ens802f0np0', 'ens801f0np0'], 'bus_info': ['0000:ca:00.0', '0000:b1:00.0']}, 
#                         {'interface': ['ens802f1np1', 'ens801f1np1'], 'bus_info': ['0000:ca:00.1', '0000:b1:00.1']}]
#     }

#     print(
#         "\n🔧 Loaded Configuration:\n"
#         "-----------------------------\n"
#         f"🌐 IP Address : {ports_config_obj.ip_address}\n"
#         f"👤 Username   : {ports_config_obj.username}\n"
#         f"🔑 Password   : {'*' * len(ports_config_obj.password) if ports_config_obj.password else 'Not Set'}\n"
#     )


#     ports_config_obj.update_ports(interfaceDetails)


