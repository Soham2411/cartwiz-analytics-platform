from django.db import models
from django.db.models import Sum, Count, Avg
from sales.models import SalesTransaction

class AnalyticsManager:
    """Custom manager for analytics queries"""
    
    @staticmethod
    def get_sales_by_region():
        """Get total sales by region"""
        return SalesTransaction.objects.values(
            'store__region'
        ).annotate(
            total_sales=Sum('total_amount'),
            transaction_count=Count('transaction_id'),
            avg_transaction=Avg('total_amount')
        ).order_by('-total_sales')
    
    @staticmethod
    def get_top_products(limit=10):
        """Get top products by revenue"""
        return SalesTransaction.objects.values(
            'product__name',
            'product__category'
        ).annotate(
            total_revenue=Sum('total_amount'),
            units_sold=Sum('quantity')
        ).order_by('-total_revenue')[:limit]
    
    @staticmethod
    def get_customer_metrics():
        """Get customer tier performance"""
        return SalesTransaction.objects.values(
            'customer__loyalty_tier'
        ).annotate(
            total_customers=Count('customer', distinct=True),
            total_revenue=Sum('total_amount'),
            avg_order_value=Avg('total_amount')
        ).order_by('-total_revenue')
    
    @staticmethod
    def get_monthly_trends():
        """Get monthly sales trends"""
        from django.db.models.functions import TruncMonth
        return SalesTransaction.objects.annotate(
            month=TruncMonth('transaction_date')
        ).values('month').annotate(
            monthly_sales=Sum('total_amount'),
            transaction_count=Count('transaction_id')
        ).order_by('month')