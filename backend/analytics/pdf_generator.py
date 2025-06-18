# analytics/pdf_generator.py - NEW FILE
# analytics/pdf_generator.py - CLEAN VERSION (No DRF imports)
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.db.models import Sum, Count, Avg
from sales.models import SalesTransaction
from stores.models import Store
from customers.models import Customer
from .ml_models import CartWizMLEngine
from datetime import datetime, timedelta
import io

class CartWizReportGenerator:
    """Generate professional PDF reports for CartWiz analytics"""
    
    def __init__(self):
        self.ml_engine = CartWizMLEngine()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.HexColor('#3498db')
        ))

    def generate_executive_summary(self):
        """Generate comprehensive executive summary PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Build PDF content
        story = []
        
        # Title Page
        story.append(Paragraph("CartWiz Analytics Platform", self.styles['CustomTitle']))
        story.append(Paragraph("Executive Summary Report", self.styles['Heading2']))
        story.append(Spacer(1, 0.5*inch))
        
        # Executive Overview
        overview_data = self._get_overview_data()
        story.append(Paragraph("Executive Overview", self.styles['SectionHeader']))
        
        # Key Metrics Table
        metrics_data = [
            ['Metric', 'Value', 'Performance'],
            ['Total Revenue', f"${overview_data['total_revenue']:,.0f}", 'Strong'],
            ['Total Transactions', f"{overview_data['total_transactions']:,}", 'Enterprise Scale'],
            ['Active Customers', f"{overview_data['total_customers']:,}", 'Engaged Base'],
            ['Average Transaction', f"${overview_data['avg_transaction_value']:.2f}", 'Healthy AOV'],
            ['Store Network', f"{overview_data['total_stores']} locations", 'Nationwide']
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Regional Performance
        story.append(Paragraph("Regional Performance Analysis", self.styles['SectionHeader']))
        regional_data = self._get_regional_data()
        
        regional_table_data = [['Region', 'Revenue', 'Stores', 'Revenue per Store']]
        for region in regional_data:
            regional_table_data.append([
                region['store__region'],
                f"${region['total_revenue']:,.0f}",
                str(region['store_count']),
                f"${region['avg_store_revenue']:,.0f}"
            ])
        
        regional_table = Table(regional_table_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1.5*inch])
        regional_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(regional_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ML Predictions Section
        story.append(Paragraph("AI-Powered Predictions", self.styles['SectionHeader']))
        
        # Sales Forecast
        sales_forecast = self.ml_engine.predict_next_quarter_sales()
        story.append(Paragraph("Sales Forecast (Next 3 Months):", self.styles['Normal']))
        
        forecast_data = [['Month', 'Predicted Revenue', 'Confidence']]
        for forecast in sales_forecast:
            forecast_data.append([
                forecast['month'],
                f"${forecast['predicted_revenue']:,.0f}",
                f"{forecast['confidence']}%"
            ])
        
        forecast_table = Table(forecast_data, colWidths=[1.5*inch, 2*inch, 1.5*inch])
        forecast_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(forecast_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>"
            f"Data Source: CartWiz Analytics Platform<br/>"
            f"Coverage: 10,000,000+ transactions across 500 stores nationwide",
            self.styles['Normal']
        ))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    def _get_overview_data(self):
        """Get overview statistics"""
        return SalesTransaction.objects.aggregate(
            total_revenue=Sum('total_amount'),
            total_transactions=Count('transaction_id'),
            avg_transaction_value=Avg('total_amount'),
            total_customers=Count('customer', distinct=True),
            total_stores=Count('store', distinct=True)
        )
    
    def _get_regional_data(self):
        """Get regional performance data"""
        return SalesTransaction.objects.values('store__region').annotate(
            total_revenue=Sum('total_amount'),
            store_count=Count('store', distinct=True),
            avg_store_revenue=Sum('total_amount') / Count('store', distinct=True)
        ).order_by('-total_revenue')