# Minecraft Bedrock Server Updater for Linux

This is a modified version of [Bedrock-Server-Updater](https://github.com/Bachperson/Bedrock-Server-Updater), which is designed to automate the process of updating Minecraft Bedrock Servers (BDS) on the **Linux** platform. I rewrite the whole code in Python, optimize the logic, and add some new features to make it easier to use.

## Basic Usage

Just run the `auto_update.py` script and pass the directory to the server for update:

```shell
python auto_update.py <PATH_TO_SERVER>
```

To output the log to a file, just add a `tee` command:

```shell
python auto_update.py <PATH_TO_SERVER> | tee <LOG_FILE>
```

The script will automatically check if there exists a new version for your server. If exists, it will:

1. Download and extract the latest server to `~/.cache/`.
2. Create a `7z` backup of your server at `<PATH_TO_SERVER>/../server_backups/`.
3. Update your server while preserving the worlds and configs (`worlds`, `allowlist.json`, `permissions.json`, `server.properties`).
4. Remove the downloaded server cache to free the disk.

After that, you can launch your updated server as usual, or restore it from the backup if there's anything wrong.

## Full Usage

The `auto_update.py` script can take multiple arguments for more fine-grained update control:

| Argument            | Default   | Description                                                     | Note                                              |
|---------------------|-----------|-----------------------------------------------------------------|---------------------------------------------------|
| `--server_dir`      |           | The directory to the server for update.                         |                                                   |
| `--download_dir`    | ~/.cache/ | The directory to download the latest server.                    |                                                   |
| `--target_dir`      | None      | The new directory for the updated server.                       | "None" denotes overwriting the original server.   |
| `--backup_dir`      | None      | The directory to store the backup files of the original server. | "None" will create a new 'server_backups' folder. |
| `--backup_type`     | zip       | Type of the server backup file. (`zip` or `7z`)                 | Run `pip install py7zr` first to use `7z`.        |
| `--keep_cache_num`  | 0         | Number of downloaded server caches to keep                      | -1 denotes infinite, 0 denotes not keeping.       |
| `--keep_backup_num` | -1        | Number of previous server backups to keep.                      | -1 denotes infinite, 0 denotes not keeping.       |

An example of the full usage is like:

```shell
python auto_update.py \
--server_dir <PATH_TO_SERVER> \
--download_dir <PATH_TO_DOWNLOAD_SERVER> \
--target_dir <PATH_TO_UPDATED_SERVER> \
--backup_dir <PATH_TO_STORE_BACKUPS> \
--backup_type "7z" \
--keep_cache_num 5 \
--keep_backup_num 5
```

This will lead to the following operations:

1. Download and extract the latest server to `<PATH_TO_DOWNLOAD_SERVER>`.
2. Create a `zip` backup of your server at `<PATH_TO_STORE_BACKUPS>`.
3. Create an updated server at `<PATH_TO_UPDATED_SERVER>`, and copy the worlds and configs (`worlds`, `allowlist.json`, `permissions.json`, `server.properties`) from the original server.
4. Remove the original server at `<PATH_TO_SERVER>`.
5. Keep the latest 5 downloaded server caches and old server backups on the disk.

## Supported Features

- **Linux Platform**: Scripts written in Python, designed for Linux, and easily transferable to other platforms like Windows.
- **Automatic Update**: Download the latest Minecraft Bedrock Server (BDS) from the official Minecraft website, and apply update if available.
- **Configuration Transfer**: Preserve the server configuration files (`worlds`, `allowlist.json`, `permissions.json`, `server.properties`) during update.
- **Server Backup**: Create a backup file of your original server for recovery.
- **Dynamic Quota Management**: Keep track of download caches and server backups to prevent exceeding the disk quota.

## License

This project is licensed under the MIT License.
