
STREET_NUMBER_RANGE_TYPE_ALL = 1
STREET_NUMBER_RANGE_TYPE_ODD = 2
STREET_NUMBER_RANGE_TYPE_EVEN = 3


def get_special_range(start_number, finish_number, type_of):
    """
    """
    numbers = []
    if type_of == STREET_NUMBER_RANGE_TYPE_ALL:
        for i in range(start_number, finish_number):
            numbers.append(i)
    elif type_of == STREET_NUMBER_RANGE_TYPE_ODD:
        for i in range(start_number, finish_number):
            if i % 2 != 0:
                numbers.append(i)
    elif type_of == STREET_NUMBER_RANGE_TYPE_EVEN:
        for i in range(start_number, finish_number):
            if i % 2 == 0:
                numbers.append(i)
    else:
        raise Exception("Unsupported `type_of` parameter specified.")
    return numbers
