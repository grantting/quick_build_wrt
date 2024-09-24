import os
import requests
import gzip
from shutil import copyfileobj

# 指定文件路径
file_path = './repositories.conf'

# 存储构建后的下载链接
download_links = []

# 读取文件并检查每一行
with open(file_path, 'r') as file:
    for line in file:
        if 'src/gz immortalwrt_packages' in line:
            # 分割字符串
            parts = line.split('/packages')
            if len(parts) == 3:
                # 构建新的下载链接
                download_link = f'https://op.dllkids.xyz/packages{parts[1]}/Packages.gz'
                download_links.append(download_link)

# 创建 ./packages 目录（如果不存在）
download_folder = './packages'
os.makedirs(download_folder, exist_ok=True)

# 下载并解压每个文件
for link in download_links:
    # 获取文件名
    file_name = link.split('/')[-1]
    file_path = f'{download_folder}/{file_name}'
    extracted_file_path = f'{download_folder}/{file_name[:-3]}'

    # 下载文件
    response = requests.get(link, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f'Successfully downloaded {file_name} to {file_path}')

        # 解压文件
        with gzip.open(file_path, 'rb') as f_in:
            with open(extracted_file_path, 'wb') as f_out:
                copyfileobj(f_in, f_out)
        print(f'Successfully extracted {file_name} to {extracted_file_path}')
    else:
        print(f'Failed to download {link}: Status code {response.status_code}')