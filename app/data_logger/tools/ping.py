import platform
import re
import subprocess


def ping(host: str, timeout: int) -> float:
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = "-n" if platform.system().lower() == "windows" else "-c"

    # Building the command. Ex: "ping -c 1 google.com"
    command = ["ping", param, "1", host, "-W", str(timeout)]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    raw_str = process.communicate()[0].decode("utf-8")

    if process.returncode == 0:
        match = re.search(r"time=(\d.+) ms", raw_str)
        if match:
            return float(match.group(1))
        else:
            raise ValueError("Could not parse ping output: " + repr(raw_str))
    else:
        return float("nan")
