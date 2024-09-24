import os

def find_repositories_conf():
    # 查找 repositories.conf 文件
    for root, dirs, files in os.walk('.'):
        if 'repositories.conf' in files:
            return os.path.join(root, 'repositories.conf')
    return None

def update_repositories_conf(file_path):
    # 更新 repositories.conf 文件中的 URL
    lines = []
    updated = False
    
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('src/gz immortalwrt_packages'):
                parts = line.split()
                if len(parts) >= 3:
                    url = parts[2]
                    new_url = url.replace('https://downloads.immortalwrt.org/releases/23.05.3/packages/', 'https://op.dllkids.xyz/packages/')
                    new_url = new_url.rstrip('/packages')
                    
                    if new_url != url:
                        parts[2] = new_url
                        updated = True
                line = ' '.join(parts) + '\n'
            lines.append(line)
    
    if updated:
        with open(file_path, 'w') as file:
            file.writelines(lines)
    
    return updated

if __name__ == "__main__":
    repositories_conf_path = find_repositories_conf()
    if repositories_conf_path and update_repositories_conf(repositories_conf_path):
        print(f"Updated URL in {repositories_conf_path}")
    else:
        print("Did not find repositories.conf or no changes made.")