import re
import time
from common_script_container.constant import CommonMethodExecution


class InterfaceManager:
    """
    A class to manage network interfaces using Linux 'ip' commands.
    Provides functionality to check interface status and bring DOWN interfaces UP.
    """

    def __init__(self,log_error = []):
        self.interFaceDetails = []


    def interface_details(self,search=""):
        """
        Fetches interface names and their status (UP/DOWN),
        excluding interfaces that have IPv4 addresses assigned.

        Args:
            search (str): Optional filter for specific interface name.

        Returns:
            list: List of dictionaries with interface name and status.
        """
        success, output = CommonMethodExecution.run_command(["ip", "-br", "a"], "Checking Interface Status", check_output=True)
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
            time.sleep(4)
            print(f"\n🔌 Before: Interface {interface} is {status}")
            success, _ = CommonMethodExecution.run_command(['ip', 'link', 'set', interface, 'up'], f"Bringing up {interface}")
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



# class PairingManagerInfo:
