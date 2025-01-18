from django.db import models


class GlassChoices(models.TextChoices):
    FOUR = '4', '4'
    FIVE = '5', '5'
    SIX = '6', '6'
    K = 'K', 'K'
    MF = '4S', '4S'

class ThicknessChoices(models.IntegerChoices):
    TWELVE = 12, '12'
    FOURTEEN = 14, '14'
    SIXTEEN = 16, '16'
    EIGHTEEN = 18, '18'
    TWENTY = 20, '20'
    TWENTY_TWO = 22, '22'
    TWENTY_FOUR = 24, '24'

