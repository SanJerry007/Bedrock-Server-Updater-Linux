#####################################################################
# Copyright(c) 2024, SanJerry007
# Licensed under MIT License.
# See the LICENSE file on https://opensource.org/licenses/MIT for details.
# Project repository: https://github.com/SanJerry007/Bedrock-Server-Updater-Linux
#####################################################################

import argparse
import datetime
import os
import re
import shutil
import zipfile
from functools import cmp_to_key
from typing import List, Optional

import requests

SPECIAL_PATHS = {"worlds", "allowlist.json", "permissions.json", "server.properties"}


def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] - {message}"
    print(log_entry)


def extract_numbers(string, match_float=True, match_sign=True):
    """Extract numbers from a given string."""
    pattern = r"\d+"
    if match_float:
        pattern = r"\d*\.\d+|" + pattern
    if match_sign:
        pattern = r"[-+]?" + pattern
    matches = re.findall(pattern, string)
    numbers = [float(match) if '.' in match else int(match) for match in matches]
    return numbers


def compare_version(v1: List[int], v2: List[int]) -> int:
    """
    Compares two versions, with each represented as a list of numbers.
    If v1 < v2, return -1.
    If v1 == v2, return 0.
    If v1 > v2, return 1.
    """
    compare_length = min(len(v1), len(v2))
    for i in range(compare_length):
        if v1[i] < v2[i]:
            return -1
        elif v1[i] > v2[i]:
            return 1
    return 0


def get_local_server_version(server_dir: str) -> List[int]:
    """Use the version of the latest vanilla behavior pack as the server version."""
    latest_version = [0]
    behavior_path = os.path.join(server_dir, "behavior_packs")

    for dirname in os.listdir(behavior_path):
        if dirname.startswith("vanilla_"):
            this_version = extract_numbers(dirname.replace("vanilla_", ""), match_float=False, match_sign=False)
            if compare_version(latest_version, this_version) < 0:
                latest_version = this_version

    return latest_version


def download_and_extract_latest_server(download_dir: str, local_version: List[int]) -> Optional[str]:
    success = False

    try:
        # request settings
        headers = {
            "Accept-Encoding": "identity",
            "Accept-Language": "en",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.33 (KHTML, like Gecko) Chrome/90.0.$RandNum.212 Safari/537.33"
        }
        search_url = "https://minecraft.net/en-us/download/server/bedrock/"
        download_url_template = r'https://www.minecraft.net/bedrockdedicatedserver/bin-linux/[^"]*'

        # get the response
        log_message(f"Connecting to {search_url} to get latest server version")
        response = requests.get(search_url, headers=headers)
        download_url = re.search(download_url_template, response.text)  # extract the version

        # get the url for downloading
        if download_url is not None:  # extract version succeeded
            download_url = download_url.group(0)
            remote_version = extract_numbers(download_url, match_float=False, match_sign=False)

            # download and extract the server
            if compare_version(local_version, remote_version) < 0:  # the remote version is the latest, try to download the latest server
                log_message(f"New version detected: {remote_version}")
                file_name = download_url.split("/")[-1]
                os.makedirs(download_dir, exist_ok=True)
                download_file = os.path.join(download_dir, file_name)
                extract_dir = os.path.join(download_dir, file_name.replace(".zip", ""))

                # check if cache available
                perform_download = True
                if os.path.isfile(download_file):  # we have a cached file locally
                    log_message(f"Using cached file \"{download_file}\"")
                    try:
                        with zipfile.ZipFile(download_file, 'r') as zip_ref:
                            zip_ref.extractall(extract_dir)
                        log_message(f"Extracted the server files to \"{extract_dir}\"")
                        success = True
                        perform_download = False
                    except:
                        log_message(f"Local cache is deprecated, will perform redownloading...")
                        shutil.rmtree(download_file)
                        shutil.rmtree(extract_dir)

                # download the server online
                if perform_download:
                    log_message(f"Downloading the latest server from {download_url}")
                    server_file = requests.get(download_url, headers=headers, stream=True, verify=True)

                    if server_file.status_code == 200:  # download succeeded
                        with open(download_file, 'wb') as f:
                            f.write(server_file.content)
                        log_message(f"Server file downloaded successfully to \"{download_file}\"")

                        extract_dir = os.path.join(download_dir, file_name.replace(".zip", ""))
                        with zipfile.ZipFile(download_file, 'r') as zip_ref:
                            zip_ref.extractall(extract_dir)
                        log_message(f"Extracted the server files to \"{extract_dir}\"")
                        success = True

                    else:  # download failed
                        log_message(f"Failed to download the server file. Status code: {server_file.status_code}")

            else:  # the local version is the latest, no update available
                log_message(f"Local version ({str.join('.', [str(v) for v in local_version])}) is already up-to-date compared to the remote version ({str.join('.', [str(v) for v in remote_version])}).")

        else:  # extract version failed
            log_message(f"Obtaining latest server version from {search_url} failed")

    except Exception as e:
        log_message(f"ERROR: {str(e)}")

    if success:
        return extract_dir
    else:
        return None


