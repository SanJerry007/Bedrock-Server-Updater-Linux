# Minecraft Bedrock Server Update Script

This PowerShell script is designed to automate the process of updating multiple Minecraft Bedrock servers. It checks for the latest server version, backs up essential configuration files, applies the update, and restarts the servers to ensure they are running the latest version. The script is easy to use and can be set up to run at regular intervals via Task Scheduler.

## Features

- **Automatic Update Checking**: Downloads the latest Minecraft Bedrock server version from the official Minecraft website.
- **Configuration Backup**: Backs up critical server configuration files (`server.properties`, `allowlist.json`, `permissions.json`) every time the script runs.
- **Server Updating**: Applies the latest server update if available.
- **Server Restarting**: Restarts all servers after applying the update.
- **Dynamic Backup Location**: Automatically creates a `backup` directory in the same location where the script is run.
- **Logging**: Logs every action to a `update_log.txt` file, providing a detailed record of the backup, update, and restart processes.
- **Enhanced Error Handling**: Includes robust error handling for web requests and file operations.

## Getting Started

### Prerequisites

- Windows operating system with PowerShell.
- Minecraft Bedrock servers set up on your system.

### Installation

1. **Clone or Download the Repository**:
   - Clone this repository to your local machine or download the `UpdateMinecraftServers.ps1` script.

2. **Place the Script**:
   - Copy the `UpdateMinecraftServers.ps1` script to a directory near your Minecraft Bedrock servers. For example, you can place it in `C:\MinecraftScripts`.

3. **Run the Script**:
   - Open PowerShell and navigate to the directory where you placed the script.
   - Run the script by executing the following command:
     ```powershell
     .\UpdateMinecraftServers.ps1
     ```
   - The script will generate a `server_paths.conf` file in the same directory.

4. **Edit the Configuration File**:
   - Open the `server_paths.conf` file and add the paths to your Minecraft Bedrock server directories. Each line should contain the path to one server directory. For example:
     ```
     C:\MinecraftServers\bedrock-server1
     C:\MinecraftServers\bedrock-server2
     ```

5. **Run the Script Again**:
   - After editing the `server_paths.conf` file, run the script again. It will:
     - Backup your server configuration files.
     - Check for and apply any updates.
     - Restart your servers.

### Running the Script at Intervals

You can set up the script to run at regular intervals using Task Scheduler:

1. **Open Task Scheduler**:
   - Press `Win + R`, type `taskschd.msc`, and press `Enter`.

2. **Create a New Task**:
   - In Task Scheduler, click on `Create Task` in the right-hand pane.

3. **General Settings**:
   - Give your task a name (e.g., "Minecraft Server Update").
   - Choose "Run whether user is logged on or not."
   - Check "Run with highest privileges."

4. **Triggers**:
   - Go to the "Triggers" tab and click `New`.
   - Set the task to run at your desired interval (e.g., daily, weekly).

5. **Actions**:
   - Go to the "Actions" tab and click `New`.
   - For "Action," select "Start a program."
   - In the "Program/script" field, enter `powershell.exe`.
   - In the "Add arguments (optional)" field, enter:
     ```plaintext
     -ExecutionPolicy Bypass -File "C:\Path\To\Your\Script\UpdateMinecraftServers.ps1"
     ```
     Replace `C:\Path\To\Your\Script\` with the actual path to the script.

6. **Conditions**:
   - Go to the "Conditions" tab and adjust settings as needed (e.g., "Start the task only if the computer is idle").

7. **Finish**:
   - Click `OK` to create the task. Enter your credentials if prompted.

The script will now run automatically at the intervals you specified.

## Logging

The script creates a `update_log.txt` file in the same directory as the script. This log file records all actions taken by the script, including:
- Backups performed
- Updates downloaded and applied
- Servers restarted
- Any errors encountered

## Example Directory Structure

If you run the script from `C:\MinecraftScripts`, the script will create the following structure:

- **Backup Directory**: `C:\MinecraftScripts\backup`
- **Update Directory**: `C:\MinecraftScripts\update`
- **Log File**: `C:\MinecraftScripts\update_log.txt`
- **Config File**: `C:\MinecraftScripts\server_paths.conf`

## Troubleshooting

- **Web Request Errors**: If the script encounters issues while downloading the update, it will log the specific error message. Ensure you have an active internet connection and that the Minecraft website is accessible.
- **File Not Found**: If a configuration file like `allowlist.json` is missing, the script will log that it was not found but will continue running.

## Contributions

Contributions to improve this script are welcome! Please feel free to fork this repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License.
