# models.py
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=250)
    email = models.CharField(max_length=250)
    password = models.CharField(max_length=250)

    def __str__(self):
        return self.username
    
# from django.db import models
# from datetime import timedelta

# class lt_july_01_final_data_12_hours(models.Model):
#     activity = models.CharField(max_length=255)
#     milestone = models.CharField(max_length=255)
#     labour_count = models.IntegerField(null=True, blank=True)
#     object_name = models.CharField(max_length=50, null=True, blank=True)
#     channel = models.CharField(max_length=50, null=True, blank=True)
#     date = models.DateField()
#     time = models.TimeField()
#     file_name = models.CharField(max_length=255, null=True, blank=True)
#     processing_time = models.FloatField(null=True, blank=True)  # ✅ Store converted interval in seconds
#     group_talking = models.BooleanField(default=False)
#     idle = models.BooleanField(default=False)
#     no_helmet = models.BooleanField(default=False)
#     group_count = models.IntegerField(null=True, blank=True)
#     idle_count = models.IntegerField(null=True, blank=True)
#     no_helmet_count = models.IntegerField(null=True, blank=True)
#     no_vest = models.BooleanField(default=False)
#     no_vest_count = models.IntegerField(null=True, blank=True)
#     box_coordinates = models.JSONField(null=True, blank=True)
#     working_hours = models.FloatField(null=True, blank=True)
#     active_hours = models.FloatField(null=True, blank=True)
#     inactive_hours = models.FloatField(null=True, blank=True)
#     total_planned_hrs = models.FloatField(null=True, blank=True)
#     class_id = models.IntegerField(null=True, blank=True)
#     time_stamp = models.BigIntegerField(null=True, blank=True)  # for timestamp
#     x1 = models.IntegerField(null=True, blank=True)
#     y1 = models.IntegerField(null=True, blank=True)
#     w = models.IntegerField(null=True, blank=True)  # Width
#     h = models.IntegerField(null=True, blank=True)  # Height
#     cx = models.IntegerField(null=True, blank=True)  # X-center coordinate
#     cy = models.IntegerField(null=True, blank=True)  # Y-center coordinate
#     eucl = models.FloatField(null=True, blank=True)  # Euclidean distance
#     confidence_score = models.FloatField(null=True, blank=True)
#     duplicate = models.BooleanField(default=False, null=True, blank=True)
#     track_id = models.IntegerField(null=True, blank=True)
#     group_event = models.BooleanField(default=False, null=True, blank=True)

#     def convert_interval_to_seconds(self):
#         """Convert a timedelta object to seconds before saving."""
#         if isinstance(self.processing_time, timedelta):
#             return self.processing_time.total_seconds()  # ✅ Convert interval to float
#         return None  # ✅ Handle NULL values safely

#     def save(self, *args, **kwargs):
#         """Override save method to ensure interval conversion."""
#         self.processing_time = self.convert_interval_to_seconds()
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.activity} - {self.milestone}"


from django.db import models

class lt_july_01_final_data_12_hours(models.Model):
    activity = models.CharField(max_length=255, null=True, blank=True)
    milestone = models.CharField(max_length=255, null=True, blank=True)
    class_id = models.IntegerField(null=True, blank=True)
    object_name = models.CharField(max_length=255, null=True, blank=True)
    channel = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)  # ✅ Matches `time with time zone`
    time_stamp = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)  # ✅ Matches `numeric`
    file_name = models.CharField(max_length=255, null=True, blank=True)
    box_coordinates = models.TextField(null=True, blank=True)  # ✅ Matches `character varying`
    processing_time = models.CharField(max_length=255, null=True, blank=True)  # ✅ Handle as a string (needs conversion)
    x1 = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    y1 = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    w = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    h = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    cx = models.IntegerField(null=True, blank=True)
    cy = models.IntegerField(null=True, blank=True)
    eucl = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    confidence_score = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    idle = models.CharField(max_length=255, null=True, blank=True)
    group_talking = models.CharField(max_length=255, null=True, blank=True)
    no_helmet = models.CharField(max_length=255, null=True, blank=True)
    idle_count = models.IntegerField(null=True, blank=True)
    group_count = models.IntegerField(null=True, blank=True)
    no_helmet_count = models.IntegerField(null=True, blank=True)
    no_vest_count = models.IntegerField(null=True, blank=True)
    no_vest = models.CharField(max_length=255, null=True, blank=True)
    duplicate = models.BooleanField(default=False, null=True, blank=True)
    track_id = models.IntegerField(null=True, blank=True)
    group_event = models.CharField(max_length=255, null=True, blank=True)
    # img = models.ImageField(upload_to='media/', blank=True, null=True)

    class Meta:
        db_table = "app_lt_july_01_final_data_12_hours"  # ✅ Ensure it maps to your existing PostgreSQL table

    def __str__(self):
        return f"{self.activity} - {self.milestone}"
        
