import os
import re
import subprocess
import traceback
from datetime import datetime
from common_script_container.constant import CommonMethodExecution,CommonSetupCheck




class FirmwareDriverInstallation:
    
    """
    FirmwareDriverInstallation

    This class provides methods to automate the installation and update process 
    for network drivers and firmware on Linux systems. It is designed to handle 
    tasks such as:

    - Extracting driver and firmware tar files.
    - Identifying the correct folder after extraction using best-match logic.
    - Running system commands to build and install drivers.
    - Executing firmware update utilities.

    Key Features:
    -------------
    - Uses `CommonMethodExecution.run_command()` for executing shell commands 
      with descriptive logging.
    - Provides detailed status updates with emojis for better terminal UX.
    - Handles errors gracefully and logs them for troubleshooting.

    Methods:
    --------
    - driver_update(driver_path, error_logs=[]):
        Installs the network driver from a tar file by extracting, building, 
        and loading kernel modules.

    - firmware_update(firmware_file_path, error_logs=[]):
        Updates firmware by extracting the tar file, navigating to the correct 
        directory, and running the firmware update tool.

    Usage:
    ------
    Example:
        installation_status, status, errors = FirmwareDriverInstallation.driver_update("/path/to/driver.tar.gz")
        firmware_status, status, errors = FirmwareDriverInstallation.firmware_update("/path/to/firmware.tar.gz")
    """

    @staticmethod
    def firmware_update(firmware_file_path, error_logs=[]):
        """
        Update firmware from a given tar file.

        Steps:
        1. Validate firmware path.
        2. Extract tar file into a working directory.
        3. Find the best matching folder after extraction.
        4. Navigate into firmware directory and run update command.
        
        Args:
            firmware_file_path (str): Path to the firmware tar file.
            error_logs (list): List to collect error messages.
        
        Returns:
            tuple: (installation_firmware: bool, status: str, error_logs: list)
        """
        installation_firmware = False
        status = "FAILED"
        error_msg = None

        try:
            CommonSetupCheck.print_separator("🚀 FIRMWARE UPDATE STARTED")

            # ✅ Validate firmware path
            if not os.path.exists(firmware_file_path):
                error_logs.append("❗ Invalid firmware path.")
                print("❌ Firmware path does not exist!")
                return False, status, error_logs

            # ✅ Prepare working directory
            os.chdir("/root")
            CommonSetupCheck.print_separator(f"📂 Current Directory: {os.getcwd()}")
            os.makedirs("setup_firmware_driver", exist_ok=True)
            os.chdir("setup_firmware_driver")

            current_path = os.getcwd()
            firmware_file_name_before_taring = os.path.basename(firmware_file_path)

            # ✅ Extract firmware tar file
            print(f"📦 Extracting firmware file: {firmware_file_path}")
            CommonMethodExecution.run_command(
                ['tar', '-xvf', firmware_file_path, '-C', current_path],
                f"Extracting firmware file: {firmware_file_path}"
            )

            # ✅ List files after extraction
            CommonMethodExecution.run_command(['ls', '-l'], "Listing files in current directory")

            # ✅ Find best matching folder after extraction
            finding_file = CommonMethodExecution.find_best_match(firmware_file_name_before_taring, os.listdir())
            CommonSetupCheck.print_separator("🔍 Firmware Folder With Highest Match Score")
            print(f"✅ Best Match: {finding_file.get('folder')} ({finding_file.get('score')}%)")

            firmware_name = finding_file.get("folder")
            print(f"📂 Extracted Folders: {os.listdir()}")
            print(f"➡️ Selected Firmware Folder: {firmware_name}")

            # ✅ Navigate into firmware directory
            os.chdir(firmware_name)
            CommonSetupCheck.print_separator(f"📂 Current Directory: {os.getcwd()}")

            # ✅ Navigate into inner folder if exists
            inner_folders = os.listdir()
            if inner_folders:
                os.chdir(inner_folders[0])
                CommonSetupCheck.print_separator(f"📂 Inner Directory: {os.getcwd()}")
                print(f"📂 Contents: {os.listdir()}")

            # ✅ Run firmware update command
            print("⚙️ Running firmware update...")
            CommonMethodExecution.run_command(['./nvmupdate64e'], "Executing firmware update tool")

            installation_firmware = True
            status = "SUCCESSFUL"
            print("🎉 Firmware update completed successfully!")

        except FileNotFoundError as e:
            error_msg = f"❌ File not found: {str(e)}"
            error_logs.append({"errors": error_msg, "traceback": traceback.format_exc()})

        except subprocess.CalledProcessError as e:
            error_msg = f"❌ Subprocess error: {e.output if e.output else str(e)}"
            error_logs.append({"errors": error_msg, "traceback": traceback.format_exc()})

        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            error_logs.append({"errors": error_msg, "traceback": traceback.format_exc()})

        CommonSetupCheck.print_separator("✅ FIRMWARE UPDATE COMPLETED")
        return installation_firmware, status, error_logs
            
    @staticmethod
    def driver_update(driver_path, error_logs=[]):
        """
        Install and update the network driver from a given tar file.

        Steps:
        1. Validate driver path.
        2. Extract tar file into a working directory.
        3. Find the best matching folder after extraction.
        4. Run installation commands (make, modprobe, etc.).
        
        Args:
            driver_path (str): Path to the driver tar file.
            error_logs (list): List to collect error messages.
        
        Returns:
            tuple: (installation_driver: bool, status: str, error_logs: list)
        """
        installation_driver = False
        status = "FAILURE"
        error_msg = None

        try:
            CommonSetupCheck.print_separator("🚀 DRIVER EXECUTION STARTED")

            # ✅ Validate driver path
            if not os.path.exists(driver_path):
                error_logs.append("❗ Invalid driver path provided.")
                print("❌ Driver path does not exist!")
                return False, status, error_logs

            # ✅ Prepare working directory
            os.chdir("/root")
            CommonSetupCheck.print_separator(f"📂 Current Directory: {os.getcwd()}")
            os.makedirs("setup_firmware_driver", exist_ok=True)
            os.chdir("setup_firmware_driver")

            current_path = os.getcwd()
            driver_file_name_before_tarting = os.path.basename(driver_path)

            # ✅ Extract firmware tar file
            print(f"📦 Extracting driver file: {driver_path}")
            CommonMethodExecution.run_command(
                ['tar', '-xvf', driver_path, '-C', current_path],
                f"Extracting firmware file: {driver_path}"
            )

            # ✅ Find best matching folder after extraction
            finding_file = CommonMethodExecution.find_best_match(driver_file_name_before_tarting, os.listdir())
            CommonSetupCheck.print_separator("🔍 Driver Folder With Highest Match Score")
            print(f"✅ Best Match: {finding_file.get('folder')} ({finding_file.get('score')}%)")

            driver_folder_name = finding_file.get("folder")
            print(f"📂 Extracted Folders: {os.listdir()}")
            print(f"➡️ Selected Driver Folder: {driver_folder_name}")

            # ✅ Navigate to driver folder
            os.chdir(driver_folder_name)
            CommonSetupCheck.print_separator(f"📂 Current Directory: {os.getcwd()}")

            # ✅ Install dependencies and build driver
            print("🔄 Updating system and installing required packages...")
            CommonMethodExecution.run_command(["apt", "update"], "Updating system packages")
            CommonMethodExecution.run_command(['apt', 'install', '-y', 'make'], "Installing 'make'")

            os.chdir("src")

            finding_file = CommonMethodExecution.find_best_match(driver_file_name_before_tarting, os.listdir())
            CommonSetupCheck.print_separator("🔍 Driver Folder With Highest Match Score")
            print(f"✅ Best Match: {finding_file.get('folder')} ({finding_file.get('score')}%)")

            driver_name = finding_file.get("folder")
            if driver_name:
                driver_name =driver_name.split(".")[0]
            print(f"📂 Extracted Folders: {os.listdir()}")
            print(f"➡️ Selected Driver Folder: {driver_name}")
            CommonMethodExecution.run_command(['make'], "Running make")
            CommonMethodExecution.run_command(['dmesg', '-c'], "Clearing dmesg logs")
            CommonMethodExecution.run_command(['make', 'install'], "Running make install")

            # ✅ Reload kernel modules
            print("🔁 Reloading kernel modules...")
            CommonMethodExecution.run_command(['rmmod', 'irdma'], "Removing irdma module")
            CommonMethodExecution.run_command(['rmmod', driver_name], "Removing ice module")
            CommonMethodExecution.run_command(['modprobe', driver_name], "Loading ice module")

            installation_driver = True
            status = "SUCCESSFUL"
            print("🎉 Driver installation completed successfully!")

        except FileNotFoundError as e:
            error_msg = f"❌ File not found: {str(e)}"
            error_logs.append({"errors": error_msg, "traceback": traceback.format_exc()})

        except subprocess.CalledProcessError as e:
            error_msg = f"❌ Subprocess error: {e.output if e.output else str(e)}"
            error_logs.append({"errors": error_msg, "traceback": traceback.format_exc()})

        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            error_logs.append({"errors": error_msg, "traceback": traceback.format_exc()})
        
        CommonSetupCheck.print_separator("🚀 DRIVER EXECUTION COMPLETED")
        return installation_driver, status, error_logs



