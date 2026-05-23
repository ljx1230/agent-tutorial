# 🐍 第 1 课：Python 环境搭建与基础语法

> 面向学员：ljx  
> 目标：从零开始搭建 Python 开发环境，并写出第一个 Python 程序

---

## 📦 一、安装 Python

### 1.1 下载 Python

- 访问官网：[https://www.python.org/downloads/](https://www.python.org/downloads/)
- 推荐下载 **Python 3.10 及以上版本**（目前最新稳定版为 3.12/3.13）
- 根据你的操作系统选择对应版本：
  - **Windows**：下载 `Windows installer (64-bit)`
  - **macOS**：下载 `macOS 64-bit universal2 installer`
  - **Linux**：使用包管理器安装（如 `sudo apt install python3`）

### 1.2 安装步骤（Windows 为例）

1. 双击下载的安装包
2. **⚠️ 重要：勾选「Add Python to PATH」**（将 Python 添加到环境变量）
3. 点击「Install Now」开始安装
4. 安装完成后，打开命令提示符（CMD），输入以下命令验证：

```bash
python --version
```

如果显示类似 `Python 3.12.0`，说明安装成功 ✅

---

## 💻 二、安装 IDE（代码编辑器）

推荐以下两种，任选其一即可：

### 选项 A：VS Code（推荐）
- 下载地址：[https://code.visualstudio.com/](https://code.visualstudio.com/)
- 安装后，在扩展商店搜索并安装 **Python 扩展**（由 Microsoft 提供）
- 优点：轻量、免费、插件丰富

### 选项 B：PyCharm
- 下载地址：[https://www.jetbrains.com/pycharm/download/](https://www.jetbrains.com/pycharm/download/)
- 初学者使用 **Community（社区版）** 即可，免费
- 优点：专为 Python 设计，开箱即用

---

## 🚀 三、第一个 Python 程序

### 3.1 在交互式环境中运行

打开终端（CMD / 终端），输入 `python` 进入交互模式：

```python
>>> print("Hello, World!")
Hello, World!
>>> exit()  # 退出交互模式
```

### 3.2 创建并运行 Python 文件

1. 新建一个文件，命名为 `hello.py`
2. 输入以下代码：

```python
print("Hello, World!")
print("你好，我是 ljx！")
```

3. 在终端中运行：

```bash
python hello.py
```

输出结果：
```
Hello, World!
你好，我是 ljx！
```

🎉 **恭喜！你写下了人生中第一个 Python 程序！**

---

## 📚 四、变量与数据类型

### 4.1 什么是变量？

变量就像是一个**标签**，用来存储数据。

```python
# 赋值语法：变量名 = 值
name = "ljx"       # 字符串
age = 25           # 整数
height = 1.75      # 浮点数
is_student = True  # 布尔值
```

### 4.2 基本数据类型

| 类型 | 英文名 | 示例 | 说明 |
|------|--------|------|------|
| 整数 | `int` | `10`, `-3`, `0` | 不带小数点的数字 |
| 浮点数 | `float` | `3.14`, `-0.5`, `2.0` | 带小数点的数字 |
| 字符串 | `str` | `"你好"`, `'Python'` | 用引号括起来的文本 |
| 布尔值 | `bool` | `True`, `False` | 只有两个值：真/假 |

### 4.3 类型查看

```python
print(type(10))        # <class 'int'>
print(type(3.14))      # <class 'float'>
print(type("Hello"))   # <class 'str'>
print(type(True))      # <class 'bool'>
```

---

## ⌨️ 五、输入与输出

### 5.1 输出：`print()`

```python
print("Hello, World!")           # 输出字符串
print(42)                        # 输出数字
print("年龄：", 25)              # 输出多个值，自动加空格
print("姓名：" + "ljx")          # 字符串拼接
```

### 5.2 输入：`input()`

```python
name = input("请输入你的名字：")
print("你好，" + name + "！")
```

运行示例：
```
请输入你的名字：ljx
你好，ljx！
```

> ⚠️ `input()` 返回的数据类型**永远是字符串**，如果需要数字，要手动转换。

```python
age = input("请输入你的年龄：")     # 返回字符串 "25"
age = int(age)                      # 转换为整数 25
print("明年你", age + 1, "岁了")
```

---

## 📝 六、注释与代码规范

### 6.1 注释

注释是给**人看**的，Python 会忽略它们。

```python
# 这是单行注释，用 # 开头

"""
这是多行注释
可以写多行内容
用三个引号包裹
"""
```

### 6.2 Python 代码规范（PEP 8）

- **缩进**：统一使用 **4 个空格**（不要混用 Tab 和空格）
- **命名**：
  - 变量名：小写字母 + 下划线，如 `my_name`、`student_age`
  - 常量名：全大写，如 `PI = 3.14`
- **等号两边加空格**：`name = "ljx"` ✅ 而不是 `name="ljx"`
- **逗号后加空格**：`print("a", "b")` ✅

---

## 🧪 七、动手练习

尝试在本地新建一个 `lesson1_practice.py` 文件，完成以下练习：

```python
# 练习1：自我介绍
name = input("请输入你的名字：")
age = int(input("请输入你的年龄："))
print("我叫", name, "，今年", age, "岁")

# 练习2：简单计算器
a = int(input("请输入第一个数字："))
b = int(input("请输入第二个数字："))
print("两数之和：", a + b)
print("两数之差：", a - b)
print("两数之积：", a * b)
print("两数之商：", a / b)
```

---

## 📖 八、本节课总结

| 知识点 | 掌握情况 |
|--------|:--------:|
| Python 安装与环境配置 | ⬜ |
| IDE 安装（VS Code / PyCharm） | ⬜ |
| 第一个程序 `print("Hello, World!")` | ⬜ |
| 变量与 4 种基本数据类型 | ⬜ |
| `input()` 输入与 `print()` 输出 | ⬜ |
| 类型转换（`int()`、`str()`） | ⬜ |
| 注释与代码规范 | ⬜ |

> 💡 **课后建议**：把上面的练习代码亲手敲一遍，遇到报错不要慌，仔细看错误信息，这是学习编程的必经之路！

---

## 🔗 九、参考资料

- Python 官方文档：[https://docs.python.org/3/tutorial/](https://docs.python.org/3/tutorial/)
- VS Code 下载：[https://code.visualstudio.com/](https://code.visualstudio.com/)
- PyCharm 下载：[https://www.jetbrains.com/pycharm/](https://www.jetbrains.com/pycharm/)

---

> 📝 本课件由 **ljx** 专属定制，加油，你已经迈出了 Python 学习的第一步！🚀
