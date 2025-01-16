from django.db import models
from django.db.models import TextChoices


users_dict = {'Trifon': 'M', 'Tsonka': 'O', 'Elena': 'A', 'Diana': 'P', 'Nadya': 'G'}


class WarehouseChoices(models.TextChoices):
    Elena = 'A', 'Алуминий'
    Nadya = 'G', 'Стъклопакети'
    Diana = 'P', 'PVC'
    Tsonka = 'O', 'Поръчки'
    Trifon = 'M', 'Управител'


class OrderTypeChoices(TextChoices):
    CASH = 'C', 'Каса'
    BANK = 'B', 'Банка'
    SELL = 'S', 'Продажба'
    ORDER_ALUMINUM = 'A', 'Поръчка Алуминий'
    ORDER_GLASS = 'G', 'Поръчка Стъклопакети'
    ORDER_PVC = 'P', 'Поръчка PVC'


class PartnerTypeChoices(TextChoices):
    SUPPLIER = 'S', 'Доставчик'
    FIRM = 'F', 'Фирма'
    RETAIL_CUSTOMER = 'RC', 'Клиент на дребно'


class YearChoices(models.IntegerChoices):
    YEAR_FOUR = 2024, '2024'
    YEAR_FIVE = 2025, '2025'
    YEAR_SIX = 2026, '2026'
    YEAR_SEVEN = 2027, '2027'
    YEAR_EIGHT = 2028, '2028'
    YEAR_NINE = 2029, '2029'
    YEAR_TEN = 2030, '2030'


class MonthChoices(models.IntegerChoices):
    JANUARY = 1, 'Януари'
    FEBRUARY = 2, 'Февруари'
    MARCH = 3, 'Март'
    APRIL = 4, 'Април'
    MAY = 5, 'Май'
    JUNE = 6, 'Юни'
    JULY = 7, 'Юли'
    AUGUST = 8, 'Август'
    SEPTEMBER = 9, 'Септември'
    OCTOBER = 10, 'Октомври'
    NOVEMBER = 11, 'Ноември'
    DECEMBER = 12, 'Декември'


class ReportChoices(TextChoices):
    FIRM_REPORT = 'FR', 'Фирмен отчет'
    DAY_REPORT = 'DR', 'Дневен отчет'
    MONTH_REPORT = 'MR', 'Месечен отчет'

