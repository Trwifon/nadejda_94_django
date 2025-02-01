from datetime import datetime
from nadejda_94_django.records.models import Order, Partner, Record
month_dict = {1: "I", 2: "II", 3: "III",
              4: "IV", 5: "V", 6: "VI",
              7: "VII", 8: "VIII", 9: "IX",
              10: "X", 11: "XI", 12: "XII"}

def get_order(order_type):
    orders = Order.objects.first()
    date = datetime.now().month
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


def get_close_balance(partner_id, order_type, difference):
    open_balance = Partner.objects.get(id=partner_id).balance

    if partner_id in (1, 2):
        return 0

    if order_type in ['C', 'B']:
        return int(open_balance) + int(difference)
    else:
        return int(open_balance) - int(difference)


def errors_test():
    start_time = datetime.now()
    test_result = []
    partners = Partner.objects.all().order_by('name')

    for partner in partners:
        if partner.id not in (1, 2):
            firm_report = create_firm_report(partner)
            if firm_report:
                record_balance = firm_report.first().balance

            if partner.balance != record_balance:
               test_result.append(f"Гр"
                                  f"ешка в баланса на {partner.name}")

    if not test_result:
        test_result.append('Няма грешки')

    end_time = datetime.now()
    test_time = end_time - start_time
    print(test_time.microseconds/1000000)


def create_firm_report(current_partner):
    firm_report = (Record.objects.filter(partner=current_partner).order_by('pk'))

    cumulative_sum = 0

    for record in firm_report:
        if record.order_type in ['C', 'B']:
            cumulative_sum += record.amount
        else:
            cumulative_sum -= record.amount
        record.balance = cumulative_sum
        record.save()

    return firm_report.reverse()




