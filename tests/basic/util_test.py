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


print(normalize_func(lambda: read('numbers.txt')))
print(normalize_func(lambda: read('numbers.txt')))
cMD5 = '74c1877caa2c9904d1f77ef6df09a9d8'

print(cMD5[4]+cMD5[1]+cMD5[16]+cMD5[9]+cMD5[19]+cMD5[30]+cMD5[28]+cMD5[22])