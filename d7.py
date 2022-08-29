#!/usr/bin/env python3

__description__ = """
The specified file and all files contained in the specified directory (recursive=False) will be decompressed with 7-Zip. 
Files are not selected by extension. 
It also requires 7-Zip executable and library to run.
"""
__date__ = "2022/08/26"
__version__ = "1.0.4"
__author__ = "ikmt"

"""
_________________________________________________________________
Need 7-Zip executable and library for working
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Winsows: 7z.exe, 7za.exe
Linux: 7zz, 7zzs, 7zr
_________________________________________________________________
Required version of Python
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Available since Python 3.6
v3.6 - formatted string literal (f-string)
v3.5 - os.scandir()
v3.2 - logging.Formatter() (Changed in version 3.2:added style parameter)
_________________________________________________________________
Test environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
OS: windows 10
pip version: 20.0.2
Python version: 3.7.6
7-Zip version: 19.0.0 (x64)
_________________________________________________________________
Command line examples
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
python d7.py -i ./filename.zip
python d7.py -i ./filename1.zip -i ./filename2.7z -i ./dirname
python d7.py -i ./filename.zip -o C:/Users/xxx/Desktop/dirname
python d7.py -i ./filename.zip -p infected
python d7.py -i ./filename.zip -p infected -c 65001
_________________________________________________________________
Changelog
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2022-08-26 v1.0.4 fixed 30% of the code
2022-08-26 v1.0.3 fixed 7-Zip command build (Apply password if extension is missing)
2022-08-04 v1.0.2 fixed terminal output format
2022-07-25 v1.0.1 fixed 7-Zip command build
2022-07-18 v1.0.0 release
"""

import argparse
import itertools
import logging
import os
import subprocess
import sys


# Constants
SCRIPT_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_7ZIP_PATH = "./7z.exe"


