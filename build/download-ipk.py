import re
import os
import requests
import gzip
import shutil

# 读取.config文件，获取arch_packages
with open('.config', 'r') as file:
    config_content = file.read()

match = re.search(r'CONFIG_TARGET_ARCH_PACKAGES="([^"]+)"', config_content)
if match:
    arch_packages = match.group(1)
else:
    raise ValueError("未能在.config文件中找到CONFIG_TARGET_ARCH_PACKAGES")

print(f"架构包: {arch_packages}")

# 读取环境变量 PLATFORM
platform = os.getenv('PLATFORM', 'ipq807x/generic')
if not platform:
    raise ValueError("Environment variable PLATFORM is not set")

# 源仓库URL列表
source_urls = [
    f"https://dl.openwrt.ai/releases/24.10/packages/{arch_packages}/kiddin9/Packages.gz",
    f"https://downloads.immortalwrt.org/releases/23.05.4/packages/{arch_packages}/luci/Packages.gz"
    # f"https://mirror-03.infra.openwrt.org/releases/23.05.5/packages/{arch_packages}/luci/Packages.gz"
]

# 创建目录来存放下载和解压的文件
download_dir = 'downloads'
os.makedirs(download_dir, exist_ok=True)

# 下载并解压Packages.gz文件
extracted_files = []
for url in source_urls:
    # 获取文件名
    filename = url.split('/')[-1]
    
    # 根据URL构建唯一的文件名
    unique_prefix = url.split('/')[2]  # 使用URL中的第二部分作为前缀
    unique_filename = f"{unique_prefix}_{filename}"
    download_path = os.path.join(download_dir, unique_filename)
    extract_path = os.path.join(download_dir, unique_filename.replace('.gz', ''))

    # 下载文件
    response = requests.get(url)
    if response.status_code == 200:
        with open(download_path, 'wb') as f:
            f.write(response.content)
        print(f"已下载: {download_path}")
        
        # 解压文件
        with gzip.open(download_path, 'rb') as f_in:
            with open(extract_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"已解压: {extract_path}")
        
        # 删除压缩包
        os.remove(download_path)
        print(f"已删除压缩包: {download_path}")
        
        # 记录解压后的文件路径
        extracted_files.append((extract_path, url))
    else:
        print(f"下载失败: {url}")

print("所有下载、解压和删除操作已完成。")

# 读取external-package.txt文件
package_names = []
with open('external-package.txt', 'r', encoding='utf-8') as file:
    package_names = file.read().splitlines()

# 查找并打印每个包的Filename
def find_package_filename(package_name, packages_file):
    with open(packages_file, 'r', encoding='utf-8') as file:
        content = file.read()
        packages = content.split('\n\n')  # 分割成多个Package条目
        for package in packages:
            if f"Package: {package_name}" in package:
                lines = package.split('\n')
                for line in lines:
                    if line.startswith("Filename: "):
                        return line.split(": ")[1]
    return None

# 创建目录来存放下载的IPK文件
ipk_download_dir = 'packages'
os.makedirs(ipk_download_dir, exist_ok=True)

# 遍历每个解压后的Packages文件
for package_name in package_names:
    found = False
    for extracted_file, source_url in extracted_files:
        filename = find_package_filename(package_name, extracted_file)
        if filename:
            # 构建下载URL
            base_url = source_url.rsplit('/', 1)[0]  # 去掉Packages.gz部分
            download_url = f"{base_url}/{filename}"
            
            # 下载IPK文件
            response = requests.get(download_url)
            if response.status_code == 200:
                ipk_path = os.path.join(ipk_download_dir, filename)
                with open(ipk_path, 'wb') as f:
                    f.write(response.content)
                print(f"已下载: {ipk_path}")
            else:
                print(f"下载失败: {download_url}")
            
            found = True
            break
    
    if not found:
        print(f"未找到包: {package_name}")

print("所有操作已完成。")