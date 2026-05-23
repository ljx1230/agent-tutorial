from utils import greet_user


def main() -> None:
    # 这个文件故意保持很小。
    # 第七课里，coding agent 更容易从这里顺着导入关系继续找到 utils.py。
    name = input("Please enter your name: ").strip()
    print(greet_user(name))


if __name__ == "__main__":
    main()
