from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from nadejda_94_django.glasses.choices import GlassChoices, ThicknessChoices
from nadejda_94_django.records.models import Partner, Order, Record


class Glasses(models.Model):
    first_glass = models.CharField(
        max_length=12,
        choices=GlassChoices.choices
    )

    second_glass = models.CharField(
        max_length=12,
        choices=GlassChoices.choices,
        null=True,
        blank=True
    )

    third_glass = models.CharField(
        max_length=12,
        choices=GlassChoices.choices,
        null=True,
        blank=True
    )

    thickness = models.IntegerField(
        choices=ThicknessChoices.choices,
    )

    width = models.IntegerField(
        validators=[MinValueValidator(8), MaxValueValidator(3210)],
    )

    height = models.IntegerField(
        validators=[MinValueValidator(8), MaxValueValidator(3210)],
    )

    number = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )

    unit_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(5)],
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    prepared_for_working = models.BooleanField(
        default=False
    )

    sent_for_working = models.DateField(
        null=True,
        blank=True
    )

    partner = models.ForeignKey(
        to=Partner,
        on_delete=models.DO_NOTHING,
    )

    order = models.ForeignKey(
        to=Record,
        on_delete=models.DO_NOTHING,
    )

    price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
    )


