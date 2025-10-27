"""
Main automation script for setting up DPDK DTS environment, updating firmware,
installing drivers, configuring ports, and preparing system for testing.

Modules Used:
- execution.setup_installation.AutomationScriptForSetupInstalltion
- execution.bus_info_details.PairingManagerInfo
- execution.dut_ports_config.DutPortConfig
"""

import os
from execution.setup_installation import AutomationScriptForSetupInstalltion
from execution.bus_info_details import PairingManagerInfo
from execution.dut_ports_config import DutPortConfig


def main():
    """
    Executes the full setup process:
    1. Update firmware and drivers
    2. Install required packages
    3. Prepare environment and clone repositories
    4. Fetch interface pairing info and map bus details
    5. Configure DUT ports
    """

    error_logs = []
    error_logs_cmd = []
    dpdk_dts_path  = ""
    dpdk_dts_folder_name = "dts_setup"
    try:
        print("\n🚀 Starting Setup Scripts...\n")\
        # STEP 1: Define paths for firmware and driver packages
        firmware_file_path = "/root/E810_NVMUpdatePackage_v4_90_Linux.tar.gz"
        driver_path = "/root/ice-2.3.10 (1).tar.gz"

        # 🔐 Replace with environment variables for security
        git_user = "*****"
        git_token = "*****"

        # Initialize automation script
        script = AutomationScriptForSetupInstalltion(
            firmware_file_path=firmware_file_path,
            driver_path=driver_path,
            git_token=git_token,
            git_user=git_user
        )
        # STEP 0.0 :Updating Proxy First 
        script.setup_proxy_environment()
        
        # STEP 1.1: Update firmware and drivers
        script.updating_firmware_drivers()

        # STEP 1.2: Install required system and Python packages
        script.install_required_packages()

        # STEP 1.3: Prepare environment for DPDK/DTS setup
        os.chdir("/root")
        script.creating_folder_setup(dpdk_dts_folder_name)

        pwd_path =script.run_command(["pwd"],"Fetching DPDK DTS Setup Path",check_output=True)
        if pwd_path[0]:
            dpdk_dts_path = pwd_path[1]
        else:
            dpdk_dts_path = f"/root/{dpdk_dts_folder_name}"
        

        # STEP 1.4: Clone DPDK and DTS repositories
        print("\n🚀 Starting DPDK and DTS setup process...\n")
        script.clone_dts_repo()
        script.clone_dpdk_repo()

        # Collect error logs
        error_logs += script.error_logs
        error_logs_cmd += script.error_logs_cmd

        # STEP 2: Fetch interface pairing info
        print("🧩 Initializing PairingManagerInfo object...")
        obj = PairingManagerInfo()

        print("\n🔍 Fetching Interface and Bus Pairing Information...\n")
        obj.fetchingInterFacePairingInfo()

        print("\n🔗 Fetching Interface Connection Details...\n")
        obj.fetchingPairDetailsFromInterface()

        print("\nMapping Interface With Bus Info")
        interface_details = obj.mapInterfaceToBus()

        # STEP 3: Configure DUT ports
       
        ports_config_obj = DutPortConfig(dpdk_dts_path)

        print(
            "\n🔧 Loaded Configuration:\n"
            "-----------------------------\n"
            f"🌐 IP Address : {ports_config_obj.ip_address}\n"
            f"👤 Username   : {ports_config_obj.username}\n"
            f"🔑 Password   : {'*' * len(ports_config_obj.password) if ports_config_obj.password else 'Not Set'}\n"
        )

        ports_config_obj.update_ports(interface_details)

    except Exception as e:
        print(f"\n❌ An error occurred during execution: {e}\n")

    print("\n✅ Script Execution Completed Successfully.\n")


if __name__ == "__main__":
    main()
