from openpyxl.reader.excel import load_workbook
from openpyxl.styles import Alignment, Font

def calculate_area(width, height, number):
    MIN_AREA = 0.3

    area = width * height / 1000000
    area = MIN_AREA if area < MIN_AREA else area
    area *= number
    return round(area, 2)


def calculate_price(area, unit_price, supplement):
    price = round((unit_price * area),2) + int(supplement)

    return price


def calculate_glass_data(ALL_ORDERS):
    glass_data = {
        'total_number': 0,
        'total_area': 0,
        'total_price': 0,
    }

    for order in ALL_ORDERS:
        area = calculate_area(order['width'], order['height'], order['number'])
        supplement = order['supplement'] if order['supplement'] else 0
        order['price'] = calculate_price(area, float(order['unit_price']), supplement)

        glass_data['total_number'] += order['number']
        glass_data['total_area'] += area
        glass_data['total_price'] += order['price']

    return glass_data


def get_glass_kind(order):
    if order.third_glass:
        kind = (f"{order.first_glass}"
                f"+{order.second_glass}"
                f"+{order.third_glass}"
                f"/{order.thickness} ")
                # f"{order.module}")

    elif order.second_glass:
        kind = (f"{order.first_glass}"
                f"+{order.second_glass}"
                f"/{order.thickness} ")
                # f"{order.module}")

    else:
        kind = (f"ед.стъкло"
                f"-{order.first_glass} ")

    if order.module:
        kind += f"{order.module}"

    return kind


def format_excel(file_path):
    wb = load_workbook(file_path)
    ws = wb.active
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 13
    ws.column_dimensions['C'].width = 6
    ws.column_dimensions['D'].width = 6
    ws.column_dimensions['E'].width = 3
    ws.column_dimensions['F'].width = 4
    ws.column_dimensions['G'].width = 4
    ws.column_dimensions['H'].width = 13
    ws.column_dimensions['I'].width = 5

    for cell in ws['C']:
        cell.font = Font(bold=True)
    for cell in ws['D']:
        cell.font = Font(bold=True)
    for cell in ws['I']:
        cell.font = Font(bold=True)

    for cell in ws['C']:
        cell.alignment = Alignment(horizontal='center')
    for cell in ws['D']:
        cell.alignment = Alignment(horizontal='center')
    for cell in ws['E']:
        cell.alignment = Alignment(horizontal='center')
    for cell in ws['F']:
        cell.alignment = Alignment(horizontal='center')
    for cell in ws['G']:
        cell.alignment = Alignment(horizontal='center')
    for cell in ws['H']:
        cell.alignment = Alignment(horizontal='center')

    ws['J1'].alignment = Alignment(horizontal='right')
    ws['K1'].alignment = Alignment(horizontal='left')
    ws['L1'].alignment = Alignment(horizontal='right')
    ws['M1'].alignment = Alignment(horizontal='left')

    wb.save(file_path)

    return None
