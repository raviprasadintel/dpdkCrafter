import re
import time
from common_script_container.constant import CommonSetupCheck
from common_script_container.constant import CommonMethodExecution




class InterfaceManager:
    """
    A class to manage network interfaces using Linux 'ip' commands.
    Provides functionality to check interface status and bring DOWN interfaces UP.
    """

    def __init__(self,error_logs = []):
        self.interFaceDetails = []
        self.error_logs = error_logs


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

    # def process_all_interfaces(self):
    #     """
    #     Checks all interfaces and brings any DOWN interfaces UP.
    #     Stores only UP interfaces in self.interFaceDetails.
    #     """

    #     print("\n🔄 Processing all interfaces...")
    #     for interface_det in self.interface_details():
    #         print(interface_det)
    #         self.bring_interface_up(interface_det)
    #         print("self.interface_details() :",self.interface_details(search=interface_det['name']) )

    #     self.interFaceDetails = [val for val in self.interface_details() if val['status'].upper() == "UP"]
    #     print(f"\n📋 Final UP Interfaces: {self.interFaceDetails}")

    def process_all_interfaces(self):
        """
        Checks all interfaces and brings any DOWN interfaces UP.
        Maintains two lists:
        - UP interfaces in self.interFaceDetails
        - DOWN interfaces in a separate list for reporting
        """
        print("\n🔄 Processing all interfaces...\n")
        down_interfaces = []  # Track interfaces that remain DOWN
        up_interfaces = []    # Track interfaces that are UP after processing
        try:
            all_interfaces = self.interface_details()
            if not all_interfaces:
                print("❌ No interfaces found!")
                return

            for interface_det in all_interfaces:
                try:
                    name = interface_det['name']
                    status = interface_det['status']

                    print(f"➡️ Checking Interface: {name} | Current Status: {status}")

                    # Attempt to bring interface UP if it's DOWN
                    if status.upper() == "DOWN":
                        print(f"🔌 Attempting to bring UP: {name}")
                        self.bring_interface_up(interface_det)

                        # Check updated status
                        updated_status = self.interface_details(search=name)
                        if updated_status and updated_status[0]['status'].upper() == "UP":
                            print(f"✅ SUCCESS: {name} is now UP")
                            up_interfaces.append(name)
                        else:
                            print(f"❌ FAILED: {name} is still DOWN")
                            down_interfaces.append(name)
                    else:
                        print(f"✅ Already UP: {name}")
                        up_interfaces.append(name)
                except Exception as e:
                    self.error_logs.append(f"❌ Unexpected error: {str(e)}")

            # Update class attribute with UP interfaces
            self.interFaceDetails = [{'name': iface, 'status': 'UP'} for iface in up_interfaces]

            # Print summary
            print("\n📋 Interface Summary:")
            print(f"✅ UP Interfaces ({len(up_interfaces)}): {up_interfaces}")
            print(f"❌ DOWN Interfaces ({len(down_interfaces)}): {down_interfaces}")
            CommonSetupCheck.print_separator()
        except Exception as e:
            self.error_logs.append(f"❌ Unexpected error: {str(e)}")
            
        return {
            "updated": True if len(up_interfaces)>1 else False,
            "status":"SUCCESSFUL" if len(up_interfaces)>1 else"FAILURE",
            "up_interface": up_interfaces,
            "down_interface": down_interfaces,
            "error_logs": self.error_logs
        }


# class PairingManagerInfo:
