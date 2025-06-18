from django.db import models

class Store(models.Model):
    store_id = models.CharField(max_length=10, primary_key=True)
    store_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    store_type = models.CharField(max_length=50)
    square_footage = models.IntegerField()
    opening_date = models.DateField()
    manager_name = models.CharField(max_length=100)
    region = models.CharField(max_length=20)
    district = models.CharField(max_length=10)
    
    class Meta:
        db_table = 'stores'
    
    def __str__(self):
        return f"{self.store_name} ({self.store_id})"
