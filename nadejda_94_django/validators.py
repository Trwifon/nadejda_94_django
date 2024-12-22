from django.core.exceptions import ValidationError

def username_validator(username):
    for char in username:
        if not (char.isalnum()):
            raise ValidationError("Вашето име трябва да съдържа само букви и цифри")