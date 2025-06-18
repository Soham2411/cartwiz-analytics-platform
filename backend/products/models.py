from django.db import models

class Product(models.Model):
    product_id = models.CharField(max_length=15, primary_key=True)
    sku = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    subcategory = models.CharField(max_length=50)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    msrp = models.DecimalField(max_digits=10, decimal_places=2)
    launch_date = models.DateField()
    seasonal_flag = models.BooleanField(default=False)
    abc_classification = models.CharField(max_length=1)
    
    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
            models.Index(fields=['abc_classification']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.product_id})"
