import subprocess
import sys
import os
from configparser import ConfigParser

def find_repositories_conf():
    # 查找 repositories.conf 文件
    for root, dirs, files in os.walk('.'):
        if 'repositories.conf' in files:
            return os.path.join(root, 'repositories.conf')
    return None

def update_repositories_conf(file_path):
    # 更新 repositories.conf 文件中的 URL
    lines = []
    updated = False
    
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('src/gz immortalwrt_packages'):
                parts = line.split()
                if len(parts) >= 3:
                    url = parts[2]
                    new_url = url.replace('https://downloads.immortalwrt.org/releases/23.05.3/packages/', 'https://op.dllkids.xyz/packages/')
                    new_url = new_url.rstrip('/packages')
                    
                    if new_url != url:
                        parts[2] = new_url
                        updated = True
                line = ' '.join(parts) + '\n'
            lines.append(line)
    
    if updated:
        with open(file_path, 'w') as file:
            file.writelines(lines)
    
    return updated

def read_packages_from_file(filename):
    # 从文件中读取插件列表
    with open(filename, 'r') as file:
        packages = [line.strip() for line in file if line.strip()]
    return ' '.join(packages)

def build_command(profile_id, packages, files):
    # 构造make命令
    command = f"make image PROFILE=\"{profile_id}\" PACKAGES=\"{packages}\" FILES=\"{files}\""
    return command

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python building_image.py <profile-id>")
        sys.exit(1)

    # 提取逗号前的部分作为 profile_id
    profile_id_with_comma = sys.argv[1]
    profile_id_parts = profile_id_with_comma.split(',')
    profile_id = profile_id_parts[0].strip()
    
    files = "files"
    
    # 查找并更新 repositories.conf 文件
    repositories_conf_path = find_repositories_conf()
    if repositories_conf_path and update_repositories_conf(repositories_conf_path):
        print(f"Updated URL in {repositories_conf_path}")
    else:
        print("Did not find repositories.conf or no changes made.")

    # 读取插件列表
    filename = 'external-package.txt'
    packages = read_packages_from_file(filename)

    # 构建并打印命令
    command = build_command(profile_id, packages, files)

    print(command)

    try:
        # 执行构建命令
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Command '{command}' failed with error code {e.returncode}.")
        sys.exit(e.returncode)