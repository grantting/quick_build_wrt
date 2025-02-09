import os
import sys
import requests
from tqdm import tqdm
import tarfile

def build_image_download_url(firmware_version, target):
    target_modified = target.replace('/', '-')
    url = f"https://downloads.immortalwrt.org/releases/{firmware_version}/targets/{target}/immortalwrt-imagebuilder-{firmware_version}-{target_modified}.Linux-x86_64.tar.zst"
    return url

def download_file_with_progress(url):
    response_head = requests.head(url)
    total_size_in_bytes = int(response_head.headers.get('content-length', 0))
    block_size = 1024

    response = requests.get(url, stream=True)
    filename = url.split('/')[-1]

    progress = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open(filename, 'wb') as file:
        for data in response.iter_content(block_size):
            progress.update(len(data))
            file.write(data)
    progress.close()

    if total_size_in_bytes != 0 and progress.n != total_size_in_bytes:
        print("ERROR: 下载不完整")
        sys.exit(1)
    else:
        print(f"文件已下载: {filename}")
    return filename

def extract_with_progress(tar_path):
    try:
        # 使用zstd模式解压
        with tarfile.open(tar_path, "r:zst") as tar:
            members = tar.getmembers()
            total_members = len(members)
            progress = tqdm(total=total_members, unit='files', desc='解压中')
            for member in members:
                tar.extract(member)
                progress.update(1)
            progress.close()
    except tarfile.ReadError as e:
        print(f"解压失败: {e}")
        print("请确认已安装zstandard库，执行命令: pip install zstandard")
        sys.exit(1)
    except Exception as e:
        print(f"未知错误: {e}")
        sys.exit(1)

def parse_input(input_string):
    parts = input_string.split(',')
    if len(parts) != 2:
        raise ValueError("输入格式错误，应为 'ID,Target'")
    return parts[0].strip(), parts[1].strip()

def main():
    if len(sys.argv) != 2:
        print("用法: python imagebuilder.py 'ID,Target'")
        sys.exit(1)
    
    input_string = sys.argv[1]
    
    try:
        id, target = parse_input(input_string)
    except ValueError as e:
        print(e)
        sys.exit(1)
    
    print(f"参数解析: ID={id}, Target={target}")

    firmware_version = os.getenv('VERSION', '23.05.3')
    url = build_image_download_url(firmware_version, target)
    print(f"下载URL: {url}")

    filename = download_file_with_progress(url)
    extract_with_progress(filename)

if __name__ == "__main__":
    main()