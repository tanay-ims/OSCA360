from django.db import models
from django.utils import timezone
import os

# Upload path function
def get_document_upload_path(instance, filename):
    senior = instance.senior_citizen
    document_type = instance.document.document_type

    lastname = ''.join(c for c in (senior.lastname or '').replace(' ', '_') if c.isalnum() or c == '_')[:50]
    firstname = ''.join(c for c in (senior.firstname or '').replace(' ', '_') if c.isalnum() or c == '_')[:50]
    suffix = ''.join(c for c in (senior.suffix or '') if c.isalnum() or c == '_')[:10]
    middlename = ''.join(c for c in (senior.middlename or '') if c.isalnum() or c == '_')[:50]

    name_parts = [part for part in [document_type, lastname, firstname, suffix, middlename] if part]
    clean_filename = f"{'_'.join(name_parts)}.pdf"
    return os.path.join('uploads', clean_filename)

# DocumentaryRequirement model
class DocumentaryRequirement(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('BC', 'Barangay Clearance'),
        ('ID', 'Identification Card'),
        ('PX', 'Picture'),
        ('OT','Other'),
    ]

    code = models.CharField(max_length=2, unique=True)
    document_type = models.CharField(max_length=2, choices=DOCUMENT_TYPE_CHOICES)
    document_name = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_name} ({self.code})"

    class Meta:
        ordering = ['code']

# SeniorCitizen model
class SeniorCitizen(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    STATUS_CHOICES = [('A', 'Active'), ('D', 'Deceased'), ('T', 'Transferred')]
    CIVIL_STATUS_CHOICES = [('S', 'Single'), ('M', 'Married'), ('W', 'Widowed'), ('D', 'Divorced'), ('SP', 'Separated')]

    osca_id = models.CharField(max_length=6, unique=True)
    registry_reference_number = models.CharField(max_length=7, unique=True)
    firstname = models.CharField(max_length=50)
    middlename = models.CharField(max_length=50, blank=True, null=True)
    lastname = models.CharField(max_length=50)
    suffix = models.CharField(max_length=4, blank=True, null=True)
    address = models.TextField()
    barangay = models.ForeignKey('sc_app.Barangay', on_delete=models.SET_NULL, null=True)
    city_municipality = models.ForeignKey('sc_app.CityMunicipality', on_delete=models.SET_NULL, null=True)
    province = models.ForeignKey('sc_app.Province', on_delete=models.SET_NULL, null=True)
    date_of_birth = models.DateField()
    place_of_birth_city_municipality = models.ForeignKey('sc_app.CityMunicipality', on_delete=models.SET_NULL, null=True, related_name='seniors_born_city')
    place_of_birth_province = models.ForeignKey('sc_app.Province', on_delete=models.SET_NULL, null=True, related_name='seniors_born_province')
    sex = models.CharField(max_length=1, choices=GENDER_CHOICES)
    civil_status = models.CharField(max_length=2, choices=CIVIL_STATUS_CHOICES)
    ethnicity = models.ForeignKey('sc_app.Ethnicity', on_delete=models.SET_NULL, null=True)
    religion = models.ForeignKey('sc_app.Religion', on_delete=models.SET_NULL, null=True)
    disability = models.ForeignKey('sc_app.Disability', on_delete=models.SET_NULL, null=True, blank=True)
    emergency_contact = models.ForeignKey('sc_app.EmergencyContact', on_delete=models.SET_NULL, null=True, blank=True)
    relationship = models.ForeignKey('sc_app.Relationship', on_delete=models.SET_NULL, null=True)
    contact_number = models.CharField(max_length=15, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    date_enrolled = models.DateField(default=timezone.now)
    documents = models.ManyToManyField(DocumentaryRequirement, through='SeniorCitizenDocument', blank=True)

    def get_age(self):
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    def __str__(self):
        return f"{self.lastname}, {self.firstname} ({self.osca_id})"

    class Meta:
        verbose_name_plural = "Senior Citizens"
        indexes = [models.Index(fields=['osca_id'])]

# SeniorCitizenDocument model
class SeniorCitizenDocument(models.Model):
    senior_citizen = models.ForeignKey(SeniorCitizen, on_delete=models.CASCADE)
    document = models.ForeignKey(DocumentaryRequirement, on_delete=models.CASCADE)
    file = models.FileField(upload_to=get_document_upload_path, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.senior_citizen} - {self.document.document_name}"

    class Meta:
        unique_together = ('senior_citizen', 'document')