# Configuring logging
log_format_string = "{asctime}[{levelname:.1}] {message}"
date_format_string = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(
    style="{", 
    fmt=log_format_string, 
    datefmt=date_format_string
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main():
    # Output log to terminal
    log_stream_handler = logging.StreamHandler()
    log_stream_handler.setFormatter(formatter)
    logger.addHandler(log_stream_handler)
    # Check command line arguments
    args = check_argument()
    exe_path = os.path.abspath(args.exe)
    files = get_file_list(args.input)
    work_dir = create_dir(args.output)
    # Table of return values ​​and their meaning
    return_code_table = {
        0: "No error", 
        1: "Warning", 
        2: "Fatal error", 
        7: "Command line error", 
        8: "Not enough memory for operation", 
        255: "User stopped the process"
    }
    # Save processing results
    statistics = dict.fromkeys([
        "total",
        "failure",
    ], 0)
    statistics['total'] = len(files)
    # Start message
    logger.info(f"[{'START':<9}] {__file__}")

    for i in range(0, statistics["total"]):
        logger.info(f"[{'IDX/TOTAL':<9}] {i + 1:05}/{statistics['total']:05}")
        # Create separate directory
        name, ext = os.path.splitext(os.path.basename(files[i]))
        base_dir_path = work_dir if(work_dir) else os.path.dirname(files[i])
        separate_dir = create_dir(os.path.join(base_dir_path, name))
        # Function to call 7-Zip
        rtn = seven_zip(exe_path, files[i], separate_dir, args.password, args.codepage)
        if(rtn.returncode != 0):
            statistics["failure"] += 1
        logger.debug(f"[{'CMD':<9}] {rtn.args}")
        logger.info(f"[{'IN_FILE':<9}] {files[i]}")
        logger.info(f"[{'OUT_DIR':<9}] {separate_dir}")
        logger.log(
            getSeverity(rtn.returncode),
            f"[{'CMDSTATUS':<9}] {rtn.returncode},{return_code_table[rtn.returncode]}"
        )

    # Result
    logger.info(f"[{'RESULT':<9}] TOTAL:{statistics['total']:^5}"
        + f",SUCCESS:{statistics['total'] - statistics['failure']:^5}"
        + f",FAILURE:{statistics['failure']:^5}")
    # End message
    logger.info(f"[{'END':<9}] {__file__}")

    return 0


def check_argument():
    # If specified with a relative path, 
    # it will be based on the script directory.
    save_current_path = os.getcwd()
    os.chdir(SCRIPT_DIR_PATH)
    default_exe_path = os.path.abspath(DEFAULT_7ZIP_PATH)
    os.chdir(save_current_path)

    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument("-c", "--codepage",
        type=int,
        default=None,
        help="specify the code page identifier(utf-8:65001, shift-jis:932, EUC-JP:20932, etc). "
            + "used when the path of the decompressed ZIP file is garbled."
    )
    parser.add_argument("-i", "--input",
        action="append",
        required=True,
        type=str,
        help="specify the compressed file or directory containing compressed files."
    )
    parser.add_argument("-o", "--output",
        type=str,
        help="specify the output directory."
    )
    parser.add_argument("-p", "--password",
        type=str,
        default=None,
        help="specify the password to decrypt the encrypted compressed files (ZIP, 7z, RAR)."
    )
    parser.add_argument("-v", "--version",
        action="version",
        version="%(prog)s " + __version__
    )
    parser.add_argument("-x", "--exe",
        type=str,
        default=default_exe_path,
        help="specify the 7-Zip executable path."
    )
    args = parser.parse_args()

    # Check the 7-Zip executable file path.
    if(not os.path.isfile(args.exe)):
        logger.error(f"The 7-Zip executable file ({args.exe}) does not exist.")
        exit(-2)
    main_executables = ["7z", "7za", "7zz", "7zzs", "7zr"]
    name, ext = os.path.splitext(os.path.basename(args.exe))
    if(not name in main_executables):
        logger.error(f"Invalid 7-Zip executable file name ({name}).")
        exit(-2)

    return args


def get_file_list(path_list, recursive=False):
    """Returns a list of files in the specified path."""
    if(isinstance(path_list, str)):
        path_list = [path_list]

    files = []
    # Recursive directory listing
    def search_sub_dir(path):
        with os.scandir(path) as it:
            for entry in it:
                if(not entry.name.startswith(".") and entry.is_file()):
                    files.extend([entry.path])
                elif(not entry.name.startswith(".") and entry.is_dir()):
                    if(recursive):	
                        search_sub_dir(entry.path)

    for path in path_list:
        absolute_path = os.path.abspath(path)
        if(os.path.isfile(absolute_path)):
            files.extend([absolute_path])
        elif(os.path.isdir(absolute_path)):
            search_sub_dir(absolute_path)
        else:
            files = None
            break

    if(files is None):
        logger.error("Invalid input file path.")
        sys.exit(-2)
    elif(len(files) <= 0):
        logger.error("File does not exist.")
        sys.exit(-2)

    return files


def create_dir(dir_path):
    """Create a directory
    Add a suffix if the same filename already exists.
    """
    abs_dir_path = None
    if(dir_path):
        abs_dir_path = os.path.abspath(dir_path)

        # Add a suffix if the same filename already exists.
        if(os.path.isfile(abs_dir_path)):
            for i in itertools.count(1):
                if(not os.path.isfile(abs_dir_path + f"({i})")):
                    abs_dir_path += f"({i})"
                    break
        
        if(not os.path.isdir(abs_dir_path)):
            os.makedirs(abs_dir_path)

    logger.debug(f"[{'CREATEDIR':<9}] {'None' if(abs_dir_path is None) else abs_dir_path}")
    
    return abs_dir_path


def seven_zip(exe_path, file_path, out_dir=None, password=None, code_page=None):
    """Build and run the command for 7-Zip."""
    name, ext = os.path.splitext(os.path.basename(file_path))
    # Build a command-line
    cmd = [exe_path]
    cmd += ["x"]
    cmd += ["-y"]
    cmd += ["-aoa"]
    cmd += ["-o" + str(out_dir)]
    # Set password
    # If the extension does not exist, it is assumed to be '.7z'.
    if(ext in [".zip", ".7z", ".rar", ""] and password is not None):
        cmd += ["-p" + str(password)]
    # Set code page identifier
    if(ext in [".zip", ".tar"] and code_page is not None):
        cmd += ["-mcp=" + str(code_page)]
    cmd += [str(file_path)]
    # Use 7zip on the command line
    # Returns standard output and standard error as a return value
    rtn = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # 7zip returncode
    # 0: No error
    # 1: Warning
    # 2: Fatal error
    # 7: Command line error
    # 8: Not enough memory for operation
    # 255: User stopped the process
    return rtn


def getSeverity(level):
    """Returns the severity for the specified level."""
    if(level == 0):
        return logging.INFO
    elif(level == 1 or level == 255):
        return logging.WARNING
    else:
        return logging.ERROR


# Execute a script from the Command Line
if __name__ == "__main__":
    main()
