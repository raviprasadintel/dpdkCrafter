"""
Main automation script for setting up DPDK DTS environment, updating firmware,
installing drivers, configuring ports, and preparing system for testing.

Modules Used:
- execution.setup_installation.AutomationScriptForSetupInstalltion
- execution.bus_info_details.PairingManagerInfo
- execution.dut_ports_config.DutPortConfig
"""

import os
from script_container.execution.setup_installation import AutomationScriptForSetupInstalltion
from script_container.execution.bus_info_details import PairingManagerInfo
from script_container.execution.dut_ports_config import DutPortConfig
from script_container.execution.dut_crbs_config import DutCrbsConfig
from script_container.execution.dut_execution_config import ExecutionCfgUpdate
from script_container.execution.constant import print_separator

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
    dpdk_dts_path = os.environ.get('DPDK_INSTALLTION_PATH',"")
    dpdk_dts_folder_name = "dts_setup"

    try:
        print("\n🚀 Starting Setup Scripts...\n")\
        # STEP 1: Define paths for firmware and driver packages
        firmware_file_path = os.environ.get('FIRMWARE_PATH',"****")
        driver_path = os.environ.get('DRIVER_PATH',"****")

        # 🔐 Replace with environment variables for security
        git_user = os.environ.get('GIT_USERNAME',"").strip()
        git_token = os.environ.get('GIT_TOKEN',"").strip()
        
        if git_token == None or git_token == "" or git_user == None or git_user == "" or dpdk_dts_path =="":
            print("Error: Missing GIT_USERNAME / GIT_TOKEN / DPDK_INSTALLTION_PATH . Please define  in your environment variables to proceed.")
            return
        # Initialize automation script
        script = AutomationScriptForSetupInstalltion(
            firmware_file_path=firmware_file_path,
            driver_path=driver_path,
            git_token=git_token,
            git_user=git_user
        )
        # ADDING SEPARATOR
        print_separator()
        # STEP 0.0 :Updating Proxy First 
        script.setup_proxy_environment()
        
        # STEP 1.1: Update firmware and drivers
        if os.environ.get('DRIVER_UPDATE', 'FALSE').upper() == 'TRUE':
            # ADDING SEPARATOR
            print_separator()
            script.updating_firmware_drivers()

        # STEP 1.2: Install required system and Python packages
        if os.environ.get("APT_PACKAGE_UPDATE_REQUIRED","FALSE").upper() == "TRUE":
            # ADDING SEPARATOR
            print_separator()
            script.install_required_packages()

        # STEP 1.3: Prepare environment for DPDK/DTS setup
       
        os.chdir(dpdk_dts_path)
        # ADDING SEPARATOR
        print_separator()
        script.creating_folder_setup(dpdk_dts_folder_name)
    
        dpdk_dts_path = os.getcwdb().decode()
        
        
        print("git_user => ",git_user,type(git_user))
        print("git_token => ",git_token,type(git_token))

        # STEP 1.4: Clone DPDK and DTS repositories
        # ADDING SEPARATOR
        print_separator()
        print("\n🚀 Starting DPDK and DTS setup process...\n")
        script.clone_dts_repo()
        # ADDING SEPARATOR
        print_separator()
        script.clone_dpdk_repo()

        # Collect error logs
        error_logs += script.error_logs
        error_logs_cmd += script.error_logs_cmd

        # STEP 2: Fetch interface pairing info
        # ADDING SEPARATOR
        print_separator()
        print("🧩 Initializing PairingManagerInfo object...")
        obj = PairingManagerInfo()

        print("\n🔍 Fetching Interface and Bus Pairing Information...\n")
        obj.fetchingInterFacePairingInfo()

        print("\n🔗 Fetching Interface Connection Details...\n")
        obj.fetchingPairDetailsFromInterface()

        print("\nMapping Interface With Bus Info")
        interface_details = obj.mapInterfaceToBus()

        print("INTERFACE DETAILS :\n\n",interface_details)
        
        # STEP 3: Configure DUT ports [ports.cfg]
        ports_config_obj = DutPortConfig(dpdk_dts_path)

        print(
            "\n🔧 Loaded Configuration:\n"
            "-----------------------------\n"
            f"🌐 IP Address : {ports_config_obj.ip_address}\n"
            f"👤 Username   : {ports_config_obj.username}\n"
            f"🔑 Password   : {'*' * len(ports_config_obj.password) if ports_config_obj.password else 'Not Set'}\n"
        )

        ports_config_obj.update_ports(interface_details)

        # STEP 4: Configure Updating Password [crbs.cfg]
        # ADDING SEPARATOR
        print_separator()
        crfs_file_obj = DutCrbsConfig(dpdk_dts_path) 
        crfs_file_obj.updating_crbs_file(
        dut_ip = ports_config_obj.ip_address,
        dut_user = ports_config_obj.username,
        dut_passwd = ports_config_obj.password,
        tester_ip = ports_config_obj.ip_address,
        tester_passwd = ports_config_obj.password
        )
        
        # STEP 5: Configure Execution.cfg
        # ADDING SEPARATOR
        print_separator()
       
        executionObj = ExecutionCfgUpdate(dpdk_dts_path)
        executionObj.update_execution_content(ports_config_obj.ip_address)
        #ERROR : Capturing Viewer
        for log in error_logs:
            print("ERROR LOG:",log)

        for log in error_logs_cmd:
            print("ERROR LOG CMD:",log)

    except Exception as e:
        print(f"\n❌ An error occurred during execution: {e}\n")

    print("\n✅ Script Execution Completed Successfully.\n")


if __name__ == "__main__":
    main()