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
from common_script_container.setup_installation import FirmwareDriverInstallation
from common_script_container.bus_info_details import PairingManagerInfo
from common_script_container.dut_ports_config import DutPortConfig
from common_script_container.dut_crbs_config import DutCrbsConfig
from common_script_container.dut_execution_config import ExecutionCfgUpdate
from common_script_container.constant import CommonMethodExecution, CommonSetupCheck
from crypto_container.cryptoScript import CryptoSetupManager



class EnvValidator:
    @staticmethod
    def validate_env_vars(var_list):
        missing_vars = []
        optional_missing = []

        # First pass: check required variables
        for var_name, is_required, message in var_list:
            value = os.environ.get(var_name)
            if is_required and not value:
                missing_vars.append(f"{var_name}: {message}")
            elif not is_required and not value:
                optional_missing.append(var_name)

        # Conditional checks
        dpdk_file_status = os.environ.get("DPDK_FILE_STATUS", "").upper()
        if dpdk_file_status == "TRUE" and not os.environ.get("DPDK_FILE_PATH"):
            missing_vars.append("DPDK_FILE_PATH: Required because DPDK_FILE_STATUS is TRUE.")

        if os.environ.get("FIRMWARE_UPDATE_REQUIRED", "").upper() == "TRUE" and not os.environ.get("FIRMWARE_PATH"):
            missing_vars.append("FIRMWARE_PATH: Required because FIRMWARE_UPDATE_REQUIRED is TRUE.")

        if os.environ.get("DRIVER_INSTALL_REQUIRED", "").upper() == "TRUE" and not os.environ.get("DRIVER_PATH"):
            missing_vars.append("DRIVER_PATH: Required because DRIVER_INSTALL_REQUIRED is TRUE.")

        # Final validation
        if missing_vars:
            error_message = "\n".join(missing_vars)
            raise EnvironmentError(f"[ENV VALIDATION FAILED]\n{error_message}")
        else:
            print("[INFO] All required environment variables are set.")
            if optional_missing:
                print(f"[INFO] Optional variables not set: {', '.join(optional_missing)}")


