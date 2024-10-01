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

# 构造目录路径
directory = f"../target/linux/{platform}/base-files/etc/uci-defaults"
# 文件路径
file_path = os.path.join(directory, "99-custom")

# 检查目录是否存在
if os.path.exists(directory):
    # 创建文件并写入内容
    with open(file_path, 'w') as file:
        file.write(content)
    print(f"File '{file_path}' has been created.")
else:
    # 输出当前所在目录
    print(f"The directory '{directory}' does not exist.")
    print(f"Current directory is '{os.getcwd()}'")