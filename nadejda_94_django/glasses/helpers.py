def calculate_price(width, height, unit_price, number):
    MIN_AREA = 0.3

    area = width * height / 1000000
    area = MIN_AREA if area < MIN_AREA else area

    price = round((unit_price * area * number),2)

    return price
