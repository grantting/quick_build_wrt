import os
import subprocess
import json

def parse_parameters(parameters_json):
    try:
        parameters = json.loads(parameters_json)
        if not {'model_name', 'target_platform'}.issubset(set(parameters)):
            raise ValueError("Parameters must include 'model_name' and 'target_platform'.")
        return parameters['model_name'], parameters['target_platform']
    except Exception as e:
        raise ValueError("Invalid parameters JSON format.") from e

# 从环境变量获取 JSON 参数
parameters_json = os.getenv('PARAMETERS_JSON', '{}')

# 解析参数
try:
    model_name, target_platform = parse_parameters(parameters_json)
except ValueError as e:
    print(f"Error parsing parameters: {e}")
    exit(1)

# 设置 PROFILE 变量
PROFILE = model_name

# 初始化 PACKAGES 变量
PACKAGES = ""

# 读取 external-package.txt 文件并将每行添加到 PACKAGES 变量中
packages_file_path = "external-package.txt"
if os.path.exists(packages_file_path):
    with open(packages_file_path, 'r') as file:
        PACKAGES = ' '.join(line.strip() for line in file if line.strip())

# 其他构建参数
FILES = "files"
DISABLED_SERVICES = ""

# 构建 OpenWRT
build_command = f'make image PROFILE="{PROFILE}" PACKAGES="{PACKAGES}" FILES="{FILES}" DISABLED_SERVICES="{DISABLED_SERVICES}"'
subprocess.run(build_command, shell=True, check=True)

print("Build completed successfully.")