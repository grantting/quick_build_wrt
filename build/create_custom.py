# 导入必要的模块
import os
import sys

# 检查是否提供了平台参数
if len(sys.argv) < 2:
    print("Usage: python build/create_custom.py PLATFORM")
    sys.exit(1)

# 获取平台参数
platform = sys.argv[1]

# 要写入的内容
content = """\
uci -q batch << EOI
set network.lan.ipaddr='192.168.10.1'
set system.hostname='Router'
EOI
"""

# 文件路径
file_path = f"./target/linux/{platform}/base-files/etc/uci-defaults/99-custom"

# 检查目录是否存在，如果不存在则创建
directory = os.path.dirname(file_path)
if not os.path.exists(directory):
    os.makedirs(directory)

# 写入内容到文件
with open(file_path, 'w') as file:
    file.write(content)

print(f"File '{file_path}' has been created.")