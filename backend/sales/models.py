from django.db import models
from stores.models import Store
from products.models import Product
from customers.models import Customer

class SalesTransaction(models.Model):
    transaction_id = models.CharField(max_length=15, primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction_date = models.DateField()
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20)
    return_flag = models.BooleanField(default=False)
    season = models.CharField(max_length=20, default='Regular')
    
    class Meta:
        db_table = 'sales_transactions'
        indexes = [
            models.Index(fields=['transaction_date']),
            models.Index(fields=['store', 'transaction_date']),
            models.Index(fields=['customer', 'transaction_date']),
            models.Index(fields=['product', 'transaction_date']),
            models.Index(fields=['season']),
        ]
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - ${self.total_amount}"