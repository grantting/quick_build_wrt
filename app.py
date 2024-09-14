import os
import json
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

def download_packages(firmware_version, target_platform, architecture):
    package_list_url = f"https://op.dllkids.xyz/packages/{architecture}"
    package_list_response = requests.get(package_list_url)
    package_list_response.raise_for_status()
    package_list_data = package_list_response.json()

    # 创建 Packages 目录
    build_dir = f"immortalwrt-imagebuilder-{firmware_version}-{target_platform.replace('/', '-')}.Linux-x86_64"
    packages_dir = os.path.join(build_dir, "Packages")
    os.makedirs(packages_dir, exist_ok=True)

    packages = []
    with open(os.path.join(build_dir, 'external-package.txt'), 'r') as file:
        for line in file:
            package_name = line.strip()
            if package_name:
                packages.append(package_name)

    downloaded_packages = set()
    for package in packages:
        if package not in downloaded_packages:
            package_url = f"{package_list_url}/{package}"
            print(f"Downloading package: {package} from {package_url}")
            package_response = requests.get(package_url)
            if package_response.status_code == 200:
                # 假设包是压缩文件，这里解压并保存
                package_path = os.path.join(packages_dir, package)
                with open(package_path, 'wb') as f:
                    f.write(package_response.content)
                downloaded_packages.add(package)
            else:
                print(f"Failed to download package: {package}")
        else:
            print(f"Package already downloaded: {package}")

if __name__ == "__main__":
    firmware_version = os.getenv('FIRMWARE_VERSION', 'Unknown')
    parameters_json = os.getenv('PARAMETERS_JSON', '{}')

    try:
        model_name, target_platform = parse_parameters(parameters_json)
        architecture = fetch_architecture(firmware_version, target_platform)
        download_and_extract(firmware_version, model_name, target_platform, architecture)
        download_packages(firmware_version, target_platform, architecture)
    except ValueError as e:
        print(f"Error: {e}")