from django.db import models
from .validators import validate_bitlocker_key

class AssetType(models.TextChoices):
    AV = 'A/V', 'A/V Equipment'
    COMPUTER = 'COM', 'Computer'
    MONITOR = 'MON', 'Monitor'
    NETWORK = 'NET', 'Network Equipment'
    PERIPHERAL = 'PER', 'Peripheral'
    PRINTER = 'PRT', 'Printer'
    PROJECTOR = 'PRJ', 'Projector'
    SERVER = 'SRV', 'Server'
    SOFTWARE = 'SFT', 'Software'
    OTHER = 'OTH', 'Other'

class Asset(models.Model):
    inventory_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=3, choices=AssetType.choices)
    location = models.CharField(max_length=100)
    details = models.TextField()
    purchase_date = models.DateField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    bitlocker_key = models.CharField(
        max_length=100,  # Allow for formatting characters
        blank=True,
        null=True,
        validators=[validate_bitlocker_key],
        help_text="BitLocker recovery key for this device (48 digits, staff only)"
    )

    def __str__(self):
        return f"{self.inventory_number} - {self.name}"