import os
import re
import requests
from bs4 import BeautifulSoup

# 读取.config文件，获取arch_packages
with open('.config', 'r') as file:
    config_content = file.read()

match = re.search(r'CONFIG_TARGET_ARCH_PACKAGES="([^"]+)"', config_content)
if match:
    arch_packages = match.group(1)
else:
    raise ValueError("Could not find CONFIG_TARGET_ARCH_PACKAGES in the .config file")

print(f"Arch Packages: {arch_packages}")

# 读取external-package.txt文件
with open('external-package.txt', 'r') as file:
    package_names = file.read().splitlines()

# 准备输出文件
found_packages = []

for package_name in package_names:
    # 构建URL
    url_kiddin9 = f"https://dl.openwrt.ai/23.05/packages/{arch_packages}/kiddin9/"
    url_base = f"https://dl.openwrt.ai/23.05/packages/{arch_packages}/base/"
    url_packages = f"https://dl.openwrt.ai/23.05/packages/{arch_packages}/packages/"

    # 请求kiddin9目录
    response = requests.get(url_kiddin9)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.ipk')]

    # 查找包名
    found = False
    for link in links:
        if link.startswith(package_name + '_'):
            found = True
            break

    if not found:
        # 请求base目录
        response = requests.get(url_base)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.ipk')]

        for link in links:
            if link.startswith(package_name + '_'):
                found = True
                break

    if not found:
        # 请求packages目录
        response = requests.get(url_packages)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.ipk')]

        for link in links:
            if link.startswith(package_name + '_'):
                found = True
                break

    if found:
        found_packages.append(package_name)
    else:
        print(f"Package {package_name} not found")

# 创建build目录（如果不存在）
os.makedirs('build', exist_ok=True)

# 将找到的包名写入build/package.txt
with open('build/package.txt', 'w') as output_file:
    for package_name in found_packages:
        output_file.write(f"{package_name}\n")

# 创建packages目录（如果不存在）
os.makedirs('packages', exist_ok=True)

# 下载文件
for package_name in found_packages:
    # 构建URL
    url_kiddin9 = f"https://dl.openwrt.ai/23.05/packages/{arch_packages}/kiddin9/"
    url_base = f"https://dl.openwrt.ai/23.05/packages/{arch_packages}/base/"
    url_packages = f"https://dl.openwrt.ai/23.05/packages/{arch_packages}/packages/"

    # 请求kiddin9目录
    response = requests.get(url_kiddin9)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.ipk')]

    # 查找包名
    found = False
    for link in links:
        if link.startswith(package_name + '_'):
            download_url = url_kiddin9 + link
            found = True
            break

    if not found:
        # 请求base目录
        response = requests.get(url_base)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.ipk')]

        for link in links:
            if link.startswith(package_name + '_'):
                download_url = url_base + link
                found = True
                break

    if not found:
        # 请求packages目录
        response = requests.get(url_packages)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.ipk')]

        for link in links:
            if link.startswith(package_name + '_'):
                download_url = url_packages + link
                found = True
                break

    if found:
        filename = download_url.split('/')[-1]
        filepath = os.path.join('packages', filename)
        response = requests.get(download_url)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filepath}")