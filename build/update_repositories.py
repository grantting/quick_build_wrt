# 指定文件路径
file_path = './repositories.conf'

try:
    # 读取原始文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    modified = False  # 标记是否进行了修改
    new_content = []  # 存储修改后的新内容

    # 遍历每一行，寻找需要替换的行
    for line in lines:
        if 'src/gz immortalwrt_packages' in line:
            # 分割字符串
            parts = line.split('/packages')
            if len(parts) == 3:
                # 替换前一部分，并拼接成新的字符串
                new_line = f'src/gz immortalwrt_packages https://op.dllkids.xyz/packages{parts[1]}\n'
                new_content.append(new_line)
                modified = True
            else:
                new_content.append(line)
        else:
            new_content.append(line)

    # 如果进行了修改，覆盖原文件
    if modified:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(new_content)
        print("文件已成功更新。")
        print("新的文件内容如下：")
        with open(file_path, 'r', encoding='utf-8') as updated_file:
            print(updated_file.read())
    else:
        print("没有找到需要替换的行。")

except FileNotFoundError:
    print(f"错误：'{file_path}' 文件未找到。请检查文件路径是否正确。")

except PermissionError:
    print(f"错误：没有权限读取或写入 '{file_path}' 文件。请检查是否有足够的权限。")

except Exception as e:
    print(f"发生了意外的错误：{e}")