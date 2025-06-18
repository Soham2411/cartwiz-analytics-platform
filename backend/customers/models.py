from django.db import models

class Customer(models.Model):
    customer_id = models.CharField(max_length=15, primary_key=True)
    email_hash = models.CharField(max_length=64)
    age_range = models.CharField(max_length=10)
    gender = models.CharField(max_length=10)
    zip_code = models.CharField(max_length=10)
    loyalty_tier = models.CharField(max_length=20)
    join_date = models.DateField()
    last_purchase_date = models.DateField()
    preferred_channel = models.CharField(max_length=20)
    total_lifetime_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'customers'
        indexes = [
            models.Index(fields=['loyalty_tier']),
            models.Index(fields=['age_range']),
            models.Index(fields=['zip_code']),
        ]
    
    def __str__(self):
        return f"Customer {self.customer_id} ({self.loyalty_tier})"
