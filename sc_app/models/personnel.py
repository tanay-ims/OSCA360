from django.db import models
from django.contrib.auth.models import User, Group
from sc_app.models.office import Office
from sc_app.models.designation import Designation

class Personnel(models.Model):
    contact_number = models.CharField(max_length=15, help_text="Used also as the initial password")
    lastname = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    middlename = models.CharField(max_length=50, blank=True, null=True)
    extension = models.CharField(max_length=10, blank=True, null=True)
    office = models.ForeignKey(Office, on_delete=models.SET_NULL, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.lastname}, {self.firstname}"
