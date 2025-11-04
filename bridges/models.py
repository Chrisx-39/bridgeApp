from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Bridge(models.Model):
    BRIDGE_TYPES = [
        ('BEAM_COMPOSITE', 'Beam Composite Bridge'),
        ('SUSPENSION', 'Suspension Bridge'),
        ('ARCH', 'Arch Bridge'),
        ('TRUSS', 'Truss Bridge'),
    ]
    
    MATERIAL_CHOICES = [
        ('STEEL_CONCRETE', 'Steel and Concrete'),
        ('CONCRETE', 'Concrete'),
        ('STEEL', 'Steel'),
    ]
    
    CONDITION_CHOICES = [
        ('POOR', 'Poor'),
        ('FAIR', 'Fair'),
        ('GOOD', 'Good'),
        ('VERY_GOOD', 'Very Good'),
        ('EXCELLENT', 'Excellent'),
    ]

    name = models.CharField(max_length=100, unique=True)
    bridge_type = models.CharField(max_length=50, choices=BRIDGE_TYPES)
    length = models.DecimalField(max_digits=6, decimal_places=3, help_text="Length in meters")
    width = models.DecimalField(max_digits=5, decimal_places=2, help_text="Width in meters")
    lanes = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    material = models.CharField(max_length=50, choices=MATERIAL_CHOICES)
    year_built = models.PositiveIntegerField()
    route = models.TextField(help_text="Route description")
    gps_coordinates = models.TextField(help_text="GPS coordinates (comma-separated)")
    
    # Condition ratings (1-5 scale)
    deck_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    girders_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    piers_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    abutment_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    
    condition_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Bridge'
        verbose_name_plural = 'Bridges'

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        ratings = [r for r in [self.deck_rating, self.girders_rating, 
                               self.piers_rating, self.abutment_rating] if r]
        return round(sum(ratings) / len(ratings), 1) if ratings else None

    @property
    def condition_category(self):
        avg = self.average_rating
        if not avg:
            return 'Unknown'
        if avg >= 4.5:
            return 'Excellent'
        elif avg >= 3.5:
            return 'Very Good'
        elif avg >= 2.5:
            return 'Good'
        elif avg >= 1.5:
            return 'Fair'
        return 'Poor'

    @property
    def bci_percentage(self):
        """Bridge Condition Index as percentage"""
        avg = self.average_rating
        return int((avg / 5) * 100) if avg else 0


class TrafficData(models.Model):
    bridge = models.OneToOneField(Bridge, on_delete=models.CASCADE, related_name='traffic')
    heavy_vehicles = models.PositiveIntegerField(default=0, help_text="Daily count")
    small_vehicles = models.PositiveIntegerField(default=0, help_text="Daily count")
    recorded_date = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Traffic Data'
        verbose_name_plural = 'Traffic Data'

    def __str__(self):
        return f"Traffic data for {self.bridge.name}"

    @property
    def total_vehicles(self):
        return self.heavy_vehicles + self.small_vehicles


class MaintenanceRecord(models.Model):
    ACTION_TYPES = [
        ('MINOR_REPAIR', 'Minor Repairs'),
        ('ROUTINE', 'Routine Maintenance'),
        ('MONITORING', 'Normal Monitoring'),
        ('MAJOR_REPAIR', 'Major Repairs'),
        ('INSPECTION', 'Inspection'),
    ]
    
    bridge = models.ForeignKey(Bridge, on_delete=models.CASCADE, related_name='maintenance_records')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_date']
        verbose_name = 'Maintenance Record'
        verbose_name_plural = 'Maintenance Records'

    def __str__(self):
        return f"{self.bridge.name} - {self.action_type} ({self.scheduled_date})"