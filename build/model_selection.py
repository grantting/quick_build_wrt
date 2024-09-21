import subprocess
import requests
import json
import re
from functools import lru_cache

# 使用装饰器缓存版本号
@lru_cache(maxsize=None)
def get_default_version():
    config_url = "https://firmware-selector.openwrt.org/config.js"
    config_response = requests.get(config_url)
    if config_response.status_code == 200:
        match = re.search(r'default_version: "(.*)"', config_response.text)
        if match:
            return match.group(1)
    print("无法获取默认版本号。")
    return None

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None

def search_profiles(data, query):
    profiles = data.get('profiles', [])
    results = [(profile['id'], profile['target']) for profile in profiles if query.lower() in profile['id'].lower()]
    return results[:10]  # 最多返回10个结果

def display_results(results):
    if not results:
        print("未找到匹配项。")
        return {}, False
    
    mapping = {}
    print("查询结果:")
    for i, (id, target) in enumerate(results, start=1):
        print(f"[{i}]: {id}, {target}")
        mapping[str(i)] = (id, target)
    
    # 添加退出选项
    print("[0]: 按0退出查询")
    mapping['0'] = ('0', '0')  # 用于退出查询
    return mapping, True

def handle_query(data, query):
    results_mapping, has_results = display_results(search_profiles(data, query))
    
    if has_results:
        while True:
            selection = input("请选择一个结果（输入编号继续，输入查询关键字重新查询）: ")
            if selection == '0':
                print("退出查询。")
                return True, None  # 结束整个程序的查询
            elif selection.isdigit() and 1 <= int(selection) <= len(results_mapping) - 1:
                id, target = results_mapping[selection]
                print(f"您选择了: {id}, {target}")
                 # 构建命令行参数
                command = ['python', 'build/imagebuilder.py', id, target]
                
                # 调用 subprocess.run 来执行 imagebuilder.py 并传递参数
                subprocess.run(command)
                return True, None  # 结束整个程序的查询
            else:
                # 用户输入无效编号时，直接使用输入作为新的查询关键字
                return False, selection
    else:
        print("没有匹配项。")
        return False, query

def main():
    version = get_default_version()
    if version:
        url = f"https://firmware-selector.openwrt.org/data/{version}/overview.json"
        data = fetch_data(url)
        
        if data is not None:
            query = input("\n请输入查询关键字（按‘0’退出）: ")
            while True:
                should_exit, new_query = handle_query(data, query)
                if should_exit:
                    break
                else:
                    query = new_query

if __name__ == "__main__":
    main()