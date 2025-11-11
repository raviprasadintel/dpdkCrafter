"""
Main automation script for setting up DPDK DTS environment, updating firmware,
installing drivers, configuring ports, and preparing system for testing.

Modules Used:
- execution.setup_installation.AutomationScriptForSetupInstalltion
- execution.bus_info_details.PairingManagerInfo
- execution.dut_ports_config.DutPortConfig
"""

import os
import subprocess
import traceback
# from script_container.execution.setup_installation import AutomationScriptForSetupInstalltion
from script_container.execution.bus_info_details import PairingManagerInfo
# from script_container.execution.dut_ports_config import DutPortConfig
# from script_container.execution.dut_crbs_config import DutCrbsConfig
# from script_container.execution.dut_execution_config import ExecutionCfgUpdate
# from script_container.execution.constant import print_separator
from crypto_container.cryptoScript import CryptoSetupManager





class EnvValidator:
    @staticmethod
    def validate_env_vars(var_list):
        missing_vars = []
        for var_name, is_required, message in var_list:
            value = os.environ.get(var_name)
            if is_required and not value:
                missing_vars.append(f"{var_name}: {message}")
        
        if missing_vars:
            error_message = "\n".join(missing_vars)
            raise EnvironmentError(f"[ENV VALIDATION FAILED]\n{error_message}")
        else:
            print("[INFO] All required environment variables are set.")


all_required_variable = [
    ["GIT_USERNAME", True, "Git username is required for repository access."],
    ["GIT_TOKEN", True, "Git token is required for authentication."],
    ["DPDK_FILE_PATH", False, "Optional: Path to the DPDK configuration file."],
    ["DTS_INSTALLTION_PATH", True, "DTS installation path is mandatory."],
    ["QAT_DRIVER_PATH",True,"QAT Driver path required for Updating QAT Example file Shoulde look Like (QAT20.L.1.2.30-00109.tar.gz)"],

]

