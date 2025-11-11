import os
import subprocess
import time
import traceback
from script_container.execution.constant import CommonFuntion


# Script Class
class CryptoSetupManager(CommonFuntion):
    """
    A utility class to manage cryptographic setup tasks in a DPDK test environment.
    This includes validating paths, executing shell commands, and preparing the system
    for crypto-related test execution.
    """

    def __init__(self,dts_setup_path, dpdk_file_path, automation_folder_path= "",git_user= "",git_token= "",qat_driver_path= "",fips_tar_file_path="",calgery_tar_file_path=""):
        """
        Initializes the CryptSetupManager with default paths and log storage.
        """
        self.logs_captured = []
        self.dts_setup_path = dts_setup_path  # Path where DTS is cloned
        self.dpdk_file_path = dpdk_file_path  # Path to the DPDK release tarball (e.g., dpdk-25.11-rc1.tar.xz)
        self.automation_folder_path = automation_folder_path # Path containing config_files, crypto_dep, qat_driver, etc.
        self.qat_driver_path = qat_driver_path #Path of QAT Driver
        self.calgery_tar_file_path = calgery_tar_file_path
        self.fips_tar_file_path = fips_tar_file_path
        self.git_user = git_user
        self.git_token = git_token
        self.dts_url = f"https://{git_user}:{git_token}@github.com/intel-sandbox/networking.dataplane.dpdk.dts.local.upstream.git".replace(" ","")  #For cloning DTS after CREDENTIAL.

        self.git_url_intel_ipsec = "https://github.com/intel/intel-ipsec-mb.git"
        self.intel_ipsec_path = ""
        self.config_file_name = "config_files"
        self.qat_driver_folder_name = "qat_driver"
        self.sw_crypto_driver_folder_name = "sw_crypto_driver"
        self.crypto_dep_folder_name = "crypto_dep"



    def clone_dts_repo(self):

        """
        Clones the private DTS repository using GitHub credentials.
        """
       
        path = os.getcwd()
        directory = os.listdir()
        if "networking.dataplane.dpdk.dts.local.upstream" in directory:
            self.run_command(["rm","-rf","networking.dataplane.dpdk.dts.local.upstream"],"Removing Existing Cloning")
        print("\n📍current path : "+str(path))
        
        self.run_command(["git", "clone", self.dts_url], "Cloning DTS repository")
        os.chdir("networking.dataplane.dpdk.dts.local.upstream")
        self.dts_setup_path =  os.getcwdb().decode()
        self.run_command(["git", "checkout","-b", "v25"], "Checking out DPDK version v25.03-rc3")

    def clone_intel_ipsc_repo(self):

        """
        Clones the private DTS repository using GitHub credentials.
        """
       
        path = os.getcwd()
        directory = os.listdir()
        if "intel-ipsec-mb" in directory:
            self.run_command(["rm","-rf","intel-ipsec-mb"],"Removing Existing Cloning")
        print("\n📍current path : "+str(path))
        
        self.run_command(["git", "clone", self.git_url_intel_ipsec], "Cloning Intel IPSEC")
        os.chdir("intel-ipsec-mb")
        self.intel_ipsec_path = os.getcwdb().decode()
        self.run_command(["git", "checkout","-b", "v25"], "Checkout for diffrent Branch")

    

    def crypto_execution_script(self):
        """
        Validates the required paths for DPDK and automation setup.
        This method should be called before executing any crypto-related test logic.

        Returns:
            bool: True if all paths are valid, False otherwise.
        """
        try:
            # Doing Validation for variable
            if not os.path.exists(self.dts_setup_path):
                error_msg = "❌ Please provide a valid DTS file path Where to Clone"
                self.logs_captured.append(error_msg)
      

            if not os.path.exists(self.dpdk_file_path):
                error_msg = "❌ Please provide a valid DPDK file path (e.g., dpdk-25.11-rc1.tar.xz)."
                self.logs_captured.append(error_msg)
                print(error_msg)

            if not os.path.exists(self.automation_folder_path):
                error_msg = "❌ Please provide a valid automation folder path containing required dependencies."
                self.logs_captured.append(error_msg)
                print(error_msg)
            
            if not self.git_token or self.git_token == "" or not self.git_user or self.git_user == "":
                self.logs_captured.append("Please Provide Correct Git username and Git Token Is very Important for cloning")

            if self.logs_captured:
                raise ValueError("One or more required paths are invalid.")
            


            ###########################################################STEP 1 PROCESS START #############################################################
            
            # WORKING FOR QAT DRIVERS
            cp_qat_driver_path = os.path.join(self.automation_folder_path,self.qat_driver_folder_name)
            qat_driver_file_name = os.path.basename(self.qat_driver_path)

            # Chanding Directory to QAT Driver Directory Have to Copy QAT File
            os.chdir(cp_qat_driver_path)
            print(os.getcwdb())
            if os.path.exists(os.path.join(cp_qat_driver_path, qat_driver_file_name)):
                self.run_command(["rm","-rf",qat_driver_file_name],"Removing If same file was there is QAT driver Folder")
            self.run_command(["cp",self.qat_driver_path,cp_qat_driver_path],f"Copying file QAT file := {qat_driver_file_name}")
            print(os.getcwdb())
            self.run_command(["tar","-xvf",qat_driver_file_name],f"Taring QAT driver flename : {qat_driver_file_name}")
            # self.run_command(["make","uninstall"],"CMD : 'Make' doing Uninstall")
            for file in os.listdir():
                self.print_separator(file)

            # Run the configure script to enable SR-IOV in host mode
            # This prepares the build system with specific features enabled
            self.run_command(["./configure" ,"--enable-icp-sriov=host"],"Run configure script with SR-IOV host mode; no extra env/context")

            # Compile the source code using 'make'
            # This builds the project based on the configuration set abov
            self.run_command(["make"],"Running Make CMD")

            # Install the compiled binaries
            # This installs the built software into the system (usually /usr/local or specified prefix
            self.run_command(["make", "install"],"Running Make CMD")

            #########################################################STEP 2 PROCESS START##################################################################
            crypto_driver_folder_path = os.path.join(self.automation_folder_path,self.sw_crypto_driver_folder_name)
            # Chanding Directory to CRYPTO Driver folder Directory Have to Copy QAT File
            os.chdir(crypto_driver_folder_path)
            print("crypto_driver_folder_path",os.getcwdb())

            # Clone the Intel IPSE repository
            # This pulls the source code from the remote Git repository
            self.clone_intel_ipsc_repo()

            # Print the current working directory for context
            # Useful for confirming where the repo was cloned
            self.print_separator(f"Within Folder {str(os.getcwdb())}")

            # Show the current Git branch
            # Helps verify that you're on the correct branch before building
            self.run_command(["git", "branch"], "Displaying current Git branch")

            # Build Intel IPSE with specific safety flags disabled
            # SAFE_LOOKUP, SAFE_DATA, and SAFE_PARAM are likely build-time safety checks
            # -j 30 enables parallel compilation using 30 threads for faster build
            self.run_command(
                ["make", "SAFE_LOOKUP=n", "SAFE_DATA=n", "SAFE_PARAM=n", "-j", "30"],
                "Building Intel IPSE with safety checks disabled and parallel jobs"
            )

            # Install the compiled Intel IPSE binaries
            # This installs the built components into the system (e.g., libraries, executables)
            self.run_command(["make", "install"], "Installing Intel IPSE binaries using 'make install'")

            # List contents of the 'lib' directory
            # This checks whether the expected library files were generated and placed correctly
            self.run_command(["ls", "lib"], "Verifying presence of compiled libraries in 'lib' directory")

            # Display all running processes
            # Useful for debugging or verifying if any related services or background processes are active
            self.run_command(["ps", "-ef"], "Listing all running processes for system inspection")

            #########################################################STEP 3 PROCESS START##################################################################            

            # WORKING ON CRYPTO_DEP FOLDER

            # Construct the path to the crypto dependency folder
            cp_crypto_dep_path = os.path.join(self.automation_folder_path, self.crypto_dep_folder_name)

            # Create the folder if it doesn't exist
            # This ensures the destination directory is available for file operations
            os.makedirs(cp_crypto_dep_path, exist_ok=True)

            # Change working directory to the crypto dependency folder
            os.chdir(cp_crypto_dep_path)
            self.print_separator(f"Current Path: {str(os.getcwdb())}")

            # Extract filenames from full tar file paths
            # These are the names of the FIPS and Calgary tarballs to be copied
            # fips_file_name = os.path.basename(self.fips_tar_file_path)
            # calgery_file_name = os.path.basename(self.calgery_tar_file_path)

            
            self.run_command(["tar", "-cvzf", self.fips_tar_file_path, "FIPS"],"FIPS UNTARING")

            #if Calgery Folder was not there It will create in root directory
            os.makedirs("/root/calgary/",exist_ok=True)
            self.run_command(["tar", "-cvzf", self.calgery_tar_file_path, "/root/calgary/"],"FIPS UNTARING")


            self.run_command(["rm", "-rf", "FIPS"],"Removing Unwanted Folder FIPS")


            # ######################################################START STEP 4 PROCESS FOR CRYPTO########################################################################

            # Starting the process :  EXECUTION FOR CRYPTO AFTER Verfication all requied details are here with us.
            self.print_separator("Starting prcoess")
            
            # While Running this CMD : We can go to path where we have to Clone DTS 
            os.chdir(self.dts_setup_path)

            # Clone : Cloning DTS
            self.clone_dts_repo()

            self.print_separator("Fetching Current List of Directory")

            print(os.listdir())

            # This Variable having DTS :CONF Folder Location
            dts_conf_path = os.path.join(self.dts_setup_path,"conf")
            if os.path.exists(dts_conf_path):
                # Checking That file if already folder if Yes then deleting removing again creating bec Id ont requiredy what previously
                # Ex/root/automation/config_files

                # COPYING FILE :
                cp_config_folder_path = os.path.join(self.automation_folder_path,self.config_file_name)

                # It wil ensure If folder was not there then it will create folder 
                # Going Within folder 
                # If folder was alread there then Removing all the file withing Folder
                os.makedirs(cp_config_folder_path,exist_ok=True)
                os.chdir(cp_config_folder_path)
                self.print_separator(f"Current Path {str( os.getcwdb().decode() )}")
                
                    

                # NOW Going back to DTS CONF folder Location ( dts_conf_path )
                os.chdir(dts_conf_path)
                self.print_separator(f"Back to DTS CONF FOLDER {str( os.getcwdb().decode() )}")

                # START COPING ALL THE FILE RELATED  TO DTS
                for fileName in os.listdir():   
                    if ("crbs" in fileName[:4])or ("ports" in fileName[:5])or ("crypto" in fileName[:6]) :
                        if os.path.exists(fileName):
                            self.run_command(["rm","-rf",fileName],f"Removing File is already avaialable : {fileName}")
                        self.run_command(["cp",fileName, cp_config_folder_path],f"Coping a file {fileName}")
                
                # Going Back from conf file one step back 
                os.chdir("..")
                self.run_command(["cp","execution.cfg", cp_config_folder_path],f"Coping a file execution.cfg")
                self.run_command(["cp","perf.sh", cp_config_folder_path],f"Coping a file perf.sh")
                

                self.run_command(["ls",cp_config_folder_path],f"Showing file which is Copied : directory {cp_config_folder_path}")
                self.print_separator("File Are Copied")
                # Now We are Copying File Which We will Process , Further.

            # GOING Within dep Folder for Taring DPDK EXECUTION SETUP 
            os.chdir(os.path.join(self.dts_setup_path,"dep"))
            self.print_separator(f"Current Path {str( os.getcwdb().decode() )}")
            # Coping DPDK FILE DEP folder
            self.run_command(["cp",self.dpdk_file_path,"."])
            dpdk_file_name = os.path.basename(self.dpdk_file_path)
            self.print_separator(f"Copied DPDK_FILE : {dpdk_file_name}")

            # Running for taring DPDK file
            self.run_command(["tar","-xvf",dpdk_file_name],f"Taring Dpdk_FILE : => {dpdk_file_name}")

            # While doing this it will remove dpdk-25.11-rc1.tar.xz => dpdk-25.11-rc1 
            if os.path.exists("dpdk"):
                self.run_command(["rm","-rf","dpdk"],"If Dpdk is previously available then delet it")
            
            # Renaming EX(DPDK-25.11-rc1 to dpdk) File into 
            
            for file_name in os.listdir():
                if ( file_name in dpdk_file_name) and (len(file_name)< len(dpdk_file_name)):
                    self.run_command(["mv",file_name,"dpdk"],f"Renaming file {file_name} :=: 'dpdk' ")
                    break
            
            self.run_command(["tar","-cvzf","dpdk.tar.gz","dpdk"])   
            self.run_command(["rm","-rf",dpdk_file_name], "Removing Extra file after Taring")

            return True

        except FileNotFoundError as e:
            error_msg = f"❌ File not found: {str(e)}"
            print(error_msg)
            return False, error_msg
        except subprocess.CalledProcessError as e:
            error_msg = f"❌ Subprocess error: {e.output if e.output else str(e)}"
            self.logs_captured.append({
                "errors": error_msg,
                "traceback": traceback.format_exc()
            })
            print(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            self.logs_captured.append({
                "errors": error_msg,
                "traceback": traceback.format_exc()
            })
            print(error_msg)
            return False, error_msg
