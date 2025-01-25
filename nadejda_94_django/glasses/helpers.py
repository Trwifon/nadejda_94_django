from django.db.models import Sum

from nadejda_94_django.records.helpers import get_close_balance, update_order
from nadejda_94_django.records.models import Record


def calculate_price(width, height, unit_price, number):
    MIN_AREA = 0.3

    area = width * height / 1000000
    area = MIN_AREA if area < MIN_AREA else area

    price = round((unit_price * area * number),2)

    return price


def get_glass_update_record(partner, current_total_price, order, warehouse):
    old_total_price = Record.objects.filter(order=order).aggregate(amount=Sum('amount'))
    correction = current_total_price - old_total_price

    record_instance = Record

    record_instance.warehouse = warehouse
    record_instance.order_type = 'G'
    record_instance.amount = correction
    record_instance.balance = get_close_balance(partner.id, 'G', correction)
    record_instance.order = order
    record_instance.note = 'Корекция'
    record_instance.partner = partner.id

    update_order('C')





