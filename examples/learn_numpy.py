# flake8: noqa


def main():
    def funA(fn):
        print('A')
        fn()
        return 'fkit'

    @funA
    def funB():
        print('B')

    print(funB)


if __name__ == "__main__":
    main()
