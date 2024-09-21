# building_image.py

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

    profile_id = sys.argv[1]
    files = "files"
    
    # 读取插件列表
    filename = 'external-package.txt'
    packages = read_packages_from_file(filename)

    # 构建并打印命令
    command = build_command(profile_id, packages, files)
    
    # 切换到immortalwrt-imagebuilder-*目录
    image_builder_dir = "immortalwrt-imagebuilder-*"
    if os.path.isdir(image_builder_dir):
        os.chdir(image_builder_dir)
    else:
        print(f"Directory not found: {image_builder_dir}")
        sys.exit(1)
    
    print(command)