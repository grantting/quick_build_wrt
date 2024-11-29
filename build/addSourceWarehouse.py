import os
import re

# 读取环境变量 PLATFORM
platform = os.getenv('PLATFORM', 'ipq807x/generic')
if not platform:
    raise ValueError("Environment variable PLATFORM is not set")

# 读取.config文件，获取arch_packages
with open('.config', 'r') as file:
    config_content = file.read()

match = re.search(r'CONFIG_TARGET_ARCH_PACKAGES="([^"]+)"', config_content)
if match:
    arch_packages = match.group(1)
else:
    raise ValueError("Could not find CONFIG_TARGET_ARCH_PACKAGES in the .config file")

print(f"Arch Packages: {arch_packages}")

# 构建自定义仓库URL
custom_repo_url = f"https://mirrors.ustc.edu.cn/immortalwrt/releases/23.05.4/packages/{arch_packages}/luci"
custom_repo_line = f"src/gz ustc_luci {custom_repo_url}"

# 定义 repositories.conf 文件路径
repo_conf_path = "repositories.conf"  # 替换为实际的文件路径

# 读取现有配置文件内容
with open(repo_conf_path, 'r') as file:
    lines = file.readlines()

# 找到插入点
insert_index = None
for i, line in enumerate(lines):
    if "## Place your custom repositories here, they must match the architecture and version." in line:
        insert_index = i + 1
        break

# 如果找到了插入点，则插入新行
if insert_index is not None:
    lines.insert(insert_index, custom_repo_line + '\n')
else:
    raise ValueError("Insertion point not found in repositories.conf")

# 将更新后的内容写回文件
with open(repo_conf_path, 'w') as file:
    file.writelines(lines)

print(f"Custom repository added to {repo_conf_path}")