import os
import requests
from bs4 import BeautifulSoup
import re

# 指定文件路径
repositories_conf_path = './repositories.conf'
external_package_path = './external-package.txt'
output_package_path = './packages.txt'
download_folder = './packages'

# 创建 ./packages 目录（如果不存在）
os.makedirs(download_folder, exist_ok=True)

# 读取环境变量PLATFORM
PLATFORM = os.getenv('PLATFORM', 'generic')  # 默认为generic，根据实际情况更改

# 包库的基本URL
primary_base_url = "https://dl.openwrt.ai/23.05/packages"
secondary_base_url = f"https://dl.openwrt.ai/23.05/packages/{PLATFORM}/base"

# 创建一个字典来存储包名及其下载链接
package_versions = {}
secondary_package_versions = {}

# 读取文件并检查每一行
with open(repositories_conf_path, 'r') as file:
    for line in file:
        if 'src/gz immortalwrt_packages' in line:
            # 分割字符串
            parts = line.split('/packages')
            if len(parts) == 3:
                # 构建新的下载链接
                download_link = f'{primary_base_url}{parts[1]}/kiddin9'
                # 获取每个下载链接的内容并解析文件名
                response = requests.get(download_link)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    for link in soup.find_all('td', class_='link'):
                        a_tag = link.find('a')
                        if a_tag and a_tag['href'].endswith('.ipk'):
                            # 解析版本号
                            match = re.match(r'^(.*?)(_.*?)-.*\.ipk$', a_tag['href'])
                            if match:
                                name_version = match.group(1)
                                version = match.group(2)
                                package_versions.setdefault(name_version, (version, a_tag['href'], download_link))
                                if version > package_versions[name_version][0]:
                                    package_versions[name_version] = (version, a_tag['href'], download_link)

# 读取第二个包库的内容并解析文件名
response = requests.get(secondary_base_url)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    for link in soup.find_all('td', class_='n'):
        a_tag = link.find('a')
        if a_tag and a_tag['href'].endswith('.ipk'):
            # 解析版本号
            match = re.match(r'^(.*?)(_.*?)-.*\.ipk$', a_tag['href'])
            if match:
                name_version = match.group(1)
                version = match.group(2)
                secondary_package_versions.setdefault(name_version, (version, a_tag['href'], secondary_base_url))
                if version > secondary_package_versions[name_version][0]:
                    secondary_package_versions[name_version] = (version, a_tag['href'], secondary_base_url)

# 合并两个字典
package_versions.update(secondary_package_versions)

# 读取外部包文件的内容
found_packages = []
not_found_packages = []

with open(external_package_path, 'r') as external_file:
    for line in external_file:
        package_name = line.strip()
        # 如果这一行是以 '-' 开头，则直接跳过搜索，并写入输出文件
        if package_name.startswith('-'):
            with open(output_package_path, 'a') as output_file:
                output_file.write(package_name + '\n')
            continue
        
        # 尝试前端匹配
        matches = [pkg for pkg, info in package_versions.items() if pkg.startswith(package_name)]
        if matches:
            found_packages.append(package_name)
            for match in matches:
                _, ipk_filename, download_link = package_versions[match]
                full_download_link = download_link + '/' + ipk_filename
                print(f"Found package: {package_name} at {full_download_link}")
                
                # 下载包
                ipk_filepath = os.path.join(download_folder, ipk_filename)
                try:
                    with requests.get(full_download_link, stream=True) as r:
                        r.raise_for_status()
                        with open(ipk_filepath, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    print(f"Downloaded {ipk_filename} successfully.")
                except Exception as e:
                    print(f"Failed to download {ipk_filename}: {e}")
        else:
            not_found_packages.append(package_name)
            print(f"No package matching: {package_name}")

# 将找到的包名追加到已有的输出文件中
with open(output_package_path, 'a') as output_file:
    for pkg in found_packages:
        output_file.write(pkg + '\n')

print(f"发现包已附加到 {output_package_path}")

if not_found_packages:
    print("未找到以下软件包：")
    for pkg in not_found_packages:
        print(pkg)
else:
    print("已找到所有请求的包。")