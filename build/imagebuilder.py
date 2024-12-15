import os
import sys
import requests
from tqdm import tqdm
import tarfile

def build_image_download_url(firmware_version, target):
    # 将 target 中的 '/' 替换为 '-'
    target_modified = target.replace('/', '-')
    url = f"https://downloads.openwrt.org/releases/{firmware_version}/targets/{target}/openwrt-imagebuilder-{firmware_version}-{target_modified}.Linux-x86_64.tar.xz"
    return url

def download_file_with_progress(url):
    # 获取文件大小
    response_head = requests.head(url)
    total_size_in_bytes = int(response_head.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte

    # 开始下载文件
    response = requests.get(url, stream=True)
    filename = url.split('/')[-1]

    # 使用 tqdm 创建进度条
    progress = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open(filename, 'wb') as file:
        for data in response.iter_content(block_size):
            progress.update(len(data))
            file.write(data)
    progress.close()

    if total_size_in_bytes != 0 and progress.n != total_size_in_bytes:
        print("ERROR, download incomplete.")
    else:
        print(f"文件已成功下载到 {filename}")
    return filename

def extract_with_progress(tar_path):
    with tarfile.open(tar_path, "r:xz") as tar:
        members = tar.getmembers()
        total_members = len(members)
        progress = tqdm(total=total_members, unit='files', desc='Extracting')
        for member in members:
            tar.extract(member)
            progress.update(1)
        progress.close()

def parse_input(input_string):
    parts = input_string.split(',')
    if len(parts) != 2:
        raise ValueError("输入格式错误，应为 ID,Target")
    return parts[0].strip(), parts[1].strip()

def main():
    if len(sys.argv) != 2:
        print("Usage: python imagebuilder.py 'ID,Target'")
        sys.exit(1)
    
    input_string = sys.argv[1]
    
    try:
        id, target = parse_input(input_string)
    except ValueError as e:
        print(e)
        sys.exit(1)
    
    print(f"接收到的参数：ID={id}, Target={target}")

    # 构建 URL
    # firmware_version = '23.05.3'
    firmware_version = os.getenv('VERSION', '23.05.3')
    url = build_image_download_url(firmware_version, target)

    # 打印 URL 以便验证
    print(f"构建的下载 URL 为: {url}")

    # 下载文件
    filename = download_file_with_progress(url)

    # 解压文件并显示进度
    extract_with_progress(filename)

if __name__ == "__main__":
    main()