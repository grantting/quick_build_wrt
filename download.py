import os
import json
from bs4 import BeautifulSoup
import requests
import tarfile
from io import BytesIO

def parse_parameters(parameters_json):
    try:
        parameters = json.loads(parameters_json)
        if not all(key in parameters for key in ['model_name', 'target_platform']):
            raise ValueError("Parameters must include 'model_name' and 'target_platform'.")
        return parameters['model_name'], parameters['target_platform']
    except Exception as e:
        raise ValueError("Invalid parameters JSON format.") from e

def fetch_architecture(firmware_version, target_platform):
    # 构建获取架构信息的URL
    profiles_url = f"https://downloads.immortalwrt.org/releases/{firmware_version}/targets/{target_platform}/profiles.json"
    
    # 下载profiles.json文件
    response = requests.get(profiles_url)
    response.raise_for_status()
    profiles_data = response.json()

    # 从profiles.json中提取架构信息
    arch_packages = profiles_data.get('arch_packages')
    if not arch_packages:
        raise ValueError("Failed to find 'arch_packages' in profiles.json")

    return arch_packages

def download_and_extract(firmware_version, model_name, target_platform, architecture):
    # 构建下载URL
    target_platform_replaced = target_platform.replace("/", "-")
    url_template = (
        "https://downloads.immortalwrt.org/releases/{firmware_version}/targets/{target_platform}/"
        "immortalwrt-imagebuilder-{firmware_version}-{target_platform_replaced}.Linux-x86_64.tar.xz"
    )
    url = url_template.format(
        firmware_version=firmware_version,
        target_platform=target_platform,
        target_platform_replaced=target_platform_replaced
    )

    # 检查是否已存在对应的目录
    build_dir = f"immortalwrt-imagebuilder-{firmware_version}-{target_platform_replaced}.Linux-x86_64"
    if not os.path.exists(build_dir):
        print(f"Firmware Version: {firmware_version}")
        print(f"Model Name: {model_name}")
        print(f"Target Platform: {target_platform}")
        print(f"Architecture: {architecture}")
        print(f"Downloading from URL: {url}")

        # 下载文件
        response = requests.get(url)
        response.raise_for_status()  # 确认请求成功

        # 解压文件
        tar_data = BytesIO(response.content)
        with tarfile.open(fileobj=tar_data) as tar:
            tar.extractall(path='.')
        
        print("Download and extraction completed.")
    else:
        print(f"Directory '{build_dir}' already exists, skipping download and extraction.")

def download_packages(firmware_version, target_platform, architecture):
    # 读取 external-package.txt 文件
    packages_to_download = []
    with open('external-package.txt', 'r') as file:
        for line in file:
            package_name = line.strip()
            if package_name:
                packages_to_download.append(package_name)

    # 构建解压后的目录
    build_dir = f"immortalwrt-imagebuilder-{firmware_version}-{target_platform.replace('/', '-')}.Linux-x86_64"
    
    package_list_url = f"https://op.dllkids.xyz/packages/{architecture}"
    package_list_response = requests.get(package_list_url)
    package_list_response.raise_for_status()

    # 解析页面找到所有包的链接
    soup = BeautifulSoup(package_list_response.text, 'html.parser')
    
    # 获取 build_dir 下的 packages 目录路径
    packages_dir = os.path.join(build_dir, "packages")
    os.makedirs(packages_dir, exist_ok=True)  # 确保目录存在

    downloaded_packages = set()
    for package_name in packages_to_download:
        # 查找对应的包
        found = False
        for link in soup.find_all('a'):
            package_full_name = link.get('href')
            package_basename = os.path.splitext(os.path.basename(package_full_name))[0]

            if package_name in package_basename and not found:
                package_url = f"{package_list_url}/{package_full_name}"
                print(f"Downloading package: {package_full_name} from {package_url}")
                package_response = requests.get(package_url)
                if package_response.status_code == 200:
                    # 保存包文件到 build_dir 下的 packages 目录
                    package_path = os.path.join(packages_dir, package_full_name)
                    with open(package_path, 'wb') as f:
                        f.write(package_response.content)
                    downloaded_packages.add(package_full_name)
                    found = True
                    break
                else:
                    print(f"Failed to download package: {package_full_name}")
                    break
        if not found:
            print(f"No matching package found for: {package_name}")
                                                
if __name__ == "__main__":
    firmware_version = os.getenv('FIRMWARE_VERSION', 'Unknown')
    parameters_json = os.getenv('PARAMETERS_JSON', '{}')
    # firmware_version = '23.05.3'
    # parameters_json = '{"model_name": "qihoo_360t7-ubootmod", "target_platform": "mediatek/filogic"}'

    try:
        model_name, target_platform = parse_parameters(parameters_json)
        architecture = fetch_architecture(firmware_version, target_platform)
        download_and_extract(firmware_version, model_name, target_platform, architecture)
        download_packages(firmware_version, target_platform, architecture)
    except ValueError as e:
        print(f"Error: {e}")
