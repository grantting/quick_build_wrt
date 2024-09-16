import os
import json
import subprocess

def parse_json(input_json):
    try:
        return json.loads(input_json)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return None

def main():
    # 读取环境变量
    parameters_json_input = os.getenv('INPUT_PARAMETERS_JSON', '{}')
    firmware_version_input = os.getenv('INPUT_FIRMWARE_VERSION', '')

    # 解析JSON输入
    parameters_json = parse_json(parameters_json_input)
    if parameters_json is None:
        print("Invalid JSON input provided.")
        return

    # 提取所需的值
    model_name = parameters_json.get('model_name', '')
    target_platform = parameters_json.get('target_platform', '')

    # 将值写回到环境变量
    os.environ['MODEL_NAME'] = model_name
    os.environ['TARGET_PLATFORM'] = target_platform
    os.environ['FIRMWARE_VERSION'] = firmware_version_input
    os.environ['PARAMETERS_JSON'] = parameters_json_input
    os.environ['URL_PLATFORM'] = target_platform

    # 输出确认信息
    print(f"MODEL_NAME={model_name}")
    print(f"TARGET_PLATFORM={target_platform}")
    print(f"FIRMWARE_VERSION={firmware_version_input}")
    print(f"PARAMETERS_JSON={parameters_json_input}")
    print(f"URL_PLATFORM={target_platform}")

if __name__ == "__main__":
    main()