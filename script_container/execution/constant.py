
# --------------------------------------------------------------------------------------------------
#                               Constant : dut_ports_config.py   (START)
# --------------------------------------------------------------------------------------------------

port_config_prompt_update = """# DUT Port Configuration
# [DUT IP]
# ports=
#     pci=Pci BDF,intf=Kernel interface;
#     pci=Pci BDF,mac=Mac address,peer=Tester Pci BDF,numa=Port Numa
#     pci=Pci BDF,peer=IXIA:card.port
#     pci=Pci BDF,peer=TREX:port
#     pci=Pci BDF,peer=Tester Pci BDF,tp_ip=$(IP),tp_path=$({{PERL_PATH}});
#     pci=Pci BDF,peer=Tester Pci BDF,sec_port=yes,first_port=Pci BDF;
# [VM NAME] virtual machine name; This section is for virtual scenario
# ports =
#     dev_idx=device index of ports info, peer=Tester Pci BDF
[{}]
ports =
{}
"""

port_config_auth_prompt = (
    "\n🔐 **Authentication Required**\n"
    "----------------------------------\n"
    "👤 Username : {username}\n"
    "🌐 IP Address : {ip}\n"
    "\n💬 Please enter your password to proceed...\n"
)
port_config_auth_confirm = (
    "\n🔐 **Authentication Confirmation**\n"
    "--------------------------------------\n"
    "👤 Username : {username}\n"
    "🌐 IP Address : {ip}\n"
    "\n🔁 Please re-enter your password to confirm...\n"
)
port_config_success = "\n✅ Password confirmed successfully!\n"
port_config_mismatch = "\n❌ Passwords do not match or are empty. Attempts left: {attempts_left}\n"
port_config_fail = "🚫 Maximum attempts reached. Authentication failed.\n"


# --------------------------------------------------------------------------------------------------
#                              Constant : dut_ports_config.py   (END)
# --------------------------------------------------------------------------------------------------
OS_DETAILS= [
    {
        "OS":"Linux"
    },
    {
        "OS":"RHEL"
    }
]