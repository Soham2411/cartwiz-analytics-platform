from django.urls import path
from . import views
from . import ml_views
from . import search_views

urlpatterns = [
    path('overview/', views.OverviewStatsView.as_view(), name='overview-stats'),
    path('regional-sales/', views.RegionalSalesView.as_view(), name='regional-sales'),
    path('top-products/', views.TopProductsView.as_view(), name='top-products'),
    path('customer-loyalty/', views.CustomerLoyaltyView.as_view(), name='customer-loyalty'),
    path('monthly-trends/', views.MonthlyTrendsView.as_view(), name='monthly-trends'),
    path('top-stores/', views.TopStoresView.as_view(), name='top-stores'),
    path('category-performance/', views.CategoryPerformanceView.as_view(), name='category-performance'),
    
    # New advanced endpoints
    path('seasonal-analysis/', views.SeasonalAnalysisView.as_view(), name='seasonal-analysis'),
    path('store-type-analysis/', views.StoreTypeAnalysisView.as_view(), name='store-type-analysis'),
    path('customer-insights/', views.CustomerInsightsView.as_view(), name='customer-insights'),
    path('ml-predictions/', views.MLPredictionsView.as_view(), name='ml-predictions'),
    path('ml-predictions/', ml_views.MLPredictionsView.as_view(), name='ml-predictions'),
    path('generate-report/', ml_views.GenerateReportView.as_view(), name='generate-report'),
    path('search/', search_views.UniversalSearchView.as_view(), name='universal-search'),
    path('product/<str:product_id>/', search_views.ProductDetailView.as_view(), name='product-detail'),
    path('store/<str:store_id>/', search_views.StoreDetailView.as_view(), name='store-detail'),
    path('customer/<str:customer_id>/', search_views.CustomerDetailView.as_view(), name='customer-detail'),
    path('trending/', search_views.TrendingProductsView.as_view(), name='trending-products'),
    path('competitive/', search_views.CompetitiveAnalysisView.as_view(), name='competitive-analysis'),
]
