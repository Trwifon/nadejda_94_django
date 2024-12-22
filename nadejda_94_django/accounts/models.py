from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models
from nadejda_94_django.validators import username_validator


class User(AbstractUser):
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[MinLengthValidator(4), username_validator],
    )

    email = models.EmailField(
        unique=True
    )

    def __str__(self):
        return self.username

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
