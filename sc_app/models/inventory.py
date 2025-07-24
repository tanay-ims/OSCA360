# models/inventory.py
from django.db import models
from sc_app.models.accountable_form import AccountableForm

class Inventory(models.Model):
    form_type = models.ForeignKey(AccountableForm, on_delete=models.CASCADE, related_name='inventories')
    quantity_received = models.PositiveIntegerField()  # Initial stock received
    quantity_issued = models.PositiveIntegerField(default=0)  # Forms issued
    date_received = models.DateField()

    def quantity_available(self):
        return self.quantity_received - self.quantity_issued

    def __str__(self):
        return f"{self.form_type} (Batch: {self.batch_number or 'N/A'}, Available: {self.quantity_available()})"

    class Meta:
        verbose_name_plural = "Inventories"