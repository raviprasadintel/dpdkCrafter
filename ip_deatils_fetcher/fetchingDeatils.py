
#!/usr/bin/env python3
"""
Sequential SSH probe: ping -> SSH -> fetch OS details + remote DPDK devbind output.
Input: Python list of [ip, username, password]
Output: Python list of dicts per host result.
"""

import subprocess
import sys
import platform
import time
import os
import re
import platform
import subprocess

from functools import wraps
# Ensure paramiko is installed
def ensure_paramiko():
    try:
        import paramiko  # noqa: F401
    except ImportError:
        print("[INFO] Installing paramiko...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])

ensure_paramiko()
import paramiko
from paramiko.ssh_exception import AuthenticationException, SSHException, NoValidConnectionsError

PING_COUNT = 1
PING_TIMEOUT_SEC = 3
SSH_TIMEOUT_SEC = 10
ERROR_LOGS = []  # store error strings for later diagnostics




# --------------------------------------------------------------------------------------------------
def ping_host(ip: str) -> bool:
    """Ping host using system ping command (ICMP)."""
    system = platform.system().lower()
    if system == "windows":
        cmd = ["ping", "-n", str(PING_COUNT), "-w", str(PING_TIMEOUT_SEC * 1000), ip]
    else:
        cmd = ["ping", "-c", str(PING_COUNT), "-W", str(PING_TIMEOUT_SEC), ip]

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.returncode == 0
    except Exception as e:
        ERROR_LOGS.append(f"ping_host error: {e}")
        return False


def connect_ssh(ip: str, username: str, password: str):
    """Connect to SSH using paramiko."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, username=username, password=password, timeout=SSH_TIMEOUT_SEC)
        return client
    except (AuthenticationException, NoValidConnectionsError, SSHException) as e:
        msg = f"[SSH ERROR] {ip}: {e}"
        print(msg)
        ERROR_LOGS.append(msg)
        return None
    except Exception as e:
        msg = f"[SSH OTHER] {ip}: {e}"
        print(msg)
        ERROR_LOGS.append(msg)
        return None


def run_cmd(ssh: paramiko.SSHClient, cmd: str, timeout: int = 10):
    """
    Run command on remote host and return (exit_status, stdout_text, stderr_text).
    Use bash -lc to get a login-like shell where exports and PATH are respected.
    """
    try:
        # Make sure we invoke a shell that processes exports, conditionals, etc.
        shell_cmd = f"bash -lc {repr(cmd)}"
        stdin, stdout, stderr = ssh.exec_command(shell_cmd, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="ignore").strip()
        err = stderr.read().decode("utf-8", errors="ignore").strip()
        status = stdout.channel.recv_exit_status()
        return status, out, err
    except Exception as e:
        ERROR_LOGS.append(f"run_cmd error for '{cmd}': {e}")
        return 1, "", str(e)


def detect_os(ssh: paramiko.SSHClient) -> str:
    """Detect OS details from remote."""
    status, out, err = run_cmd(ssh, "test -f /etc/os-release && cat /etc/os-release")
    if status == 0 and out:
        for line in out.splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.split("=", 1)[1].strip().strip('"')
    # Fallback
    status, out, err = run_cmd(ssh, "uname -a")
    return out or "Unknown"

def is_header_title(line: str) -> bool:
    return bool(line.strip())

def is_underline(line: str) -> bool:
    s = line.strip()
    return len(s) > 0 and set(s) == {"="}


def clone_dpdk_repo_remote(ssh: paramiko.SSHClient, timeout: int = 120):

    # Export proxies only within this shell invocation
    proxy_env = (
        "export no_proxy='localhost,127.0.0.1,intel.com,ger.corp.intel.com'; "
        "export ftp_proxy='http://proxy-iind.intel.com:911'; "
        "export http_proxy='http://proxy-iind.intel.com:911'; "
        "export https_proxy='http://proxy-iind.intel.com:912'; "
    )

    # Ensure git is present
    status, out, err = run_cmd(ssh, "command -v git || echo 'GIT_NOT_FOUND'", timeout=10)
    if "GIT_NOT_FOUND" in (out + err):
        return "FAILURE", "git not found on remote host. Please install git."

    # Create a working directory and clone/update there
    # We use ~/fetch_details on the remote
    prep_cmd = (
        "set -e; "
        "mkdir -p ~/fetch_details; "
        "cd ~/fetch_details; "
        "if [ -d dpdk ]; then echo 'dpdk exists; pulling'; cd dpdk; git pull --ff-only; cd ..; "
        "else echo 'cloning dpdk'; git clone https://github.com/DPDK/dpdk.git; fi; "
        "echo 'ready';"
    )

    status, out, err = run_cmd(ssh, proxy_env + prep_cmd, timeout=timeout)
    if status != 0:
        return "FAILURE", f"prep failed: {err or out}"

    # Run devbind script to list devices
    devbind_cmd = "cd ~/fetch_details/dpdk && ./usertools/dpdk-devbind.py -s"
    status, out, err = run_cmd(ssh, proxy_env + devbind_cmd, timeout=timeout)
    if status != 0 and not out:
        return "FAILURE", f"dpdk-devbind.py failed: {err}"
    return "SUCCESS", out or err



def network_filter_data(lines):
    import re
    result = []
    started = False       
    collecting = False 
    
    def is_header_title(line: str) -> bool:
        return bool(line.strip())

    def is_underline(line: str) -> bool:
        s = line.strip()
        return len(s) > 0 and set(s) == {"="}

    i = 0
    # Accept fields in any order, and make both numa/if/unused optional.
    # We still require drv=... at minimum.
    device_line_pattern_flexible = re.compile(
        r"""^
        (?P<pci>[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7])\s+     # PCI
        '(?P<name>[^']+)'\s+                                                # name
        (?:
            (?:numa_node=(?P<numa>\d+)\s+)|
            (?:if=(?P<iface>\S+)\s+)|
            (?:unused=(?P<unused>\S+)\s+)|
            (?:drv=(?P<driver>\S+)\s+)
        )+                                                                  # one or more of these fields, any order
        (?:\*Active\*)?                                                     # optional flag (with or without spaces)
        \s*$                                                                # end
        """,
        re.VERBOSE
    )
    while i < len(lines):
        line = lines[i]
        if not started and "Network devices using kernel driver" in line:
            started = True
            i += 1
            if i < len(lines) and is_underline(lines[i]):
                collecting = True
                i += 1
                continue
            else:
                break
        if collecting:

            if is_header_title(line) and (i + 1) < len(lines) and is_underline(lines[i + 1]):
                break
            # result.append(line)
            m = device_line_pattern_flexible.match(line.rstrip("\r"))
            if m:
                d = m.groupdict()
                d["active"] = "*Active*" in line
              
                result.append(d)

        i += 1
    return result

def ip_details_scrapper(ssh,timeout =10, search=""):

    status, out, err = run_cmd(ssh,"ip -br a", timeout=timeout)
    if status != 0:
        return []
    interface_status = []

    for line in out.splitlines():
        match = re.match(r'^(\S+)\s+(UP|DOWN)(?:\s+(.*))?$', line)
        if not match:
            continue  # Skip lines that don't match the expected format

        name, status, ip_info = match.groups()
        ip_info = ip_info.strip() if ip_info else ""

        # Skip if IPv4 is present
        if re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}/\d+\b', ip_info):
            continue

        interface_status.append({'name': name, 'status': status})

    # Filter by search term if provided
    return [iface for iface in interface_status if search in iface['name']] if search else interface_status

def fetchching_bus_info(ssh,timeout=10):
    print("\n🔍 Fetching PCI Bus Info...\n")
    try:
        status, out, err = run_cmd(ssh,"lshw -c network -businfo", timeout=timeout)
        
        lines = out.strip()[1:]  # Skip the header
        pattern = r'^(pci@\S+)\s+(\S+)\s+network\s+(.*)$'
        parsed_info = []
        for line in lines.splitlines():
            match = re.match(pattern, line.strip())
            if match:
                bus, device, description = match.groups()
                parsed_info.append({
                    'bus': bus,
                    'device': device,
                    'description': description
                })
        bus_info = parsed_info
        return bus_info
    except Exception as e:
        print(e)
        ERROR_LOGS.append(f"❌ Error parsing bus info: {e}")
        return []
def extract_interface_names( log_data):
    """
    Extracts all network interface names from NIC link status messages.

    Args:
        log_data (str): The full dmesg output as a string.

    Returns:
        List[str]: A list of interface names (e.g., 'ens801f1np1').
    """
    try:
        pattern = r'\b(\w+): NIC Link is (?:Down|up)\b'
        return re.findall(pattern, log_data, re.MULTILINE)
    except Exception as e:
        ERROR_LOGS.append(f"❌ Error extracting interface names: {e}")
        return []
def update_interface_pairs(interface_list, existing_pairs):
    """
    Creates non-repeating interface pairs from the input list.
    Only adds a pair if it doesn't already exist in either order.

    Args:
        interface_list (list): List of interface names.
        existing_pairs (list): List of existing pairs (each pair is a list of two interfaces).

    Returns:
        list: Updated list of valid interface pairs.
    """
    try:
        updated_pairs = existing_pairs.copy()
        for i in range(0, len(interface_list) - 1, 2):
            pair = [interface_list[i], interface_list[i + 1]]
            reverse_pair = [interface_list[i + 1], interface_list[i]]
            if pair not in updated_pairs and reverse_pair not in updated_pairs:
                updated_pairs.append(pair)
        return updated_pairs
    except Exception as e:
        ERROR_LOGS.append(f"❌ Error updating interface pairs: {e}")
        return existing_pairs
    
def fetchingPairDetailsFromInterface(ssh,timeout =10,interFaceDetails=[]):
    """
    Processes all UP interfaces and attempts to fetch pairing details using `ethtool` and `dmesg`.
    Extracts interface names from NIC link messages and avoids redundant processing.
    Updates the pairingInterface list with interfaces that show link activity.
    """
    try:

        status, out, err = run_cmd(ssh,"dmesg -c ", timeout=timeout)
        status, out, err = run_cmd(ssh,"dmesg -c ", timeout=timeout)

        pairingInterface = []
    
        for details in interFaceDetails:
            try:
                interface = details['name']
                status = details['status']

                print(f"🔍 Processing Interface: {interface} | Status: {status}")

                run_cmd(ssh,f"ethtool -r {interface}", timeout=timeout)
                success, out, err = run_cmd(ssh,"dmesg -c ", timeout=timeout)
                print(out)

                if status != 0:
                    continue
                interface_pair = extract_interface_names(out)
                pairingInterface = update_interface_pairs(interface_pair, pairingInterface)

               
            except Exception as e:
                ERROR_LOGS.append(f"❌ Error processing interface {details.get('name', 'unknown')}: {e}")

        # Final cleanup
        status, out, err = run_cmd(ssh,"dmesg -c ", timeout=timeout)
        status, out, err = run_cmd(ssh,"dmesg -c ", timeout=timeout)

        print("\n🔗 Final Interface Pairings:")
        for pair in pairingInterface:
            print(f"  ✅ {pair[0]} ↔ {pair[1]}")
        return   pairingInterface
    except Exception as e:
        ERROR_LOGS.append(f"❌ Error in fetchingPairDetailsFromInterface: {e}")  
        return []
def process_hosts(hosts):
    results = []
    for ip, username, password in hosts:
        record = {
            "ip": ip,
            "username": username,
            "reachable": "no",
            "ssh": "no",
            "Supported OS": "",
            "error": "",
            "dpdk_devbind_s": "",
        }
        print(f"[INFO] Checking {ip}...")
        if not ping_host(ip):
            record["error"] = "Ping failed"
            results.append(record)
            continue

        record["reachable"] = "yes"
        ssh = connect_ssh(ip, username, password)
        if not ssh:
            record["error"] = "SSH failed"
            results.append(record)
            continue

        try:
            # OS detection
            record["ssh"] = "yes"
            record["Supported OS"] = detect_os(ssh)

            # Remote DPDK probe
            status, logs = clone_dpdk_repo_remote(ssh, timeout=180)
            if status == "SUCCESS":
                data = list(network_filter_data(logs.splitlines()))
                enterface_name = [{"name":val.get("name"),"pci":val.get("pci")} for val in data if "name" in val] 
                record["dpdk_devbind_s"] = enterface_name

                interFaceDetails = ip_details_scrapper(ssh=ssh)
                record["ip_details"] = interFaceDetails
                record["bus_info"] = fetchching_bus_info(ssh=ssh)

                pair_info = fetchingPairDetailsFromInterface(ssh=ssh,interFaceDetails=interFaceDetails) 
                record["pair_info"] = pair_info

            else:
                record["error"] = (record["error"] + "; " + logs).strip("; ")

        finally:
            try:
                ssh.close()
            except Exception:
                pass

        results.append(record)
    return results


# if __name__ == "__main__":
#     # Example input list
#     hosts_input = [
#         ["10.138.182.136", "root", "tester"],
#         # ["10.138.182.176", "root", "tester"],
#     ]
#     start = time.time()
#     results = process_hosts(hosts_input)
#     print("\n=== RESULTS ===")
#     for r in results:
#         print(r)
#     print(f"[INFO] Completed in {time.time() - start:.1f}s")

#     # Optional: show collected error logs, if any
#     if ERROR_LOGS:
#         print("\n=== ERROR LOGS ===")
#         for e in ERROR_LOGS:
#             print(e)