all_required_variable = [
    # ["GIT_USERNAME", True, "Git username required to access private repositories."],
    # ["GIT_TOKEN", True, "GitHub token required for authentication and secure repository access."],
    # ["DPDK_FILE_STATUS", True,
    #  "If TRUE, use the DPDK file for installation; otherwise clone from the repository. "
    #  "If TRUE, DPDK_FILE_PATH must be provided."],
    # ["DPDK_FILE_PATH", False, "Path to the DPDK tarball used for installation (required if DPDK_FILE_STATUS is TRUE)."],
    # ["DTS_INSTALLATION_PATH", True, "Path where the DTS (DPDK Test Suite) is installed."],
    # ["DTS_RUN", False, "Determines whether DTS should be executed (default is FALSE)."],
    # ["QAT_DRIVER_PATH", True,
    #  "Path to the QAT driver archive (e.g., QAT20.L.1.2.30-00109.tar.gz) used for updating QAT examples."],
    # ["FIPS_TAR_FILE_PATH", True, "Path to the FIPS tarball (e.g., fips.tar.gz) for cryptographic validation."],
    # ["CALGARY_TAR_FILE_PATH", True,
    #  "Path to the Calgary tarball (e.g., calgary.tar.gz) used for performance or compliance testing."],
    ["FIRMWARE_UPDATE_REQUIRED", False, "Set to TRUE when a firmware update is required."],
    # ["DRIVER_INSTALL_REQUIRED", False, "Set to TRUE when driver installation is required."],
    ["FIRMWARE_PATH", False, "Path to firmware file (required if FIRMWARE_UPDATE_REQUIRED is TRUE)."],
    # ["DRIVER_PATH", False, "Path to driver file (required if DRIVER_INSTALL_REQUIRED is TRUE)."],
    # ["APT_PACKAGES_INSTALL_REQUIRED",True, "Set this to TRUE if system packages need to be installed; otherwise set to FALSE."]
]




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
    conclusion = []
    try:
        print("\n🚀 Starting Setup Scripts...\n")

        # FIRMWARE INSTALLATION :
        if os.environ.get("FIRMWARE_UPDATE_REQUIRED","").upper() == "TRUE":
            statement = FirmwareDriverInstallation.firmware_update(firmware_file_path = os.environ.get("FIRMWARE_PATH"),error_logs= error_logs)
            
            # Add emoji indicators for status
            status_emoji = "✅" if statement[1].upper() == "SUCCESS" else "❌"
            conclusion.append(
                {
                    "FIRMWARE_UPDATE": {
                        "UPDATED": f"{'✔️' if statement[0] else '❌'}",
                        "STATUS": f"{status_emoji} {statement[1]}",
                        "ERRORS": statement[2] if statement[2] else "None"
                    }
                }
            )

        # DRIVER UPDATE :
        if os.environ.get("DRIVER_INSTALL_REQUIRED","").upper() == "TRUE":
            pass


        # APT PACKAGES INSTALL


        # # CRYPTO SETTING : Execution
        # cryptObj = CryptoSetupManager(
        # dts_setup_path=os.environ.get("DTS_INSTALLTION_PATH",""), 
        # dpdk_file_path=os.environ.get("DPDK_FILE_PATH"),
        # automation_folder_path= "/root/automation/",
        # git_user= os.environ.get("GIT_USERNAME"),
        # git_token= os.environ.get("GIT_TOKEN"),
        # qat_driver_path = os.environ.get("QAT_DRIVER_PATH"),
        # fips_tar_file_path = os.environ.get("FIPS_TAR_FILE_PATH"),
        # calgery_tar_file_path= os.environ.get("CALGARY_TAR_FILE_PATH"),
        # logs_captured=error_logs
        # )

        # status_execution = cryptObj.crypto_execution_script()

        # if status_execution['status']:
        #     # Fetching Current Bus Info DETAILS..
        #     print("🧩 Initializing PairingManagerInfo object...")
        #     managerInfo = PairingManagerInfo(error_logs)

        #     print("\n🔍 Fetching Interface and Bus Pairing Information...\n")
        #     managerInfo.fetchingInterFacePairingInfo()

        #     print("\n🔗 Fetching Interface Connection Details...\n")
        #     managerInfo.fetchingPairDetailsFromInterface()

        #     print("\nMapping Interface With Bus Info")
        #     interface_details = managerInfo.mapInterfaceToBus()

        #     print("INTERFACE DETAILS :\n\n",interface_details)

        #     # GETTING FILE PATH WHILE RUNNING ABAOVE CMD WE WILL GET
        #     dts_driver_path = status_execution['dts_driver_path']
        #     config_file_folder_path = status_execution['config_file_folder_path']

        #     # STEP : Configure DUT ports [ports.cfg]
        #     output_file_path = os.path.join(dts_driver_path,"conf","ports.cfg")
        #     ports_config_obj = DutPortConfig(dts_driver_path)

        #     print(
        #         "\n🔧 Loaded Configuration:\n"
        #         "-----------------------------\n"
        #         f"🌐 IP Address : {ports_config_obj.ip_address}\n"
        #         f"👤 Username   : {ports_config_obj.username}\n"
        #         f"🔑 Password   : {'*' * len(ports_config_obj.password) if ports_config_obj.password else 'Not Set'}\n"
        #     )

        #     ports_config_obj.update_ports(interface_details)


        CommonSetupCheck.print_separator("PRINTING CONCLUSION")
        for con in conclusion:
            print(con)






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

    # print("\n✅ Script Execution Completed Successfully.\nDisplaying - Errors Logs\n")

    # print("\n✅ Script Execution Completed Successfully.\n")


if __name__ == "__main__":
    # CHECKING ALL VARIABLE ASSIGN PROPERLY
    EnvValidator.validate_env_vars(all_required_variable)

    # EXECUTING STARTED
    main()