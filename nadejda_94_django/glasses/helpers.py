from numpy import number


def calculate_area(width, height, number):
    MIN_AREA = 0.3

    area = width * height / 1000000
    area = MIN_AREA if area < MIN_AREA else area
    area *= number
    return round(area, 2)


def calculate_price(area, unit_price):
    price = round((unit_price * area),2)
    # price = unit_price * area

    return price

def calculate_glass_data(ALL_ORDERS):
    glass_data = {
        'total_number': 0,
        'total_area': 0,
        'total_price': 0,
    }

    for order in ALL_ORDERS:
        area = calculate_area(order['width'], order['height'], order['number'])
        order['price'] = calculate_price(area, float(order['unit_price']))

        glass_data['total_number'] += order['number']
        glass_data['total_area'] += area
        glass_data['total_price'] += order['price']

    return glass_data





def get_glass_kind(order):
    if order.third_glass:
        kind = f"{order.first_glass}+{order.second_glass}+{order.third_glass}/{order.thickness}"
    elif order.second_glass:
        kind = f"{order.first_glass}+{order.second_glass}/{order.thickness}"
    else:
        kind = f"ед.стъкло-{order.first_glass}"

    return kind





