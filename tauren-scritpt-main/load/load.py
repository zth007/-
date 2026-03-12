"""
读取文件
"""
import os

class Load:

    @staticmethod
    def load(file_name):
        """加载文件"""
        # 兼容从txt文件加载
        dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(dir, file_name)
        print("读取文件信息: " + file_path)
        link_items = []
        try:
            with open(file_path, 'r', encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    # 跳过注释行和空行
                    if not line or line.startswith("#"):
                        continue
                    link_items.append(line)
        except FileNotFoundError:
            print(f"文件 {file_name} 不存在，返回空列表")
        except Exception as e:
            print(f"读取文件 {file_name} 失败: {e}")
        return link_items

    @staticmethod
    def load_map(file_name):
        """加载映射文件"""
        # 兼容从txt文件加载
        dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(dir, file_name)
        print("读取文件信息: " + file_path)
        link_item_map = {}
        try:
            with open(file_path, 'r', encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    # 跳过注释行和空行
                    if not line or line.startswith("#"):
                        continue
                    line_items = line.split(">")
                    # 只处理格式正确的行
                    if len(line_items) >= 2:
                        link_item_map[line_items[0]] = ">".join(line_items[1:])
        except FileNotFoundError:
            print(f"文件 {file_name} 不存在，返回空字典")
        except Exception as e:
            print(f"读取文件 {file_name} 失败: {e}")
        return link_item_map