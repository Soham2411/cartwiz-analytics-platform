from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .ml_models import CartWizMLEngine
from datetime import datetime
from django.http import HttpResponse
from .pdf_generator import CartWizReportGenerator

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
    
class GenerateReportView(APIView):
    """Generate and download PDF report"""
    
    def get(self, request):
        try:
            # Generate PDF report
            report_generator = CartWizReportGenerator()
            pdf_data = report_generator.generate_executive_summary()
            
            # Create HTTP response with PDF
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="CartWiz_Executive_Report_{datetime.now().strftime("%Y%m%d")}.pdf"'
            
            return response
            
        except Exception as e:
            return Response({
                'error': 'Failed to generate report',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)