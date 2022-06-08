def is_odd(a):
    return bool(a - ((a >> 1) << 1))


def distribute(items, number):
    res = [  ]
    start = 0
    end = number
    for item in items:
        if items[start:end] == []:
            return res
        res.append(items[start:end])
        start += number
        end += number
    return res