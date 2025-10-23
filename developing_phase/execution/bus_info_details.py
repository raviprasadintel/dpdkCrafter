import re
import os
import time
import subprocess
import platform



def check_os():
    """
    Checks and prints operating system details using platform and os.uname (if available).
    """
    print("\n🔍 Checking Operating System Info...\n")

    # Method 1: Using platform
    os_name = platform.system()
    os_version = platform.version()
    os_release = platform.release()
    print(f"🖥️ OS Name: {os_name}")
    print(f"📦 Version: {os_version}")
    print(f"📤 Release: {os_release}")

    # Method 2: Using os.uname() (Linux/Unix only)
    if hasattr(os, "uname"):
        uname_info = os.uname()
        print(f"🧾 Detailed Info: {uname_info}")

# --------------------------------------------------------------------------------------------------

class InterfaceManager:
    """
    A class to manage network interfaces using Linux 'ip' commands.
    Provides functionality to check interface status and bring DOWN interfaces UP.
    """

    def __init__(self):
        self.interFaceDetails = []

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
        

    def interface_details(self,search=""):
        """
        Fetches interface names and their status (UP/DOWN),
        excluding interfaces that have IPv4 addresses assigned.

        Args:
            search (str): Optional filter for specific interface name.

        Returns:
            list: List of dictionaries with interface name and status.
        """
        success, output = self.run_command(["ip", "-br", "a"], "Checking Interface Status", check_output=True)
        if not success:
            return []

        interface_status = []
        for line in output.splitlines():
            match = re.match(r'^(\S+)\s+(UP|DOWN)(?:\s+(.*))?$', line)
            if not match:
                continue  # Skip lines that don't match the expected format

            name, status, ip_info = match.groups()
            ip_info = ip_info.strip() if ip_info else ""

            # Skip if IPv4 is present
            if re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}/\d+\b', ip_info):
                continue

            interface_status.append({'name': name, 'status': status})

        # Filter by search term if provided
        return [iface for iface in interface_status if search in iface['name']] if search else interface_status
    
    def bring_interface_up(self, interface_det):
        """
        Brings a DOWN interface UP.

        Args:
            interface_det (dict): Dictionary with 'name' and 'status' of the interface.
        """
        interface = interface_det['name']
        status = interface_det['status']

        if status.lower() == "down":
            print(f"\n🔌 Before: Interface {interface} is {status}")
            success, _ = self.run_command(['ip', 'link', 'set', interface, 'up'], f"Bringing up {interface}")
            if success:
                updated_status = self.interface_details(search=interface)
                print(f"✅ After: Interface {interface} status ➡️ {updated_status}")
            else:
                print(f"❌ Failed to bring up interface {interface}")

    def process_all_interfaces(self):
        """
        Checks all interfaces and brings any DOWN interfaces UP.
        Stores only UP interfaces in self.interFaceDetails.
        """
        print("\n🔄 Processing all interfaces...")
        for interface_det in self.interface_details():
            self.bring_interface_up(interface_det)

        self.interFaceDetails = [val for val in self.interface_details() if val['status'].upper() == "UP"]
        print(f"\n📋 Final UP Interfaces: {self.interFaceDetails}")



# --------------------------------------------------------------------------------------------------

