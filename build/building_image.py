# building_image.py

import subprocess
import sys
import os

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
    
    # 读取插件列表
    filename = 'external-package.txt'
    packages = read_packages_from_file(filename)

    # 构建并打印命令
    command = build_command(profile_id, packages, files)

      
    print(command)

    # 执行构建命令
    subprocess.run(command, shell=True, check=True)