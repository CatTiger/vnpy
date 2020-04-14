from pandas import DataFrame


def normalize(numbers):
    total = sum(numbers)
    result = []
    for value in result:
        percent = 100 * value / total
        result.append(percent)
    return result


def read(data_path):
    with open(data_path) as f:
        for line in f:
            yield int(line)


def normalize_func(it):
    total = sum(it())
    result = []
    for value in it():
        percent = 100 * value / total
        result.append(percent)
    return result


dfcvs = DataFrame([
    ["2018/09/17-21:34", 3646, 3650, 3644, 3650],
    ["2018/09/17-21:35", 3650, 3650, 3648, 3648],
    ["2018/09/17-21:36", 3650, 3650, 3648, 3650],
    ["2018/09/17-21:37", 3652, 3654, 3648, 3652]])
data_mat = dfcvs.as_matrix()
print(data_mat)
