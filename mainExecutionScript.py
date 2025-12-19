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
from common_script_container.setup_installation import FirmwareDriverInstallation, PackageInstalltion, AutomationScriptForSetupInstalltion
from common_script_container.bus_info_details import InterfaceManager,PairingManagerInfo
from common_script_container.dut_ports_config import DutPortConfig
from common_script_container.dut_crbs_config import DutCrbsConfig
from common_script_container.dut_execution_config import ExecutionCfgUpdate
from common_script_container.constant import CommonMethodExecution, CommonSetupCheck
from crypto_container.cryptoScript import CryptoSetupManager
from ip_deatils_fetcher.fetchingDeatils import process_hosts


class EnvValidator:
    @staticmethod
    def validate_env_vars(var_list):
        missing_vars = []
        optional_missing = []

        message_list = {}
        # First pass: check required variables
        for var_name, is_required, message in var_list:
            value = os.environ.get(var_name)
            message_list[var_name] = message
            if is_required and not value:
                missing_vars.append(f"\n{var_name}: {message}")
            elif not is_required and not value:
                optional_missing.append(var_name)

        # Conditional checks
        dpdk_file_status = os.environ.get("DPDK_FILE_STATUS", "").upper()
        if dpdk_file_status == "TRUE" and not os.environ.get("DPDK_FILE_PATH"):
            missing_vars.append(message_list["DPDK_FILE_PATH"])

        if os.environ.get("FIRMWARE_UPDATE_REQUIRED", "").upper() == "TRUE" and not os.environ.get("FIRMWARE_PATH"):
            missing_vars.append(message_list["FIRMWARE_PATH"])

        if os.environ.get("DRIVER_INSTALL_REQUIRED", "").upper() == "TRUE" and not os.environ.get("DRIVER_PATH"):
            missing_vars.append(message_list["DRIVER_PATH"])
        
        if os.environ.get("DTS_INSTALLATION_REQUIRED","").upper() == "TRUE" and(
            not os.environ.get("GIT_USERNAME") or 
            not os.environ.get("GIT_TOKEN") or
            not os.environ.get("DTS_INSTALLATION_PATH") 
            ):

            mess = (f"✅ If DTS_INSTALLATION_REQUIRED is set to TRUE, these variables are required.\n"
                    f"GIT_USERNAME : {message_list["GIT_USERNAME"]}\n"
                    f"GIT_TOKEN : {message_list["GIT_TOKEN"]}\n"
                    f"DTS_INSTALLATION_PATH : {message_list["DTS_INSTALLATION_PATH"]}\n"
                    f"DTS_RUN : {message_list["DTS_RUN"]}\n"
                    f"UPDATE_AUTOMATICALLY_PORTS_CRBS_EXECUTION : {message_list["DTS_RUN"]}\n"
                   
                    )
            missing_vars.append(mess)
        if os.environ.get("DTS_INSTALLATION_REQUIRED","").upper() == "FALSE" and(
            os.environ.get("UPDATE_AUTOMATICALLY_PORTS_CRBS_EXECUTION","").upper() =="TRUE") and(
            not os.environ.get("DTS_INSTALLATION_PATH")
            ):

            mess = "Automatic update of CRBS.CFG, PORTS.CFG, and EXECUTION.CFG is enabled (UPDATE_AUTOMATICALLY_PORTS_CRBS_EXECUTION=TRUE)\n REQUIRED : DTS_INSTALLATION_PATH \n\n Exampls /root/dts_setup/networking.dataplane.dpdk.dts.local.upstreamg \n\n"
            missing_vars.append(mess)

        # Final validation
        if missing_vars:
            error_message = "\n".join(missing_vars)
            raise EnvironmentError(f"[ENV VALIDATION FAILED]\n{error_message}")
        else:
            print("[INFO] All required environment variables are set.")
            if optional_missing:
                print(f"[INFO] Optional variables not set: {', '.join(optional_missing)}")


