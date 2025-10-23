import re
import os
import time
import subprocess
import platform
from execution.bus_info_details import PairingManagerInfo


# #######################################   Main Execution Block   ###########################################################

if __name__ == "__main__":
    print("\n🚀 Starting Interface Pairing Manager...\n")

    try:
        # Initialize and run pairing manager
        os.chdir("/root/testing/dts_setup/")
        print("🧩 Initializing PairingManagerInfo object...")
        obj = PairingManagerInfo()

        print("\n🔍 Fetching Interface and Bus Pairing Information...\n")
        obj.fetchingInterFacePairingInfo()

        print("\n🔗 Fetching Interface Connection Details...\n")
        obj.fetchingPairDetailsFromInterface()

        print("\nMapping Interface With Bus Info")
        interfaceDetails = obj.mapInterfaceToBus()

        print(interfaceDetails)

    except Exception as e:
        print(f"\n❌ An error occurred during execution: {e}\n")

    print("\n✅ Script Execution Completed Successfully.\n")