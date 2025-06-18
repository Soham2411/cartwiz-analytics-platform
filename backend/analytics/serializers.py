from rest_framework import serializers

class RegionalSalesSerializer(serializers.Serializer):
    region = serializers.CharField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    store_count = serializers.IntegerField()
    avg_store_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)

class TopProductSerializer(serializers.Serializer):
    product_name = serializers.CharField()
    category = serializers.CharField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    units_sold = serializers.IntegerField()

class CustomerLoyaltySerializer(serializers.Serializer):
    loyalty_tier = serializers.CharField()
    customer_count = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    avg_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    revenue_per_customer = serializers.DecimalField(max_digits=15, decimal_places=2)

class MonthlyTrendSerializer(serializers.Serializer):
    month = serializers.DateField()
    monthly_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    transaction_count = serializers.IntegerField()
    avg_transaction = serializers.DecimalField(max_digits=10, decimal_places=2)

class TopStoreSerializer(serializers.Serializer):
    store_name = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    store_type = serializers.CharField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    transaction_count = serializers.IntegerField()

class OverviewStatsSerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_transactions = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    total_stores = serializers.IntegerField()
    avg_transaction_value = serializers.DecimalField(max_digits=10, decimal_places=2)