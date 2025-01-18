from datetime import datetime
from nadejda_94_django.records.models import Order, Partner, Record


def get_order(order_type):
    orders = Order.objects.first()

    date = datetime.now().month
    month_dict = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
                  7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"}
    current_month = month_dict[date]
    db_month = orders.month

    counter = 0
    if order_type == 'A':
        counter = orders.al_counter
    elif order_type == 'G':
        order_type = 'C'
        counter = orders.glass_counter
    elif order_type == 'P':
        counter = orders.pvc_counter
    else:
        return ''

    if current_month != db_month:
        orders.month = current_month
        orders.al_counter, orders.glass_counter, orders.pvc_counter = 1, 1, 1
        orders.save()
        counter = 1

    update_order(order_type)

    return f"{order_type}-{current_month}-{counter}"


def update_order(order_type):
    orders = Order.objects.first()

    if order_type == 'A':
        orders.al_counter += 1
    elif order_type == 'C':
        orders.glass_counter += 1
    elif order_type == 'P':
        orders.pvc_counter += 1

    orders.save()

    return


def get_close_balance(partner_id, order_type, amount):
    open_balance = Partner.objects.get(id=partner_id).balance

    if partner_id == 1 or partner_id == 2:
        return 0

    if order_type in ['C', 'B']:
        return int(open_balance) + int(amount)
    else:
        return int(open_balance) - int(amount)


def errors_test():
    start_time = datetime.now()
    test_result = []
    partners = Partner.objects.all().order_by('name')

    for partner in partners:
        if partner.id not in (1, 2):
            partner_records = Record.objects.filter(partner=partner).order_by('pk')

            if partner_records:
                current_balance = partner_records[0].balance
                record_error = 0
                last_record_and_partner_error = 0
                total_error = 0

                for record in partner_records[1:]:
                    if record.order_type in ('C', 'B'):
                        current_balance += record.amount
                    else:
                        current_balance -= record.amount

                    if record.balance != current_balance:
                        record_error += 1

                if partner.balance != partner_records.last().balance:
                    last_record_and_partner_error += 1

                if partner.balance != current_balance:
                    total_error += 1

                if record_error != 0 or last_record_and_partner_error != 0 or total_error != 0:
                    test_result.append(f"{partner.name}: "
                       f"(Грешки в баланса на запис: {record_error}, "
                       f"Разлика между балансите в последния запис и фирмата: {last_record_and_partner_error}, "
                       f"Разлика между сумата от вички записи и фирмата: {total_error})")
    end_time = datetime.now()
    test_time = end_time - start_time
    print(test_time.microseconds/1000000)
    return test_result





