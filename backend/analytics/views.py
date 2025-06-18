from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Avg, F, Q
from django.db.models.functions import TruncMonth
from sales.models import SalesTransaction
from stores.models import Store
from customers.models import Customer
from .serializers import (
    RegionalSalesSerializer, TopProductSerializer, CustomerLoyaltySerializer,
    MonthlyTrendSerializer, TopStoreSerializer, OverviewStatsSerializer
)

# Add these NEW imports for ML
from .ml_models import CartWizMLEngine
from datetime import datetime


class BaseFilteredView(APIView):
    """Base class with common filtering logic"""
    
    def get_filtered_queryset(self, request):
        """Apply filters to the base queryset"""
        queryset = SalesTransaction.objects.all()
        
        # Year filter
        year = request.query_params.get('year')
        if year and year != 'all':
            queryset = queryset.filter(transaction_date__year=year)
        
        # Region filter
        region = request.query_params.get('region')
        if region and region != 'all':
            queryset = queryset.filter(store__region=region)
        
        # Category filter
        category = request.query_params.get('category')
        if category and category != 'all':
            queryset = queryset.filter(product__category=category)
        
        # Date range filter (if provided)
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(transaction_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(transaction_date__lte=end_date)
            
        return queryset

class OverviewStatsView(BaseFilteredView):
    """Get high-level overview statistics with filtering"""
    
    def get(self, request):
        queryset = self.get_filtered_queryset(request)
        
        # Calculate overview metrics from filtered data
        overview = queryset.aggregate(
            total_revenue=Sum('total_amount'),
            total_transactions=Count('transaction_id'),
            avg_transaction_value=Avg('total_amount')
        )
        
        # Count unique customers and stores in filtered data
        overview['total_customers'] = queryset.values('customer').distinct().count()
        overview['total_stores'] = queryset.values('store').distinct().count()
        
        # Handle case where no data matches filters
        if not overview['total_revenue']:
            overview = {
                'total_revenue': 0,
                'total_transactions': 0,
                'avg_transaction_value': 0,
                'total_customers': 0,
                'total_stores': 0
            }
        
        serializer = OverviewStatsSerializer(overview)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RegionalSalesView(BaseFilteredView):
    """Get sales performance by region with filtering"""
    
    def get(self, request):
        queryset = self.get_filtered_queryset(request)
        
        regional_data = queryset.values('store__region').annotate(
            total_revenue=Sum('total_amount'),
            store_count=Count('store', distinct=True),
            avg_store_revenue=Sum('total_amount') / Count('store', distinct=True)
        ).order_by('-total_revenue')
        
        # Format data for serializer
        formatted_data = []
        for item in regional_data:
            if item['total_revenue']:  # Only include regions with data
                formatted_data.append({
                    'region': item['store__region'],
                    'total_revenue': item['total_revenue'],
                    'store_count': item['store_count'],
                    'avg_store_revenue': item['avg_store_revenue']
                })
        
        serializer = RegionalSalesSerializer(formatted_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TopProductsView(BaseFilteredView):
    """Get top products by revenue with filtering"""
    
    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        queryset = self.get_filtered_queryset(request)
        
        top_products = queryset.values(
            'product__name', 'product__category'
        ).annotate(
            total_revenue=Sum('total_amount'),
            units_sold=Sum('quantity')
        ).order_by('-total_revenue')[:limit]
        
        # Format data for serializer
        formatted_data = []
        for item in top_products:
            formatted_data.append({
                'product_name': item['product__name'],
                'category': item['product__category'],
                'total_revenue': item['total_revenue'],
                'units_sold': item['units_sold']
            })
        
        serializer = TopProductSerializer(formatted_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CustomerLoyaltyView(BaseFilteredView):
    """Get customer performance by loyalty tier with filtering"""
    
    def get(self, request):
        queryset = self.get_filtered_queryset(request)
        
        loyalty_data = queryset.values('customer__loyalty_tier').annotate(
            customer_count=Count('customer', distinct=True),
            total_revenue=Sum('total_amount'),
            avg_order_value=Avg('total_amount')
        ).order_by('-total_revenue')
        
        # Format data for serializer
        formatted_data = []
        for item in loyalty_data:
            revenue_per_customer = (
                item['total_revenue'] / item['customer_count'] 
                if item['customer_count'] > 0 else 0
            )
            formatted_data.append({
                'loyalty_tier': item['customer__loyalty_tier'],
                'customer_count': item['customer_count'],
                'total_revenue': item['total_revenue'],
                'avg_order_value': item['avg_order_value'],
                'revenue_per_customer': revenue_per_customer
            })
        
        serializer = CustomerLoyaltySerializer(formatted_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MonthlyTrendsView(BaseFilteredView):
    """Get monthly revenue trends with filtering"""
    
    def get(self, request):
        year = request.query_params.get('year', '2024')
        queryset = self.get_filtered_queryset(request)
        
        # If year is specified in URL param, use it; otherwise use filter
        if year != 'all':
            queryset = queryset.filter(transaction_date__year=year)
        
        monthly_data = queryset.annotate(
            month=TruncMonth('transaction_date')
        ).values('month').annotate(
            monthly_revenue=Sum('total_amount'),
            transaction_count=Count('transaction_id'),
            avg_transaction=Avg('total_amount')
        ).order_by('month')
        
        serializer = MonthlyTrendSerializer(monthly_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TopStoresView(BaseFilteredView):
    """Get top performing stores with filtering"""
    
    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        queryset = self.get_filtered_queryset(request)
        
        top_stores = queryset.values(
            'store__store_name', 'store__city', 'store__state', 'store__store_type'
        ).annotate(
            total_revenue=Sum('total_amount'),
            transaction_count=Count('transaction_id')
        ).order_by('-total_revenue')[:limit]
        
        # Format data for serializer
        formatted_data = []
        for item in top_stores:
            formatted_data.append({
                'store_name': item['store__store_name'],
                'city': item['store__city'],
                'state': item['store__state'],
                'store_type': item['store__store_type'],
                'total_revenue': item['total_revenue'],
                'transaction_count': item['transaction_count']
            })
        
        serializer = TopStoreSerializer(formatted_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CategoryPerformanceView(BaseFilteredView):
    """Get performance by product category with filtering"""
    
    def get(self, request):
        queryset = self.get_filtered_queryset(request)
        
        category_data = queryset.values('product__category').annotate(
            total_revenue=Sum('total_amount'),
            units_sold=Sum('quantity'),
            avg_price=Avg('final_price'),
            transaction_count=Count('transaction_id')
        ).order_by('-total_revenue')
        
        return Response(category_data, status=status.HTTP_200_OK)

class SeasonalAnalysisView(BaseFilteredView):
    """New endpoint for seasonal analysis"""
    
    def get(self, request):
        queryset = self.get_filtered_queryset(request)
        
        seasonal_data = queryset.values('season').annotate(
            total_revenue=Sum('total_amount'),
            transaction_count=Count('transaction_id'),
            avg_transaction_value=Avg('total_amount')
        ).order_by('-total_revenue')
        
        return Response(seasonal_data, status=status.HTTP_200_OK)

class StoreTypeAnalysisView(BaseFilteredView):
    """New endpoint for store type analysis"""
    
    def get(self, request):
        queryset = self.get_filtered_queryset(request)
        
        store_type_data = queryset.values('store__store_type').annotate(
            total_revenue=Sum('total_amount'),
            store_count=Count('store', distinct=True),
            transaction_count=Count('transaction_id'),
            avg_revenue_per_store=Sum('total_amount') / Count('store', distinct=True)
        ).order_by('-total_revenue')
        
        return Response(store_type_data, status=status.HTTP_200_OK)

class CustomerInsightsView(BaseFilteredView):
    """Advanced customer analytics"""
    
    def get(self, request):
        queryset = self.get_filtered_queryset(request)
        
        # Customer demographics analysis
        age_analysis = queryset.values('customer__age_range').annotate(
            customer_count=Count('customer', distinct=True),
            total_revenue=Sum('total_amount'),
            avg_order_value=Avg('total_amount')
        ).order_by('-total_revenue')
        
        # Channel preference analysis  
        channel_analysis = queryset.values('customer__preferred_channel').annotate(
            customer_count=Count('customer', distinct=True),
            total_revenue=Sum('total_amount'),
            transaction_count=Count('transaction_id')
        ).order_by('-total_revenue')
        
        return Response({
            'age_demographics': age_analysis,
            'channel_preferences': channel_analysis
        }, status=status.HTTP_200_OK)
    
# Add this new view class at the bottom (after your existing views)
class MLPredictionsView(APIView):
    """Machine Learning predictions endpoint"""
    
    def get(self, request):
        ml_engine = CartWizMLEngine()
        
        sales_forecast = ml_engine.predict_next_quarter_sales()
        customer_clv = ml_engine.calculate_customer_lifetime_value(limit=10)
        product_demand = ml_engine.predict_product_demand(limit=5)
        business_insights = ml_engine.generate_business_insights()
        
        return Response({
            'sales_forecast': sales_forecast,
            'customer_lifetime_value': customer_clv,
            'product_demand_forecast': product_demand,
            'business_insights': business_insights,
            'generated_at': datetime.now().isoformat()
        }, status=status.HTTP_200_OK)