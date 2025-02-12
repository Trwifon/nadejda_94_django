from numpy import number


def calculate_area(width, height, number):
    MIN_AREA = 0.3

    area = width * height / 1000000
    area = MIN_AREA if area < MIN_AREA else area
    area *= number
    return round(area, 2)


def calculate_price(width, height, unit_price, number):
    area = calculate_area(width, height, number)

    price = round((unit_price * area),2)

    return price


def get_glass_kind(order):
    if order.third_glass:
        kind = f"{order.first_glass}+{order.second_glass}+{order.third_glass}/{order.thickness}"
    elif order.second_glass:
        kind = f"{order.first_glass}+{order.second_glass}/{order.thickness}"
    else:
        kind = f"ед.стъкло-{order.first_glass}"

    return kind





