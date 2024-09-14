import os
import requests
import tarfile
from io import BytesIO

def download_and_extract(firmware_version, target_platform):
    # 构建下载URL
    url_template = "https://downloads.immortalwrt.org/releases/{firmware_version}/targets/{target_platform}/immortalwrt-imagebuilder-{firmware_version}-{target_platform//\//-}.Linux-x86_64.tar.xz"
    url = url_template.format(firmware_version=firmware_version, target_platform=target_platform.replace("/", "-"))
    
    print(f"Firmware Version: {firmware_version}")
    print(f"Target Platform: {target_platform}")
    print(f"Downloading from URL: {url}")

    # 下载文件
    response = requests.get(url)
    response.raise_for_status()  # 确认请求成功

    # 解压文件
    tar_data = BytesIO(response.content)
    with tarfile.open(fileobj=tar_data) as tar:
        tar.extractall(path='.')
    
    print("Download and extraction completed.")

if __name__ == "__main__":
    firmware_version = os.getenv('FIRMWARE_VERSION', 'Unknown')
    target_platform = os.getenv('TARGET_PLATFORM', 'Unknown')
    download_and_extract(firmware_version, target_platform)