class PackageInstalltion:

    @staticmethod
    def install_required_packages(os_system,erros_logs=[]):

        """
        Installs required system and Python packages for DPDK and DTS setup.
        """
        packages_installer, status, error_logs = False,"FAILURE", erros_logs
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            os_name = os_system.get("os_name","LINUX").strip().lower()
            installer_name = "apt"
            if os_name == "openeuler":
                installer_name = "yum"
            elif os_name == "ubuntu":
                installer_name = "apt"
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
                CommonMethodExecution.run_command(pkg, f"Installing {' '.join(pkg[3:]) if len(pkg) > 3 else pkg[1]}")

            for pkg in pip_packages:
                CommonMethodExecution.run_command(pkg, f"Installing Python package {pkg[2]}")
            packages_installer = True
            status = "SUCCESSFUL"
        except subprocess.CalledProcessError as e:
            error_msg = f"❌ Subprocess error: {e.output if e.output else str(e)}"
            error_logs.append({"errors": error_msg, "traceback": traceback.format_exc()})

        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            error_logs.append({"errors": error_msg, "traceback": traceback.format_exc()})
        
        CommonSetupCheck.print_separator("🚀 DRIVER EXECUTION COMPLETED")
        return packages_installer, status, error_logs


class AutomationScriptForSetupInstalltion:

    def __init__(self):
        # # Github Credential integration username and token with url for verfication \ Authentication
        self.dts_url = "https://{}:{}@github.com/intel-sandbox/networking.dataplane.dpdk.dts.local.upstream.git"
        self.dpdk_url = "https://github.com/DPDK/dpdk.git"

    


    # def creating_folder_setup(self,setup_file_name= "setup_firmware_driver"):

    #     """
    #     Creates a setup directory for firmware and driver extraction.
    #     Changes working directory to the newly created folder.
    #     """
    #     print("📁 Creating folder for firmware and driver setup if it doesn't exist...")
    #     os.makedirs(setup_file_name, exist_ok=True)
    #     os.chdir(setup_file_name)
    #     setup_file_path = os.getcwdb().decode()
    #     return setup_file_path
    

    # ###################################   Dpdk and Dts Setup Script       ##################################################################



    def clone_dts_repo(self):

        """
        Clones the private DTS repository using GitHub credentials.
        """
       
        path = os.getcwd()
        print("\n📍current path : "+str(path))
        CommonMethodExecution.run_command(["git", "clone", self.dts_url], "Cloning DTS repository")
        os.chdir("networking.dataplane.dpdk.dts.local.upstream")
        os.chdir("dep")
        
    def clone_dpdk_repo(self):

        """
        Clones the public DPDK repository and checks out a specific version.
        """
        CommonMethodExecution.run_command(["git", "clone", self.dpdk_url], "Cloning DPDK repository")

        CommonMethodExecution.run_command(["tar", "-czvf", "dpdk.tar.gz", "dpdk/"],"taring dpdk file")
        path = os.getcwd()
        print("\n📍current path : "+str(path))
        os.chdir("dpdk")
        CommonMethodExecution.run_command(["git", "checkout","-b", "v25.03-rc3"], "Checking out DPDK version v25.03-rc3")

    