def backup_local_server(server_dir: str, backup_dir: str, type: str = "zip"):
    os.makedirs(backup_dir, exist_ok=True)

    today = datetime.datetime.today()
    today = today.replace(second=0, microsecond=0)
    now_time = today.strftime("%Y%m%d%H%M")
    target_name = f"{now_time}-{os.path.basename(server_dir)}"

    log_message(f"Creating server backup...")
    os.makedirs(backup_dir, exist_ok=True)
    target_file = os.path.join(backup_dir, f"{target_name}.{type}")

    # remove existed backup
    if os.path.isfile(target_file):
        os.remove(target_file)
        log_message(f"Successfully removed existed backup file \"{target_file}\"!")

    # create a new one
    if type == "zip":
        import zipfile
        with zipfile.ZipFile(target_file, 'w') as archive:
            if os.path.isdir(server_dir):
                for dirpath, dirnames, filenames in os.walk(server_dir):
                    save_dirpath = dirpath.replace(server_dir, ".")
                    for filename in filenames:
                        archive.write(os.path.join(dirpath, filename), arcname=os.path.join(save_dirpath, filename), compress_type=zipfile.ZIP_LZMA)
            else:
                archive.write(server_dir, arcname=os.path.basename(server_dir), compress_type=zipfile.ZIP_LZMA)
    elif type == "7z":
        import py7zr
        with py7zr.SevenZipFile(target_file, 'w') as archive:
            if os.path.isdir(server_dir):
                archive.writeall(server_dir, arcname="")
            else:
                archive.write(server_dir, arcname=os.path.basename(server_dir))
    else:
        raise ValueError(f"Wrong file type \"{type}\"!")

    log_message(f"Successfully compressed \"{server_dir}\" to file \"{target_file}\"!")


def update_server_properties(source_file: str, target_file: str):
    """
    Update the values in `server.properties` from a given source file to the target file.
    - Keys in both source and target: source -> target
    - Keys only in source:            neglect
    - Keys only in target:            keep the target
    """
    source_dict, target_dict, result_dict = {}, {}, {}

    with open(source_file, "r", encoding="UTF-8") as f:
        for line in f.readlines():
            if not line.startswith("#") and not line == "\n":
                key, value = line.split("=")
                source_dict[key.strip()] = value.strip()

    with open(target_file, "r", encoding="UTF-8") as f:
        target_lines = f.readlines()  # backup lines for writing
        for line in target_lines:
            if not line.startswith("#") and not line == "\n":
                key, value = line.split("=")
                target_dict[key.strip()] = value.strip()

    # compare keys
    all_keys = sorted(list(set(source_dict.keys()) | set(target_dict.keys())))
    for key in all_keys:
        if key in source_dict and key in target_dict:  # in both source and target
            result_dict[key] = source_dict[key]
            log_message(f"(server.property) {key}={source_dict[key]} (use old)")
        elif key not in target_dict:  # only in source
            log_message(f"(server.property) {key} (dropped)")
        else:  # only in target
            result_dict[key] = target_dict[key]
            log_message(f"(server.property) {key}={target_dict[key]} (use new)")

    # update server.property
    with open(target_file, "w", encoding="UTF-8") as f:
        for line in target_lines:
            if not line.startswith("#") and not line == "\n":  # Skip comment lines and invalid lines
                key = line.split("=")[0].strip()
                f.write(f"{key}={result_dict[key]}\n")
            else:
                f.write(line)  # Write the comment line unchanged


def update_server(local_server_dir: str, latest_server_dir: str, target_server_dir: Optional[str] = None):
    """
    The special paths to handle:
    - `worlds`: Directly copy to the target directory.
    - `allowlist.json`: Directly copy to the target directory.
    - `permissions.json`: Directly copy to the target directory.
    - `server.properties`: Compare and validate the keys & values one by one, and copy the existing ones from old to new.
    """
    if target_server_dir is None:
        target_server_dir = local_server_dir
    os.makedirs(target_server_dir, exist_ok=True)

    # 1. copy non-special files from `latest_server_dir` to `target_server_dir`
    for filename in sorted(os.listdir(latest_server_dir)):
        if filename not in SPECIAL_PATHS:
            server_dir = os.path.join(latest_server_dir, filename)
            target_path = os.path.join(target_server_dir, filename)
            if os.path.isfile(server_dir):
                shutil.copy2(server_dir, target_path)  # Replace the local file with the latest server file
            else:
                shutil.copytree(server_dir, target_path, dirs_exist_ok=True)
            log_message(f"Copied \"{server_dir}\" to \"{target_path}\"")

    # 2. copy special files from `local_server_dir` to `target_server_dir`
    if target_server_dir != local_server_dir:
        for filename in SPECIAL_PATHS - {"server.properties"}:
            server_dir = os.path.join(local_server_dir, filename)
            target_path = os.path.join(target_server_dir, filename)
            if os.path.isfile(server_dir):
                shutil.copy2(server_dir, target_path)  # Replace the local file with the latest server file
            else:
                shutil.copytree(server_dir, target_path, dirs_exist_ok=True)
            log_message(f"Copied \"{server_dir}\" to \"{target_path}\"")

    # 3. update `server.properties`
    old_property_file = os.path.join(local_server_dir, "server.properties")
    latest_property_file = os.path.join(latest_server_dir, "server.properties")
    new_property_file_temp = os.path.join(target_server_dir, "server.properties.temp")

    shutil.copy2(latest_property_file, new_property_file_temp)
    update_server_properties(old_property_file, new_property_file_temp)  # the operations are kind of complicated

    new_property_file = os.path.join(target_server_dir, "server.properties")
    if os.path.exists(new_property_file):
        os.remove(new_property_file)
    os.rename(new_property_file_temp, new_property_file)
    log_message(f"Updated the information of \"{new_property_file}\"")

    # 4. remove the old server
    if target_server_dir != local_server_dir:
        shutil.rmtree(local_server_dir)
        log_message(f"Removed the old server \"{local_server_dir}\"")

    # 5. remove the `latest_server_dir`
    shutil.rmtree(latest_server_dir)
    log_message(f"Removed the latest_server_dir \"{local_server_dir}\"")


