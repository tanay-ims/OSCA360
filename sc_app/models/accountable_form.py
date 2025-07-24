# models/accountable_form.py
from django.db import models

class AccountableForm(models.Model):
    FORM_TYPES = (
        ('PB', 'Purchase Booklet'),
        ('ID', 'ID Card'),
    )
    name = models.CharField(max_length=20, choices=FORM_TYPES, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.get_name_display()