import re
import pyautogui
import time
import os

def open_powershell():
    pyautogui.hotkey('win', 'r')  # Opens Run dialog
    time.sleep(1)
    pyautogui.write('powershell\n', interval=0.1)
    time.sleep(2)  # Wait for PowerShell to open

def run_command_in_powershell(command):
    pyautogui.write(command + '\n', interval=0.1)
    time.sleep(2)  # Wait for command to execute

def open_directory_in_vscode(directory):
    run_command_in_powershell(f"code {directory}")

def handle_commands_from_text(text):
    shell_pattern = r"<<<shell>>>(.*?)<<<endshell>>>"
    python_pattern = r"<<<python \(([\w/\\]+\.py)\)>>>(.*?)<<<endpython>>>"  # Updated pattern to include directory structure

    shell_matches = re.findall(shell_pattern, text, re.DOTALL)
    python_matches = re.findall(python_pattern, text, re.DOTALL)
    
    # Exit clause: Check if there are no matches and exit if true
    if not shell_matches and not python_matches:
        print("No script or Python code found in the text.")
        return  # Exit the function early
    
    current_directory = "C:/Lagrange"  # Set a default or initial directory if needed

    open_powershell()
    run_command_in_powershell(f'cd {current_directory}\n')
    for command in shell_matches:
        if "cd" in command:
            new_directory = command.split()[-1].strip()
            if new_directory.startswith('..'):
                current_directory = '\\'.join(current_directory.split('\\')[:-1])
            elif ':' in new_directory:
                current_directory = new_directory  # Full path
            else:
                current_directory = os.path.join(current_directory, new_directory)
        run_command_in_powershell(command)

    run_command_in_powershell(f"cd {current_directory}")

    if python_matches:
        for full_path, code in python_matches:
            filepath = os.path.join(current_directory, full_path)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as file:
                file.write(code.strip())
            print(f"Code written to {filepath}")

    if current_directory:
        open_directory_in_vscode(current_directory)

