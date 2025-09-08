import platform


def os_checker():
    system = platform.system()
    if system == "Windows":
        return "dlv.exe"
    elif system == "Darwin":
        return "dlv2.1.2-macos"
    elif system == "Linux":
        raise ValueError(f"Linux, no dlv available in project")
    else:
        raise ValueError(f"Unknown operating system: {system}")