all_required_variable = [
    ["DPDK_FILE_STATUS", False,
     "If TRUE, use the DPDK file for installation; otherwise clone from the repository. "
     "If TRUE, DPDK_FILE_PATH must be provided."],
    ["DPDK_FILE_PATH", False, "Path to the DPDK tarball used for installation (required if DPDK_FILE_STATUS is TRUE)."],

    # For Dts setup this thing is required 
    ["DTS_INSTALLATION_REQUIRED", False,"Set to TRUE if DTS installation is required; FALSE to skip installation."],
    ["DTS_INSTALLATION_PATH", False, "Path where the DTS (DPDK Test Suite) is installed."],
    ["GIT_USERNAME", False, "Git username required to access private repositories."],
    ["GIT_TOKEN", False, "GitHub token required for authentication and secure repository access."],
    ["DTS_RUN", False, "Determines whether DTS should be executed (default is FALSE)."],
    ["UPDATE_AUTOMATICALLY_PORTS_CRBS_EXECUTION", False, "Set to TRUE to automatically update CRBS.CFG, PORTS.CFG, and EXECUTION.CFG based on system configuration; set to FALSE to disable automatic updates."],
    # ["QAT_DRIVER_PATH", True,
    #  "Path to the QAT driver archive (e.g., QAT20.L.1.2.30-00109.tar.gz) used for updating QAT examples."],
    # ["FIPS_TAR_FILE_PATH", True, "Path to the FIPS tarball (e.g., fips.tar.gz) for cryptographic validation."],
    # ["CALGARY_TAR_FILE_PATH", True,
    #  "Path to the Calgary tarball (e.g., calgary.tar.gz) used for performance or compliance testing."],
    ["FIRMWARE_UPDATE_REQUIRED", False, "Set to TRUE when a firmware update is required."],
    ["DRIVER_INSTALL_REQUIRED", False, "Set to TRUE when driver installation is required."],
    ["FIRMWARE_PATH", False, "Path to firmware file (required if FIRMWARE_UPDATE_REQUIRED is TRUE)."],
    ["DRIVER_PATH", False, "Path to driver file (required if DRIVER_INSTALL_REQUIRED is TRUE)."],
    ["APT_PACKAGES_INSTALL_REQUIRED",True, "Set this to TRUE if system packages need to be installed; otherwise set to FALSE."]
]


def conclusion_print(conclusion,error_logs):
    CommonSetupCheck.print_separator("Error Throw :\n",header=False)
    for errors in error_logs:
        print(errors)
    CommonSetupCheck.print_separator("PRINTING CONCLUSION")
    for con in conclusion:
        print(con)


