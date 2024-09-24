import os
import requests
from bs4 import BeautifulSoup

# 指定文件路径
repositories_conf_path = './repositories.conf'
external_package_path = './external-package.txt'
output_package_path = './packages.txt'

# 存储构建后的下载链接
download_links = []

# 读取文件并检查每一行
with open(repositories_conf_path, 'r') as file:
    for line in file:
        if 'src/gz immortalwrt_packages' in line:
            # 分割字符串
            parts = line.split('/packages')
            if len(parts) == 3:
                # 构建新的下载链接
                download_link = f'https://op.dllkids.xyz/packages{parts[1]}'
                download_links.append(download_link)

# 创建 ./packages 目录（如果不存在）
download_folder = './packages'
os.makedirs(download_folder, exist_ok=True)

# 创建一个字典来存储包名及其下载链接
package_names = {}

# 获取每个下载链接的内容并解析文件名
for download_link in download_links:
    response = requests.get(download_link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        for link in soup.find_all('td', class_='link'):
            a_tag = link.find('a')
            if a_tag and a_tag['href'].endswith('.ipk'):
                package_names[a_tag['href']] = download_link + '/' + a_tag['href']

# 读取外部包文件的内容
found_packages = []
not_found_packages = []

with open(external_package_path, 'r') as external_file:
    for line in external_file:
        package_name = line.strip()
        # 尝试前端匹配
        matches = [pkg for pkg in package_names if pkg.startswith(package_name)]
        if matches:
            found_packages.append(package_name)
            for match in matches:
                full_download_link = package_names[match]
                print(f"Found package: {package_name} at {full_download_link}")
        else:
            not_found_packages.append(package_name)
            print(f"No package matching: {package_name}")

# 将找到的包名写入新的文件
with open(output_package_path, 'w') as output_file:
    for pkg in found_packages:
        output_file.write(pkg + '\n')

print(f"Found packages have been written to {output_package_path}")

if not_found_packages:
    print("The following packages were not found:")
    for pkg in not_found_packages:
        print(pkg)
else:
    print("All requested packages were found.")