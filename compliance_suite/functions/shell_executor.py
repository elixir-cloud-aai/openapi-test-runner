"""Module compliance_suite.functions.shell_executor.py

This module contains class definition for Shell Executor which will run shell commands to calculate the expected
outcome from TES servers
"""

import subprocess
import sys
from typing import List


class ShellExecutor():
    """Shell Executor class is used to execute shell commands"""

    def execute_command(
            self,
            command: List[str],
            command_file_path: str,
            local_file_path: str
    ) -> str:
        """Execute command in system OS to calculate the desired result on a local file at local_file_path"""

        # Replace "Cat" command if Windows OS. Making the TES Compliance Suite OS independent
        if sys.platform == "win32":
            command = ["type" if item == "cat" else item for item in command]
            local_file_path = local_file_path.replace("/", "\\")

        # Replace container file path with local file path to perform shell command on local file
        command = [local_file_path if item == command_file_path else item for item in command]

        out = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, text=True)
        return out.communicate()[0]
