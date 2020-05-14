from sympy import *
from datetime import datetime

if __name__ == "__main__":
    """使用SymPy进行方程求解"""
    x = Symbol('x')
    # str = '100 * (1 + x)**3 - 200'
    str = '5000 * (1 + x)**1 + 5000*(1 + x)**1.6 + 5000*(1 + x)**1.2 - 15000'
    print(solve(str, x))
    # print(solve(str, x)[0].evalf())
    # print(solve(str, x))
    # print(solve(2 ** x - 4, x))
