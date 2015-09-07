import sys


def fn_1():
    global var_1
    global var_2
    return var_1 + var_2

def fn_2():
    var_1 = 1
    var_2 = 2
    return fn_1()
