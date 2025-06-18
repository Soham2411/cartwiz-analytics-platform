# analytics/search_views.py - NEW FILE
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Sum, Count, Avg
from django.db.models.functions import TruncMonth
from sales.models import SalesTransaction
from stores.models import Store
from customers.models import Customer
from products.models import Product
from datetime import datetime, timedelta

class UniversalSearchView(APIView):
    """Universal search across products, customers, and stores"""
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query or len(query) < 2:
            return Response({
                'error': 'Search query must be at least 2 characters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Search products
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(category__icontains=query) | 
            Q(brand__icontains=query) |
            Q(sku__icontains=query)
        )[:10]
        
        # Search stores  
        stores = Store.objects.filter(
            Q(store_name__icontains=query) |
            Q(city__icontains=query) |
            Q(state__icontains=query) |
            Q(store_type__icontains=query)
        )[:10]
        
        # Search customers (limited for privacy)
        customers = Customer.objects.filter(
            Q(loyalty_tier__icontains=query) |
            Q(preferred_channel__icontains=query)
        )[:10]
        
        # Format results
        results = {
            'query': query,
            'products': [{
                'id': p.product_id,
                'name': p.name,
                'category': p.category,
                'brand': p.brand,
                'price': float(p.msrp),
                'type': 'product'
            } for p in products],
            'stores': [{
                'id': s.store_id,
                'name': s.store_name,
                'city': s.city,
                'state': s.state,
                'type': s.store_type,
                'type': 'store'
            } for s in stores],
            'customers': [{
                'id': c.customer_id,
                'tier': c.loyalty_tier,
                'channel': c.preferred_channel,
                'type': 'customer'
            } for c in customers],
            'total_results': len(products) + len(stores) + len(customers)
        }
        
        return Response(results, status=status.HTTP_200_OK)

class ProductDetailView(APIView):
    """Detailed product analysis"""
    
    def get(self, request, product_id):
        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get product sales analytics
        sales_data = SalesTransaction.objects.filter(product_id=product_id).aggregate(
            total_revenue=Sum('total_amount'),
            units_sold=Sum('quantity'),
            total_transactions=Count('transaction_id'),
            avg_price=Avg('final_price'),
            avg_discount=Avg('discount_percent')
        )
        
        # Monthly sales trend
        monthly_sales = SalesTransaction.objects.filter(
            product_id=product_id
        ).annotate(
            month=TruncMonth('transaction_date')
        ).values('month').annotate(
            revenue=Sum('total_amount'),
            units=Sum('quantity')
        ).order_by('month')
        
        # Top performing stores for this product
        top_stores = SalesTransaction.objects.filter(
            product_id=product_id
        ).values(
            'store__store_name', 'store__city', 'store__state'
        ).annotate(
            revenue=Sum('total_amount'),
            units=Sum('quantity')
        ).order_by('-revenue')[:5]
        
        # Customer segments buying this product
        customer_segments = SalesTransaction.objects.filter(
            product_id=product_id
        ).values('customer__loyalty_tier').annotate(
            customers=Count('customer', distinct=True),
            revenue=Sum('total_amount')
        ).order_by('-revenue')
        
        result = {
            'product': {
                'id': product.product_id,
                'name': product.name,
                'category': product.category,
                'subcategory': product.subcategory,
                'brand': product.brand,
                'msrp': float(product.msrp),
                'cost': float(product.cost),
                'margin': float((product.msrp - product.cost) / product.msrp * 100),
                'launch_date': product.launch_date,
                'seasonal': product.seasonal_flag,
                'abc_class': product.abc_classification
            },
            'performance': sales_data,
            'monthly_trends': list(monthly_sales),
            'top_stores': list(top_stores),
            'customer_segments': list(customer_segments)
        }
        
        return Response(result, status=status.HTTP_200_OK)

class StoreDetailView(APIView):
    """Detailed store analysis"""
    
    def get(self, request, store_id):
        try:
            store = Store.objects.get(store_id=store_id)
        except Store.DoesNotExist:
            return Response({'error': 'Store not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Store performance metrics
        store_metrics = SalesTransaction.objects.filter(store_id=store_id).aggregate(
            total_revenue=Sum('total_amount'),
            total_transactions=Count('transaction_id'),
            unique_customers=Count('customer', distinct=True),
            avg_transaction=Avg('total_amount'),
            unique_products=Count('product', distinct=True)
        )
        
        # Monthly performance
        monthly_performance = SalesTransaction.objects.filter(
            store_id=store_id
        ).annotate(
            month=TruncMonth('transaction_date')
        ).values('month').annotate(
            revenue=Sum('total_amount'),
            transactions=Count('transaction_id'),
            customers=Count('customer', distinct=True)
        ).order_by('month')
        
        # Top products at this store
        top_products = SalesTransaction.objects.filter(
            store_id=store_id
        ).values(
            'product__name', 'product__category'
        ).annotate(
            revenue=Sum('total_amount'),
            units=Sum('quantity')
        ).order_by('-revenue')[:10]
        
        # Customer loyalty breakdown
        loyalty_breakdown = SalesTransaction.objects.filter(
            store_id=store_id
        ).values('customer__loyalty_tier').annotate(
            customers=Count('customer', distinct=True),
            revenue=Sum('total_amount'),
            avg_spend=Avg('total_amount')
        ).order_by('-revenue')
        
        result = {
            'store': {
                'id': store.store_id,
                'name': store.store_name,
                'address': store.address,
                'city': store.city,
                'state': store.state,
                'zip_code': store.zip_code,
                'type': store.store_type,
                'square_footage': store.square_footage,
                'opening_date': store.opening_date,
                'manager': store.manager_name,
                'region': store.region,
                'district': store.district
            },
            'performance': store_metrics,
            'monthly_trends': list(monthly_performance),
            'top_products': list(top_products),
            'customer_loyalty': list(loyalty_breakdown)
        }
        
        return Response(result, status=status.HTTP_200_OK)

class CustomerDetailView(APIView):
    """Detailed customer analysis"""
    
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Customer purchase behavior
        purchase_behavior = SalesTransaction.objects.filter(customer_id=customer_id).aggregate(
            total_spent=Sum('total_amount'),
            total_transactions=Count('transaction_id'),
            avg_order_value=Avg('total_amount'),
            unique_products=Count('product', distinct=True),
            unique_stores=Count('store', distinct=True),
            total_units=Sum('quantity')
        )
        
        # Purchase history by month
        monthly_purchases = SalesTransaction.objects.filter(
            customer_id=customer_id
        ).annotate(
            month=TruncMonth('transaction_date')
        ).values('month').annotate(
            spent=Sum('total_amount'),
            transactions=Count('transaction_id')
        ).order_by('month')
        
        # Favorite categories
        favorite_categories = SalesTransaction.objects.filter(
            customer_id=customer_id
        ).values('product__category').annotate(
            spent=Sum('total_amount'),
            transactions=Count('transaction_id'),
            units=Sum('quantity')
        ).order_by('-spent')[:5]
        
        # Favorite stores
        favorite_stores = SalesTransaction.objects.filter(
            customer_id=customer_id
        ).values(
            'store__store_name', 'store__city', 'store__state'
        ).annotate(
            visits=Count('transaction_id'),
            spent=Sum('total_amount')
        ).order_by('-spent')[:5]
        
        # Recent transactions
        recent_transactions = SalesTransaction.objects.filter(
            customer_id=customer_id
        ).select_related('product', 'store').order_by('-transaction_date')[:10]
        
        recent_list = [{
            'date': t.transaction_date,
            'product': t.product.name,
            'store': t.store.store_name,
            'amount': float(t.total_amount),
            'quantity': t.quantity
        } for t in recent_transactions]
        
        result = {
            'customer': {
                'id': customer.customer_id,
                'tier': customer.loyalty_tier,
                'age_range': customer.age_range,
                'gender': customer.gender,
                'zip_code': customer.zip_code,
                'join_date': customer.join_date,
                'last_purchase': customer.last_purchase_date,
                'preferred_channel': customer.preferred_channel,
                'lifetime_value': float(customer.total_lifetime_value)
            },
            'behavior': purchase_behavior,
            'monthly_activity': list(monthly_purchases),
            'favorite_categories': list(favorite_categories),
            'favorite_stores': list(favorite_stores),
            'recent_transactions': recent_list
        }
        
        return Response(result, status=status.HTTP_200_OK)

class TrendingProductsView(APIView):
    """Get trending products based on recent sales velocity"""
    
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        limit = int(request.query_params.get('limit', 10))
        
        # Simple approach: Get recent top performers
        recent_date = datetime.now() - timedelta(days=days)
        
        # Debug: Check if we have any recent data
        total_recent_transactions = SalesTransaction.objects.filter(
            transaction_date__gte=recent_date
        ).count()
        
        print(f"DEBUG: Found {total_recent_transactions} transactions in last {days} days")
        
        if total_recent_transactions == 0:
            # If no recent data, get overall top products
            trending = SalesTransaction.objects.values(
                'product__name', 'product__category', 'product__brand'
            ).annotate(
                recent_revenue=Sum('total_amount'),
                recent_units=Sum('quantity'),
                recent_transactions=Count('transaction_id'),
                growth_score=Sum('total_amount') / Count('transaction_id')
            ).order_by('-recent_revenue')[:limit]
        else:
            # Get recent top performers
            trending = SalesTransaction.objects.filter(
                transaction_date__gte=recent_date
            ).values(
                'product__name', 'product__category', 'product__brand'
            ).annotate(
                recent_revenue=Sum('total_amount'),
                recent_units=Sum('quantity'),
                recent_transactions=Count('transaction_id'),
                growth_score=Sum('total_amount') / Count('transaction_id')
            ).order_by('-recent_revenue')[:limit]
        
        # Convert to list and ensure we have data
        trending_list = list(trending)
        
        print(f"DEBUG: Found {len(trending_list)} trending products")
        if trending_list:
            print(f"DEBUG: First product: {trending_list[0]}")
        
        return Response({
            'period_days': days,
            'total_recent_transactions': total_recent_transactions,
            'trending_products': trending_list
        }, status=status.HTTP_200_OK)
    
class CompetitiveAnalysisView(APIView):
    """Analyze competitive positioning by category"""
    
    def get(self, request):
        from django.db.models import DecimalField, FloatField, F, Case, When
        
        category = request.query_params.get('category', 'Electronics')
        
        # First get total category revenue
        category_total = SalesTransaction.objects.filter(
            product__category=category
        ).aggregate(total=Sum('total_amount'))['total'] or 1
        
        # Brand performance in category
        brand_performance = SalesTransaction.objects.filter(
            product__category=category
        ).values('product__brand').annotate(
            revenue=Sum('total_amount'),
            units=Sum('quantity'),
            avg_price=Avg('final_price'),
            # Fixed market share calculation with output_field
            market_share=Case(
                When(revenue__gt=0, then=F('revenue') * 100.0 / category_total),
                default=0,
                output_field=FloatField()
            )
        ).order_by('-revenue')
        
        # Price positioning
        price_tiers = SalesTransaction.objects.filter(
            product__category=category
        ).values('product__name', 'product__brand').annotate(
            avg_price=Avg('final_price'),
            revenue=Sum('total_amount'),
            units=Sum('quantity')
        ).order_by('-avg_price')[:20]
        
        return Response({
            'category': category,
            'brand_performance': list(brand_performance),
            'price_positioning': list(price_tiers)
        }, status=status.HTTP_200_OK)