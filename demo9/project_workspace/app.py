from utils import greet_user


def main() -> None:
    name = input("Please enter your name: ").strip()
    print(greet_user(name))


if __name__ == "__main__":
    main()