def main():
    """
    Executes the full setup process:
    0. Checking Current OS system
    1. Update firmware.
    2. Update driver
    3. Install required packages
    4. Trying to make interface UP 
    5. Mapping Inteerface with, bus details using `DMESG -C`
    6. Prepare environment and clone repositories
    7. Configure DUT ports
    """

    error_logs = []
    conclusion = []
    try:
        if 1:
            hosts_input = [
                ["10.138.182.136", "root", "tester"],
                # ["10.138.182.176", "root", "tester"],
            ]
            
            results = process_hosts(hosts_input)

            print("\n=== RESULTS ===")
            for r in results:
                for key , val in r.items():
                    print(key, ": ",val)

        else:
            CommonSetupCheck.print_separator("🚀 Starting Setup Scripts...\n\n",header=False)
            # STEP 0 :
            # OS SYSTEM -: CHECK
            CommonSetupCheck.print_separator("CURRENT SYSTEM OS CHECK")
            os_check = CommonSetupCheck.check_os()
            dts_setup_path = os.environ.get("DTS_INSTALLATION_PATH","")
            # STEP 1 :
            # FIRMWARE INSTALLATION :
            if os.environ.get("FIRMWARE_UPDATE_REQUIRED","").upper() == "TRUE":
                CommonSetupCheck.print_separator("FIRMWARE UPDATE PROCESS STARTED ...")
                statement = FirmwareDriverInstallation.firmware_update(firmware_file_path = os.environ.get("FIRMWARE_PATH"),error_logs= error_logs)
                
                # Add emoji indicators for status
                status_emoji = "✅" if statement[1].upper() == "SUCCESS" else "❌"
                conclusion.append(
                    {
                        "FIRMWARE_UPDATE_STATUS": {
                            "UPDATED": f"{'✔️' if statement[0] else '❌'}",
                            "STATUS": f"{status_emoji} {statement[1]}",
                            "ERRORS": statement[2] if statement[2] else "None"
                        }
                    }
                )

            # STEP 2 :
            # DRIVER UPDATE :
            if os.environ.get("DRIVER_INSTALL_REQUIRED","").upper() == "TRUE":
                CommonSetupCheck.print_separator("DRIVER UPDATE PROCESS STARTED ...")
                statement = FirmwareDriverInstallation.driver_update(driver_path = os.environ.get("DRIVER_PATH"),error_logs= error_logs)
                # Add emoji indicators for status
                status_emoji = "✅" if statement[1].upper() == "SUCCESS" else "❌"
                conclusion.append(
                    {
                        "DRIVER_UPDATE_STATUS": {
                            "UPDATED": f"{'✔️' if statement[0] else '❌'}",
                            "STATUS": f"{status_emoji} {statement[1]}",
                            "ERRORS": statement[2] if statement[2] else "None"
                        }
                    }
                )

            # STEP 3 :
            # APT PACKAGES INSTALL
            if os.environ.get("APT_PACKAGES_INSTALL_REQUIRED","").upper() == "TRUE":
                CommonSetupCheck.print_separator("PACKAGE INSTALLATION STARTED ...")
                statement = PackageInstalltion.install_required_packages(os_check)
                status_emoji = "✅" if statement[1].upper() == "SUCCESS" else "❌"
                conclusion.append(
                    {
                        "APT_PACKAGE_INSTALL_STATUS": {
                            "UPDATED": f"{'✔️' if statement[0] else '❌'}",
                            "STATUS": f"{status_emoji} {statement[1]}",
                            "ERRORS": statement[2] if statement[2] else "None"
                        }
                    }
                )

            # STEP 4: Prepare environment and clone repositories
            dts_setup = False
            dpdk_setup = False
            if os.environ.get("DTS_INSTALLATION_REQUIRED", "FALSE").upper() == "TRUE":
                dpdk_file_status = os.environ.get("DPDK_FILE_STATUS", "FALSE").upper() == "TRUE"
                dpdk_file_path = os.environ.get("DPDK_FILE_PATH", "")

                CommonSetupCheck.print_separator("📦 DTS/DPDK INSTALLATION PROCESSS STARTED ...")

                
                # ✅ Check if DTS setup path exists
                if os.path.exists(dts_setup_path):
                    CommonSetupCheck.print_separator(f"\n✅ DTS setup path exists: {dts_setup_path}\n",header=False)
                else:
                    dts_setup_path = os.getcwd()
                    CommonSetupCheck.print_separator(f"\n⚠️ DTS setup path not found. Creating in same Directory : {dts_setup_path}\n",header=False)

                if dpdk_file_status:
                    print(f"🔍 Checking DPDK file path: {dpdk_file_path}")
                    if not os.path.exists(dpdk_file_path):
                        CommonSetupCheck.print_separator("⚠️ Provided DPDK path is invalid. Proceeding with cloning DPDK repository...")
                    else:
                        print("✅ Valid DPDK file path found.")
                else:
                    CommonSetupCheck.print_separator("ℹ️ DPDK file status is FALSE. Proceeding with cloning DPDK repository...")

                # CLONING AND INSTALLATION DTS SETUP 
                # GOING TO DTS setup folder to clone dts
                if os.path.exists(os.path.join(dts_setup_path,"dts_setup")) == True:
                    CommonMethodExecution.run_command(["rm", "-rf", "dts_setup"], "REMOVING EXISTING DTS_SETUP")
                os.chdir(dts_setup_path)
                os.makedirs("dts_setup",exist_ok=True)
            
                dts_setup_path = os.path.join(dts_setup_path,"dts_setup")
                os.chdir(dts_setup_path)
                statement =AutomationScriptForSetupInstalltion.clone_dts_repo(os.environ.get("GIT_USERNAME"),os.environ.get("GIT_TOKEN"))
                status_emoji = "✅" if statement[0].upper() == "SUCCESS" else "❌"
                conclusion.append(
                    {
                        "DTS-CLONING": {
                            "UPDATED": f"{'✔️' if statement[0] else '❌'}",
                            "STATUS": f"{status_emoji} {statement[1]}",
                            "ERRORS": statement[1] if statement[1] else "None"
                        }
                    }
                )
                dts_setup  = statement[0].upper() != "SUCCESS"
            
                if statement[0].upper() == "SUCCESS":
                    statement = AutomationScriptForSetupInstalltion.clone_dpdk_repo(
                        DPDK_FILE_STATUS = os.environ.get("DPDK_FILE_STATUS").upper() == "TRUE" ,
                        DPDK_FILE_PATH = os.environ.get("DPDK_FILE_PATH","")
                    )
                    status_emoji = "✅" if statement[0].upper() == "SUCCESS" else "❌"
                    conclusion.append(
                        {
                            "DPDK-CLONING": {
                                "UPDATED": f"{'✔️' if statement[0] else '❌'}",
                                "STATUS": f"{status_emoji} {statement[1]}",
                                "ERRORS": statement[1] if statement[1] else "None"
                            }
                        }
                    )
                    # COMMING OUT DEP FOLDER
                    os.chdir("..")
                    dts_setup_path = os.getcwd()
                    dpdk_setup = statement[0].upper() != "SUCCESS"
            if (os.environ.get("DTS_INSTALLATION_REQUIRED", "FALSE").upper() == "TRUE")and(dts_setup or dpdk_setup):
                conclusion_print(conclusion,error_logs)
                return 
                
            # IF step 5 : 
            if os.environ.get("UPDATE_AUTOMATICALLY_PORTS_CRBS_EXECUTION","").upper() == "TRUE":
                # FETCHING BUS INFO DETAILS
                interface_man_obj  = InterfaceManager(error_logs= error_logs)
                statement = interface_man_obj.process_all_interfaces()
                up_interface = []
                down_inteface = []
                up_interface += statement["up_interface"]
                down_inteface += statement['down_interface']

                if len(up_interface) <=0:
                    CommonSetupCheck.print_separator("⚠️ Attempted to enable the interface, but it could not be brought UP.")
                # Mapping bus info into 
                print("🧩 Initializing PairingManagerInfo object...")
                pariting_obj = PairingManagerInfo()

                print("\n🔍 Fetching Interface and Bus Pairing Information...\n")
                pariting_obj.fetchingInterFacePairingInfo()

                print("\n🔗 Fetching Interface Connection Details...\n")
                pariting_obj.fetchingPairDetailsFromInterface()

                print("\nMapping Interface With Bus Info")
                interface_details = pariting_obj.mapInterfaceToBus()

                # Configuring ports.cfg: 
                ports_config_obj = DutPortConfig(dts_setup_path)
                print(
                    "\n🔧 Loaded Configuration:\n"
                    "-----------------------------\n"
                    f"🌐 IP Address : {ports_config_obj.ip_address}\n"
                    f"👤 Username   : {ports_config_obj.username}\n"
                    f"🔑 Password   : {'*' * len(ports_config_obj.password) if ports_config_obj.password else 'Not Set'}\n"
                )
                statement = ports_config_obj.update_ports(interface_details)

                status_emoji = "✅" if statement[0].upper() == "SUCCESS" else "❌"
                conclusion.append(
                    {
                        "PORTS.CFG-UPDATE-STATUS": {
                            "UPDATED": f"{'✔️' if statement[0] else '❌'}",
                            "STATUS": f"{status_emoji} {statement[1]}",
                            "ERRORS": statement[1] if statement[1] else "None"
                        }
                    }
                )
                # UPDATING : crbs.cfg

                crfs_file_obj = DutCrbsConfig(dts_setup_path) 
                statement = crfs_file_obj.updating_crbs_file(
                dut_ip = ports_config_obj.ip_address,
                dut_user = ports_config_obj.username,
                dut_passwd = ports_config_obj.password,
                tester_ip = ports_config_obj.ip_address,
                tester_passwd = ports_config_obj.password
                )
                status_emoji = "✅" if statement[0].upper() == "SUCCESS" else "❌"
                conclusion.append(
                    {
                        "CRBS.CFG-UPDATE-STATUS": {
                            "UPDATED": f"{'✔️' if statement[0] else '❌'}",
                            "STATUS": f"{status_emoji} {statement[1]}",
                            "ERRORS": statement[1] if statement[1] else "None"
                        }
                    }
                )
                # UPDATING Execution.cfg 
                executionObj = ExecutionCfgUpdate(dts_setup_path)
                statement = executionObj.update_execution_content(ports_config_obj.ip_address)
                status_emoji = "✅" if statement[0].upper() == "SUCCESS" else "❌"
                conclusion.append(
                    {
                        "EXECUTION.CFG-UPDATE-STATUS": {
                            "UPDATED": f"{'✔️' if statement[0] else '❌'}",
                            "STATUS": f"{status_emoji} {statement[1]}",
                            "ERRORS": statement[1] if statement[1] else "None"
                        }
                    }
                )

            if (os.environ.get("DTS_RUN","").upper() == "TRUE") and((os.environ.get("UPDATE_AUTOMATICALLY_PORTS_CRBS_EXECUTION","").upper() == "TRUE")or (os.environ.get("DTS_INSTALLATION_REQUIRED", "FALSE").upper() == "TRUE") ):
                os.chdir(dts_setup_path)

            # CHECK FOR CRYPTO DRIVER :
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


            conclusion_print(conclusion,error_logs)
         
            

    except FileNotFoundError as e:
        error_msg = f"❌ File not found: {str(e)}"
        print(error_msg)
        return False, error_msg
    except subprocess.CalledProcessError as e:
        error_msg = f"❌ Subprocess error: {e.output if e.output else str(e)}"
        error_logs.append({
            "errors": error_msg,
            "traceback": traceback.format_exc()
        })
        print(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"❌ Unexpected error: {str(e)}"
        error_logs.append({
            "errors": error_msg,
            "traceback": traceback.format_exc()
        })
        print(error_msg)
        return False, error_msg
    
    

    # print("\n✅ Script Execution Completed Successfully.\nDisplaying - Errors Logs\n")

    # print("\n✅ Script Execution Completed Successfully.\n")


if __name__ == "__main__":
    # CHECKING ALL VARIABLE ASSIGN PROPERLY
    # EnvValidator.validate_env_vars(all_required_variable)

    # EXECUTING STARTED
    main()