class PairingManagerInfo(InterfaceManager):
    """
    Extends InterfaceManager to include PCI bus and device pairing information
    for network interfaces using `lshw -c network -businfo`.
    Also includes logic to extract NIC link events and pair interfaces based on activity.
    """

    def __init__(self):
        super().__init__()
        self.bus_info = []
        self.pairingInterface = []
        self.mapped_bus_pairs = []

        # Fetch bus info on initialization
        try:
            self.busInfo()
        except Exception as e:
            print(f"❌ Error initializing bus info: {e}")

    def busInfo(self):
        """
        Fetches and parses PCI bus info for network interfaces.

        Returns:
            list: List of dictionaries with 'bus', 'device', 'description'.
        """
        print("\n🔍 Fetching PCI Bus Info...\n")
        try:
            success, output = self.run_command(['lshw', '-c', 'network', '-businfo'], "Fetching Bus Info", check_output=True)
            if not success:
                return []

            lines = output.strip().split('\n')[1:]  # Skip the header
            pattern = r'^(pci@\S+)\s+(\S+)\s+network\s+(.*)$'

            parsed_info = []
            for line in lines:
                match = re.match(pattern, line.strip())
                if match:
                    bus, device, description = match.groups()
                    parsed_info.append({
                        'bus': bus,
                        'device': device,
                        'description': description
                    })

            self.bus_info = parsed_info
            print(f"🧾 Bus Info Parsed:\n{self.bus_info}\n")
        except Exception as e:
            print(f"❌ Error parsing bus info: {e}")

    def fetchingInterFacePairingInfo(self):
        """
        Processes interfaces and prints pairing info with bus details.
        """
        print("\n🔗 Fetching Interface Pairing Info...\n")
        try:
            self.process_all_interfaces()
            interfaceDetails = self.interFaceDetails

            print(f"📡 Interface Details:\n{interfaceDetails}\n")
            print(f"🧬 Bus Info Details:\n{self.bus_info}\n")
        except Exception as e:
            print(f"❌ Error fetching interface pairing info: {e}")

    def extract_interface_names(self, log_data):
        """
        Extracts all network interface names from NIC link status messages.

        Args:
            log_data (str): The full dmesg output as a string.

        Returns:
            List[str]: A list of interface names (e.g., 'ens801f1np1').
        """
        try:
            pattern = r'\b(\w+): NIC Link is (?:Down|up)\b'
            return re.findall(pattern, log_data, re.MULTILINE)
        except Exception as e:
            print(f"❌ Error extracting interface names: {e}")
            return []

    def update_interface_pairs(self, interface_list, existing_pairs):
        """
        Creates non-repeating interface pairs from the input list.
        Only adds a pair if it doesn't already exist in either order.

        Args:
            interface_list (list): List of interface names.
            existing_pairs (list): List of existing pairs (each pair is a list of two interfaces).

        Returns:
            list: Updated list of valid interface pairs.
        """
        try:
            updated_pairs = existing_pairs.copy()
            for i in range(0, len(interface_list) - 1, 2):
                pair = [interface_list[i], interface_list[i + 1]]
                reverse_pair = [interface_list[i + 1], interface_list[i]]
                if pair not in updated_pairs and reverse_pair not in updated_pairs:
                    updated_pairs.append(pair)
            return updated_pairs
        except Exception as e:
            print(f"❌ Error updating interface pairs: {e}")
            return existing_pairs

    def fetchingPairDetailsFromInterface(self):
        """
        Processes all UP interfaces and attempts to fetch pairing details using `ethtool` and `dmesg`.
        Extracts interface names from NIC link messages and avoids redundant processing.
        Updates the pairingInterface list with interfaces that show link activity.
        """
        try:
            print("\n🧹 Clearing dmesg buffer before starting...\n")
            self.run_command(["dmesg", "-c"], "Clearing dmesg buffer")
            self.run_command(["dmesg", "-c"], "Clearing again for safety")

            print("😴 Sleeping for 3 seconds before starting NIC link checks...\n")
            time.sleep(3)
            print("✅ Awake and starting interface pairing check!\n")

            pairingInterface = []
            interFaceDetails = self.interFaceDetails

            for details in interFaceDetails:
                try:
                    interface = details['name']
                    status = details['status']

                    print(f"🔍 Processing Interface: {interface} | Status: {status}")

                    self.run_command(["ethtool", "-r", interface], f"Resetting {interface}")
                    success, output = self.run_command(["dmesg", "-c"], f"Checking NIC link for {interface}", check_output=True)

                    if success:
                        interface_pair = self.extract_interface_names(output)
                        pairingInterface = self.update_interface_pairs(interface_pair, pairingInterface)

                    print("😴 Sleeping for 2 seconds before next interface...\n")
                    time.sleep(2)
                    print("✅ Continuing to next interface...\n")
                    print("🧹 Clearing dmesg buffer...\n")
                except Exception as e:
                    print(f"❌ Error processing interface {details.get('name', 'unknown')}: {e}")

            # Final cleanup
            self.run_command(["dmesg", "-c"], "Clearing dmesg buffer after")
            self.run_command(["dmesg", "-c"], "Final clear")

            print("😴 Sleeping for 2 seconds before final output...\n")
            time.sleep(2)
            print("✅ Final pairing complete!\n")

            print("\n🔗 Final Interface Pairings:")
            self.pairingInterface = pairingInterface
            for pair in pairingInterface:
                print(f"  ✅ {pair[0]} ↔ {pair[1]}")
        except Exception as e:
            print(f"❌ Error in fetchingPairDetailsFromInterface: {e}")


    def mapInterfaceToBus(self):
        """
        Maps each interface pair to their corresponding PCI bus addresses using bus_info.

        Args:
            bus_info (list): List of dictionaries containing 'bus', 'device', and 'description'.

        Returns:
            list: List of dictionaries with 'interface' and 'bus_info' keys.
                Example: [{'interface': [...], 'bus_info': [...]}]
        """
        print("\n🔗 Starting interface-to-bus mapping...\n")

        interface_connection = self.pairingInterface  # Interface pairs to be mapped
        bus_info = self.bus_info  # PCI bus info list

        # Create a lookup dictionary for quick access to bus address by device name
        device_to_bus = {
            entry['device']: entry['bus'].replace('pci@', '') for entry in bus_info
        }

        mapped_pairs = []  # Final result list

        for pair in interface_connection:
            try:
                # Extract bus info for each interface in the pair
                bus_pair = [device_to_bus.get(iface, 'N/A') for iface in pair]

                # Append the mapping to the result list
                mapped_pairs.append({
                    'interface': pair,
                    'bus_info': bus_pair
                })

                # Print detailed mapping info
                print(f"✅ Mapped Pair:")
                print(f"   🔌 Interfaces : {pair}")
                print(f"   🧭 Bus Info   : {bus_pair}\n")

            except Exception as e:
                print(f"❌ Error mapping pair {pair}: {e}")

        print("🎯 Completed interface-to-bus mapping.\n\n")
        return {
            "bus_info": self.bus_info,
            "interface_connection": self.pairingInterface,
            "mapped_pair": mapped_pairs 
        }

# --------------------------------------------------------------------------------------------------

# #######################################   Main Execution Block   ###########################################################

if __name__ == "__main__":
    print("\n🚀 Starting Interface Pairing Manager...\n")

    try:
        # Initialize and run pairing manager
        print("🧩 Initializing PairingManagerInfo object...")
        obj = PairingManagerInfo()

        print("\n🔍 Fetching Interface and Bus Pairing Information...\n")
        obj.fetchingInterFacePairingInfo()

        print("\n🔗 Fetching Interface Connection Details...\n")
        obj.fetchingPairDetailsFromInterface()

        print("\nMapping Interface With Bus Info")
        interfaceDetails = obj.mapInterfaceToBus()

        print(interfaceDetails)

       
        # Display the loaded configuration details

     
    except Exception as e:
        print(f"\n❌ An error occurred during execution: {e}\n")

    print("\n✅ Script Execution Completed Successfully.\n")


