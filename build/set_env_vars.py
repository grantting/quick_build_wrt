import os
import json
import subprocess

def parse_json(input_json):
    try:
        return json.loads(input_json)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return None

def set_environment_variables(parameters_json, firmware_version):
    # 解析JSON输入
    parameters = parse_json(parameters_json)
    if parameters is None:
        print("Invalid JSON input provided.")
        return

    # 提取所需的值
    model_name = parameters.get('model_name', '')
    target_platform = parameters.get('target_platform', '')

    # 构建设置环境变量的命令
    env_commands = [
        f'echo "MODEL_NAME={model_name}" >> $GITHUB_ENV',
        f'echo "TARGET_PLATFORM={target_platform}" >> $GITHUB_ENV',
        f'echo "FIRMWARE_VERSION={firmware_version}" >> $GITHUB_ENV',
        f'echo "PARAMETERS_JSON={parameters_json}" >> $GITHUB_ENV',
        f'echo "URL_PLATFORM={target_platform}" >> $GITHUB_ENV'
    ]

    # 执行设置环境变量的命令
    for command in env_commands:
        subprocess.run(command, shell=True, check=True)

def main():
    # 读取环境变量
    parameters_json_input = os.getenv('INPUT_PARAMETERS_JSON', '{}')
    firmware_version_input = os.getenv('INPUT_FIRMWARE_VERSION', '')

    # 设置环境变量
    set_environment_variables(parameters_json_input, firmware_version_input)

if __name__ == "__main__":
    main()