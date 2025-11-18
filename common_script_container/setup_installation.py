import os
import re
import subprocess
import traceback
from datetime import datetime
from common_script_container.constant import CommonMethodExecution,CommonSetupCheck


class FirmwareDriverInstallation(CommonMethodExecution):
    
    @staticmethod
    def firmware_update(firmware_file_path):
        error_logs = []
        # Setup File-Location container
        print("checked")
        try:
            CommonSetupCheck.print_separator("CHECKING EXECUTINN STAARTED")
            if os.path.exists(firmware_file_path) == False:
                error_logs.append("❗ Invalid firmware path.")
                return False, error_logs
            os.chdir("/root")
            CommonSetupCheck.print_separator(str(os.getcwd()))
            os.makedirs("setup_firmware_driver",exist_ok=True)
            os.chdir("setup_firmware_driver")

            current_path = os.getcwdb().decode()
            firmware_file_name_before_taring = os.path.basename(firmware_file_path)
            # Extract firmware 
            FirmwareDriverInstallation.run_command(['tar', '-xvf',firmware_file_path, '-C', current_path],f"Extracting firmware file: {firmware_file_path}")

            # List files in current directory
            FirmwareDriverInstallation.run_command(['ls','-l'], "Listing files in current directory")

            # Fecthning Firmware Name :
            
            firmware_name = (firmware_file_name_before_taring).split(".")[0]
            # Updating FileName
            for file in os.listdir():
                if (firmware_name in file) and (firmware_file_name_before_taring != file):
                    firmware_name = file
            
            os.chdir(firmware_name)
            CommonSetupCheck.print_separator(str(os.getcwd()))
            




        except FileNotFoundError as e:
            error_msg = f"❌ File not found: {str(e)}"
            print(error_msg)
            return False, error_msg
        except subprocess.CalledProcessError as e:
            error_msg = f"❌ Subprocess error: {e.output if e.output else str(e)}"
            error_logs({
                "errors": error_msg,
                "traceback": traceback.format_exc()
            })
            print(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            error_logs({
                "errors": error_msg,
                "traceback": traceback.format_exc()
            })
            print(error_msg)
            return False, error_msg







class AutomationScriptForSetupInstalltion(CommonMethodExecution):

    def __init__(self,firmware_file_path = None, driver_path = None, git_user = "",git_token = "", operating_system_deatils={} ):
        self.firmware_file_path = firmware_file_path
        self.driver_path =  driver_path

        # Github Credential integration username and token with url for verfication \ Authentication
        self.dts_url = f"https://{git_user}:{git_token}@github.com/intel-sandbox/networking.dataplane.dpdk.dts.local.upstream.git".replace(" ","")
        self.dpdk_url = "https://github.com/DPDK/dpdk.git"
        self.error_logs = []
        self.error_logs_cmd = []

        self.operating_system_deatils = operating_system_deatils


    
    def creating_folder_setup(self,setup_file_name= "setup_firmware_driver"):

        """
        Creates a setup directory for firmware and driver extraction.
        Changes working directory to the newly created folder.
        """
        print("📁 Creating folder for firmware and driver setup if it doesn't exist...")
        os.makedirs(setup_file_name, exist_ok=True)
        os.chdir(setup_file_name)
        setup_file_path = os.getcwdb().decode()
        return setup_file_path
    


    # #############################   Updating firmware -:  ###################################################################
            
    def updating_firmware_drivers(self):

        """
        Validates paths and extracts firmware and driver tar files.
        Navigates into extracted directories and runs firmware installation.

        Parameters:
        - firmware_file_path (str): Path to the firmware tar.gz file.
        - driver_path (str): Path to the driver tar.gz file.
        """
        if not self.firmware_file_path or not self.driver_path:
            raise Exception("❗ Please provide both firmware and driver file paths.")

        # Validate file paths
        errors = []
        if not os.path.exists(self.firmware_file_path):
            errors.append("❗ Invalid firmware path.")
        if not os.path.exists(self.driver_path):
            errors.append("❗ Invalid driver path.")
        if errors:
            raise Exception("\n".join(errors))
        
        installation_firmware = False
        installation_driver = False

        # Setup File-Location container
        setup_file_path = self.creating_folder_setup()
        current_path = os.getcwd()
        print(f"\n📍 Current working directory: {current_path}\n")

        # Extract firmware 
        self.run_command(['tar', '-xvf', self.firmware_file_path, '-C', current_path],
                    f"Extracting firmware file: {self.firmware_file_path}")
        
        # Extrating driver 
        self.run_command(['tar', '-xvf', self.driver_path, '-C', current_path],
                    f"Extracting driver file: {self.driver_path}")

        # List files in current directory
        success, output = self.run_command(['ls'], "Listing files in current directory", check_output=True)
        if not success:
            print("⚠️ Failed to list files.")
            

        # Attempt to find firmware folder and navigate into it
        firmware_name = self.firmware_file_path.split("/")[-1].split("_")[0]
        if firmware_name in output:
            try:
                os.chdir(firmware_name)
                success, output = self.run_command(['ls', '-p'], "Listing contents of firmware directory", check_output=True)
                if success:
                    # Find first folder (lines ending with '/')
                    folders = [line for line in output.splitlines() if line.endswith('/')]
                    if folders:
                        os.chdir(folders[0].rstrip('/'))
                        installation_driver = True
                        self.run_command(['./nvmupdate64e'], "Running firmware installation")
                        
                    else:
                        print("⚠️ No subdirectory found to enter.")
                else:
                    print("⚠️ Failed to list contents of firmware directory.")
            except Exception as e:
                print("❌ Error navigating firmware directory:", e)
                self.error_logs.append(["❌ Error navigating firmware directory:", e])
        else:
            print(f"⚠️ Firmware folder '{firmware_name}' not found in extracted contents.")


        # Attempting to install driver :
        
        # Changing the directory root setup directory
        os.chdir(setup_file_path)
        success, output = self.run_command(['ls','-l'], "Listing files in current directory", check_output=True)
        # Fetching current driver data 
        if not success:
            print("⚠️ Failed to list files.")
        output = re.findall(r'^d[\w-]+\s+\d+\s+\w+\s+\w+\s+\d+\s+\w+\s+\d+\s+[\d:]+\s+(.+)$', output, re.MULTILINE)

        # Attempt to find driver folder and navigate into it
        driver_name = self.driver_path.split("/")[-1].split("_")[0].split(".")[0] 
        
        for folder_name in output:
            if driver_name in folder_name:
                os.chdir(folder_name)
                try:
                    # Installing Make cmd 
                    self.run_command(["apt", "update"], "updating Sudo Update :\n")
                    self.run_command(['apt','install','-y','make'], "Instalation Of Make cmd")

                    os.chdir("src")
                    # Run make commands
                    
                    self.run_command(['make'], "Running make")
                    self.run_command(['dmesg', '-c'], "Clearing dmesg")
                    self.run_command(['make', 'install'], "Running make install")
                    self.run_command(['rmmod', 'irdma'], "Removing irdma module")
                    self.run_command(['rmmod', 'ice'], "Removing ice module")
                    self.run_command(['modprobe', 'ice'], "Loading ice module")

                    installation_driver= True
                except Exception as x:
                    print("❌ Failed Error:", x)
                    self.error_logs.append(["❌ Failed Error:", x])
                # Breaking loop driver is updated .
                break
        
        # Assuming installation_driver and installation_firmware are boolean values
        driver_status = "✅" if installation_driver else "❌"
        firmware_status = "✅" if installation_firmware else "❌"
        print("\n\nInstallation Driver Status: {} | Firmware Status: {}\n\n".format(driver_status, firmware_status))



    # ###################################   Dpdk and Dts Setup Script       ##################################################################



    def clone_dts_repo(self):

        """
        Clones the private DTS repository using GitHub credentials.
        """
       
        path = os.getcwd()
        print("\n📍current path : "+str(path))
        self.run_command(["git", "clone", self.dts_url], "Cloning DTS repository")
        os.chdir("networking.dataplane.dpdk.dts.local.upstream")
        os.chdir("dep")
        
    def clone_dpdk_repo(self):

        """
        Clones the public DPDK repository and checks out a specific version.
        """
        self.run_command(["git", "clone", self.dpdk_url], "Cloning DPDK repository")

        self.run_command(["tar", "-czvf", "dpdk.tar.gz", "dpdk/"],"taring dpdk file")
        path = os.getcwd()
        print("\n📍current path : "+str(path))
        os.chdir("dpdk")
        self.run_command(["git", "checkout","-b", "v25.03-rc3"], "Checking out DPDK version v25.03-rc3")


    def install_required_packages(self):

        """
        Installs required system and Python packages for DPDK and DTS setup.
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        os_name = self.operating_system_deatils.get("os_name","LINUX").strip().lower()
        installer_name = "apt"

        if os_name == "openeuler":
            installer_name = "yum"
        apt_packages = [
            ["sudo", "timedatectl", "set-ntp", "false"],
            ["sudo", "timedatectl", "set-time", current_time],
            ["sudo", "timedatectl", "set-ntp", "true"],
            [installer_name, "update"],
            [installer_name, "install", "-y", "gcc"],
            [installer_name, "install", "-y", "build-essential"],
            [installer_name, "install", "-y", "meson"],
            [installer_name, "install", "-y", "ninja-build"],
            [installer_name, "install", "-y", "libnuma-dev"],
            [installer_name, "install", "-y", "python3-pip"],
            [installer_name, "install", "-y", "libpcap-dev"],
            [installer_name, "install", "-y", "libboost-all-dev"],
            [installer_name, "install", "-y", "libudev-dev"],
            [installer_name, "install", "-y", "libnl-3-dev"],
            [installer_name, "install", "-y", "libnl-genl-3-dev"],
            [installer_name, "install", "-y", "nasm"],
            [installer_name, "install", "-y", "yasm"],
            [installer_name, "install", "-y", "python3-scapy"],
            [installer_name, "install", "-y", "pkg-config"],
            [installer_name, "install", "-y", "lldpad"]
        ]

        pip_packages = [
            ["pip3", "install", "xlrd", "--break-system-packages"],
            ["pip3", "install", "xlwt", "--break-system-packages"],
            ["pip3", "install", "pexpect==4.7.0", "--break-system-packages"],
            ["pip3", "install", "pyelftools", "--break-system-packages"],

        ]

        for pkg in apt_packages:
            self.run_command(pkg, f"Installing {' '.join(pkg[3:]) if len(pkg) > 3 else pkg[1]}")

        for pkg in pip_packages:
            self.run_command(pkg, f"Installing Python package {pkg[2]}")