EnvValidator.validate_env_vars(all_required_variable)

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
    # dpdk_dts_folder_name = "dts_setup"

    try:
        print("\n🚀 Starting Setup Scripts...\n")\
        # # STEP 1: Define paths for firmware and driver packages
        # firmware_file_path = os.environ.get('FIRMWARE_PATH',"****")
        # driver_path = os.environ.get('DRIVER_PATH',"****")

        # # 🔐 Replace with environment variables for security
        # git_user = os.environ.get('GIT_USERNAME',"").strip()
        # git_token = os.environ.get('GIT_TOKEN',"").strip()
        
        # if (os.environ.get("DPDK_SETUP_INSTALLATION","false").upper() == "TRUE") and (git_token == None or git_token == "" or git_user == None or git_user == "" or dpdk_dts_path ==""):
        #     print("Error: Missing GIT_USERNAME / GIT_TOKEN / DPDK_INSTALLTION_PATH . Please define  in your environment variables to proceed.")
        #     return
        # # Initialize automation script
        # script = AutomationScriptForSetupInstalltion(
        #     firmware_file_path=firmware_file_path,
        #     driver_path=driver_path,
        #     git_token=git_token,
        #     git_user=git_user
        # )
        # # ADDING SEPARATOR
        # print_separator()
        # # STEP  :Updating Proxy First 
        # script.setup_proxy_environment()
        
        # # STEP : Update firmware and drivers
        # if os.environ.get('DRIVER_UPDATE', 'FALSE').upper() == 'TRUE':
        #     # ADDING SEPARATOR
        #     print_separator()
        #     script.updating_firmware_drivers()

        # # STEP : Install required system and Python packages
        # if os.environ.get("APT_PACKAGE_UPDATE_REQUIRED","FALSE").upper() == "TRUE":
        #     # ADDING SEPARATOR
        #     print_separator()
        #     script.install_required_packages()

        # # STEP : Prepare environment for DPDK/DTS setup
        # if os.environ.get("DPDK_SETUP_INSTALLATION","false").upper() == "TRUE":
        #     os.chdir(dpdk_dts_path)
        #     # ADDING SEPARATOR
        #     print_separator()
        #     script.creating_folder_setup(dpdk_dts_folder_name)
        
        #     dpdk_dts_path = os.getcwdb().decode()
            
            
        #     print("git_user => ",git_user,type(git_user))
        #     print("git_token => ",git_token,type(git_token))

        #     # STEP : Clone DPDK and DTS repositories
        #     # ADDING SEPARATOR
        #     print_separator()
        #     print("\n🚀 Starting DPDK and DTS setup process...\n")
        #     script.clone_dts_repo()
        #     # ADDING SEPARATOR
        #     print_separator()
        #     script.clone_dpdk_repo()

        #     # Collect error logs
        #     error_logs += script.error_logs
        #     error_logs_cmd += script.error_logs_cmd

        #     # STEP : Fetch interface pairing info
        #     # ADDING SEPARATOR
        #     print_separator()
        #     print("🧩 Initializing PairingManagerInfo object...")
        #     obj = PairingManagerInfo()

        #     print("\n🔍 Fetching Interface and Bus Pairing Information...\n")
        #     obj.fetchingInterFacePairingInfo()

        #     print("\n🔗 Fetching Interface Connection Details...\n")
        #     obj.fetchingPairDetailsFromInterface()

        #     print("\nMapping Interface With Bus Info")
        #     interface_details = obj.mapInterfaceToBus()

        #     print("INTERFACE DETAILS :\n\n",interface_details)
            
        #     # STEP : Configure DUT ports [ports.cfg]
        #     ports_config_obj = DutPortConfig(dpdk_dts_path)

        #     print(
        #         "\n🔧 Loaded Configuration:\n"
        #         "-----------------------------\n"
        #         f"🌐 IP Address : {ports_config_obj.ip_address}\n"
        #         f"👤 Username   : {ports_config_obj.username}\n"
        #         f"🔑 Password   : {'*' * len(ports_config_obj.password) if ports_config_obj.password else 'Not Set'}\n"
        #     )

        #     ports_config_obj.update_ports(interface_details)

        #     # STEP : Configure Updating Password [crbs.cfg]
        #     # ADDING SEPARATOR
        #     print_separator()
        #     crfs_file_obj = DutCrbsConfig(dpdk_dts_path) 
        #     crfs_file_obj.updating_crbs_file(
        #     dut_ip = ports_config_obj.ip_address,
        #     dut_user = ports_config_obj.username,
        #     dut_passwd = ports_config_obj.password,
        #     tester_ip = ports_config_obj.ip_address,
        #     tester_passwd = ports_config_obj.password
        #     )
            
        #     # STEP : Configure Execution.cfg
        #     # ADDING SEPARATOR
        #     print_separator()
        
        #     executionObj = ExecutionCfgUpdate(dpdk_dts_path)
        #     executionObj.update_execution_content(ports_config_obj.ip_address)
        #     #ERROR : Capturing Viewer
        #     for log in error_logs:
        #         print("ERROR LOG:",log)

        #     for log in error_logs_cmd:
        #         print("ERROR LOG CMD:",log)


        #     # STEP : Executing Process [DTS] setup
        #     if os.environ.get("DPDK_SETUP_RUN","false").upper() == "TRUE":
        #         # ADDING SEPARATOR
        #         print_separator()
        #         print_separator()
        #         path = dpdk_dts_path.strip() + "/networking.dataplane.dpdk.dts.local.upstream"
        #         os.chdir(path)
        #         script.run_command(["./dts"],"\n\n---------------RUNNING DTS SERVICE-----------\n\n")
        #         print_separator()
        #         print_separator()

        # Worked on Later Dpdk Setup And all
        cryptObj = CryptoSetupManager(
        dts_setup_path=os.environ.get("DTS_INSTALLTION_PATH",""), 
        dpdk_file_path=os.environ.get("DPDK_FILE_PATH"),
        automation_folder_path= "/root/automation/",
        git_user= os.environ.get("GIT_USERNAME"),
        git_token= os.environ.get("GIT_TOKEN"),
        qat_driver_path = os.environ.get("QAT_DRIVER_PATH")
        )

        cryptObj.crypto_execution_script()


        # # Fetching Current Bus Info DETAILS..
        # print("🧩 Initializing PairingManagerInfo object...")
        # managerInfo = PairingManagerInfo()

        # print("\n🔍 Fetching Interface and Bus Pairing Information...\n")
        # managerInfo.fetchingInterFacePairingInfo()

        # print("\n🔗 Fetching Interface Connection Details...\n")
        # managerInfo.fetchingPairDetailsFromInterface()

        # print("\nMapping Interface With Bus Info")
        # interface_details = managerInfo.mapInterfaceToBus()

        # print("INTERFACE DETAILS :\n\n",interface_details)

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

    print("\n✅ Script Execution Completed Successfully.\nDisplaying - Errors Logs\n")



if __name__ == "__main__":

    
    main()