def delete_download_cache_files(download_dir: str, max_num: int = -1):
    if max_num >= 0:
        all_versions = sorted(
            [
                extract_numbers(filename, match_float=False, match_sign=False)
                for filename in os.listdir(download_dir)
                if os.path.isfile(os.path.join(download_dir, filename))
            ],
            key=cmp_to_key(compare_version)
        )
        log_message(f"{len(all_versions)} cached server updates detected, keeping the latest {max_num} files")

        if len(all_versions) > max_num:
            # O(n^2) complexity, can be optimized using sets.
            # (It is kind of nauseous, so I use this inefficient implementation which is OK as the backups are usually very little)
            for filename in sorted(os.listdir(download_dir)):
                if os.path.isfile(os.path.join(download_dir, filename)):
                    this_version = extract_numbers(filename, match_float=False, match_sign=False)
                    delete = True
                    if max_num > 0:  # o need to compare if keep 0
                        for keep_version in all_versions[-max_num:]:
                            if compare_version(keep_version, this_version) == 0:
                                delete = False
                                break
                    if delete:
                        file_path = os.path.join(download_dir, filename)
                        os.remove(file_path)
                        log_message(f"Old update cache \"{file_path}\" has been deleted")
        else:
            log_message(f"No cached update to delete")
    else:
        log_message(f"Keeping infinite number of cached updates")


def delete_local_server_backup_files(backup_dir: str, max_num: int = -1):
    if max_num >= 0:
        all_files = sorted(
            [
                filename
                for filename in os.listdir(backup_dir)
                if os.path.isfile(os.path.join(backup_dir, filename))
            ],
            key=lambda x: int(x.split('-')[0]),
            reverse=True
        )
        log_message(f"{len(all_files)} backup server files detected, keeping the latest {max_num} files")

        if len(all_files) > max_num:
            for filename in all_files[max_num:]:
                file_path = os.path.join(backup_dir, filename)
                os.remove(file_path)
                log_message(f"Old server backup \"{file_path}\" has been deleted")
        else:
            log_message(f"No server backup to delete")
    else:
        log_message(f"Keeping infinite number of server backups")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--server_dir', type=str, help="The directory to the server for update.")
    parser.add_argument('--download_dir', type=str, default="~/.cache", help="The directory to download the latest server.")
    parser.add_argument('--target_dir', type=str, default=None, help="The new directory for the updated server. (None denotes overwriting the original server dir)")
    parser.add_argument('--backup_dir', type=str, default=None, help="The directory to store the backup files of the original server. (If None, will create a new 'server_backups' folder at the same level as `server_dir`)")
    parser.add_argument('--backup_type', default="zip", choices=("zip", "7z"), type=str)
    parser.add_argument('--keep_cache_num', type=int, default=0, help="Number of downloaded server caches to keep. (-1 denotes infinite, 0 denotes not keeping)")
    parser.add_argument('--keep_backup_num', type=int, default=-1, help="Number of previous server backups to keep. (-1 denotes infinite, 0 denotes not keeping)")
    args = parser.parse_args()

    if args.backup_dir is None and args.keep_backup_num != 0:  # automatically set the backup dir
        args.backup_dir = os.path.join(os.path.dirname(args.server_dir), "server_backups")
        log_message(f"Automatically setting backup directory to \"{args.backup_dir}\"")

    log_message(args)

    local_version = get_local_server_version(args.server_dir)
    latest_server_dir = download_and_extract_latest_server(args.download_dir, local_version)

    if latest_server_dir is not None:
        if args.keep_backup_num != 0:
            backup_local_server(args.server_dir, args.backup_dir, type=args.backup_type)
        update_server(args.server_dir, latest_server_dir, args.target_dir)

        delete_download_cache_files(args.download_dir, args.keep_cache_num)
        delete_local_server_backup_files(args.backup_dir, args.keep_backup_num)

    log_message("Done!")


def func_test():
    # test the download
    download_and_extract_latest_server("./temp", [0])
