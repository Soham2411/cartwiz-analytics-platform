import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cartwiz_backend.settings')
django.setup()

from sales.models import SalesTransaction
from django.db.models import Sum

print("=== Quick Analytics Test ===")
print(f"Total transactions: {SalesTransaction.objects.count():,}")

revenue = SalesTransaction.objects.aggregate(total=Sum('total_amount'))['total']
print(f"Total revenue: ${revenue:,.2f}")

print("Revenue by region:")
regional = SalesTransaction.objects.values('store__region').annotate(
    total=Sum('total_amount')
).order_by('-total')

for region in regional:
    print(f"  {region['store__region']}: ${region['total']:,.0f}")