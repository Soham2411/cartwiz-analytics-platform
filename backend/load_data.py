"""
CartWiz: Enterprise Data Loader
Efficiently loads 10M+ records from CSV files into PostgreSQL
"""

import os
import sys
import django
import pandas as pd
from datetime import datetime
import numpy as np

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cartwiz_backend.settings')
django.setup()

from stores.models import Store
from products.models import Product
from customers.models import Customer
from sales.models import SalesTransaction
from django.db import transaction
from django.utils.dateparse import parse_date

class CartWizDataLoader:
    def __init__(self, data_directory='../data'):
        self.data_dir = data_directory
        self.batch_size = 1000  # Process records in batches for memory efficiency
        
    def load_stores(self):
        """Load store data from CSV"""
        print("Loading stores data...")
        
        # Clear existing data
        Store.objects.all().delete()
        
        # Read CSV
        df = pd.read_csv(f'{self.data_dir}/stores.csv')
        
        stores_to_create = []
        for _, row in df.iterrows():
            store = Store(
                store_id=row['store_id'],
                store_name=row['store_name'],
                address=row['address'],
                city=row['city'],
                state=row['state'],
                zip_code=row['zip_code'],
                store_type=row['store_type'],
                square_footage=row['square_footage'],
                opening_date=parse_date(str(row['opening_date'])),
                manager_name=row['manager_name'],
                region=row['region'],
                district=row['district']
            )
            stores_to_create.append(store)
        
        # Bulk create for efficiency
        Store.objects.bulk_create(stores_to_create)
        print(f"✓ Loaded {len(stores_to_create)} stores")
        
    def load_products(self):
        """Load product data from CSV"""
        print("Loading products data...")
        
        # Clear existing data
        Product.objects.all().delete()
        
        # Read CSV
        df = pd.read_csv(f'{self.data_dir}/products.csv')
        
        products_to_create = []
        for _, row in df.iterrows():
            product = Product(
                product_id=row['product_id'],
                sku=row['sku'],
                name=row['name'],
                brand=row['brand'],
                category=row['category'],
                subcategory=row['subcategory'],
                cost=row['cost'],
                msrp=row['msrp'],
                launch_date=parse_date(str(row['launch_date'])),
                seasonal_flag=row['seasonal_flag'],
                abc_classification=row['abc_classification']
            )
            products_to_create.append(product)
        
        # Bulk create for efficiency
        Product.objects.bulk_create(products_to_create)
        print(f"✓ Loaded {len(products_to_create)} products")
        
    def load_customers(self):
        """Load customer data from CSV"""
        print("Loading customers data...")
        
        # Clear existing data
        Customer.objects.all().delete()
        
        # Read CSV
        df = pd.read_csv(f'{self.data_dir}/customers.csv')
        
        customers_to_create = []
        for _, row in df.iterrows():
            customer = Customer(
                customer_id=row['customer_id'],
                email_hash=row['email_hash'],
                age_range=row['age_range'],
                gender=row['gender'],
                zip_code=row['zip_code'],
                loyalty_tier=row['loyalty_tier'],
                join_date=parse_date(str(row['join_date'])),
                last_purchase_date=parse_date(str(row['last_purchase_date'])),
                preferred_channel=row['preferred_channel'],
                total_lifetime_value=row['total_lifetime_value']
            )
            customers_to_create.append(customer)
        
        # Bulk create for efficiency
        Customer.objects.bulk_create(customers_to_create)
        print(f"✓ Loaded {len(customers_to_create)} customers")
        
    def load_sales_transactions(self):
        """Load sales transaction data from CSV - optimized for 10M+ records"""
        print("Loading sales transactions (this will take several minutes)...")
        
        # Clear existing data
        SalesTransaction.objects.all().delete()
        
        # Read CSV in chunks to manage memory
        chunk_size = self.batch_size
        total_loaded = 0
        
        # Use chunked reading for large files
        csv_file = f'{self.data_dir}/sales.csv'
        
        print(f"Processing {csv_file} in chunks of {chunk_size}...")
        
        for chunk_num, df_chunk in enumerate(pd.read_csv(csv_file, chunksize=chunk_size)):
            transactions_to_create = []
            
            for _, row in df_chunk.iterrows():
                try:
                    # Get foreign key objects
                    store = Store.objects.get(store_id=row['store_id'])
                    customer = Customer.objects.get(customer_id=row['customer_id'])
                    product = Product.objects.get(product_id=row['product_id'])
                    
                    transaction_obj = SalesTransaction(
                        transaction_id=row['transaction_id'],
                        store=store,
                        customer=customer,
                        product=product,
                        transaction_date=parse_date(str(row['transaction_date'])),
                        quantity=row['quantity'],
                        unit_price=row['unit_price'],
                        discount_percent=row.get('discount_percent', 0),
                        discount_amount=row['discount_amount'],
                        final_price=row['final_price'],
                        total_amount=row['total_amount'],
                        payment_method=row['payment_method'],
                        return_flag=row['return_flag'],
                        season=row.get('season', 'Regular')
                    )
                    transactions_to_create.append(transaction_obj)
                    
                except (Store.DoesNotExist, Customer.DoesNotExist, Product.DoesNotExist) as e:
                    print(f"Warning: Skipping transaction {row['transaction_id']} - {e}")
                    continue
            
            # Bulk create this chunk
            if transactions_to_create:
                with transaction.atomic():
                    SalesTransaction.objects.bulk_create(transactions_to_create)
                
                total_loaded += len(transactions_to_create)
                
                # Progress indicator
                if chunk_num % 10 == 0:  # Every 10 chunks
                    print(f"  Loaded {total_loaded:,} transactions...")
        
        print(f"✓ Loaded {total_loaded:,} sales transactions")
        
    def load_all_data(self):
        """Load all data in the correct order"""
        start_time = datetime.now()
        print("=== CartWiz Enterprise Data Loading ===")
        print(f"Started at: {start_time}")
        
        try:
            # Load in dependency order
            self.load_stores()
            self.load_products()
            self.load_customers()
            self.load_sales_transactions()
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            print(f"\n=== Loading Complete! ===")
            print(f"Total time: {duration}")
            print(f"Finished at: {end_time}")
            
            # Verify data loaded correctly
            self.verify_data()
            
        except Exception as e:
            print(f"Error during data loading: {e}")
            raise
    
    def verify_data(self):
        """Verify all data loaded correctly"""
        print("\n=== Data Verification ===")
        
        store_count = Store.objects.count()
        product_count = Product.objects.count()
        customer_count = Customer.objects.count()
        transaction_count = SalesTransaction.objects.count()
        
        print(f"Stores: {store_count:,}")
        print(f"Products: {product_count:,}")
        print(f"Customers: {customer_count:,}")
        print(f"Transactions: {transaction_count:,}")
        
        # Calculate total revenue
        from django.db.models import Sum
        total_revenue = SalesTransaction.objects.aggregate(
            total=Sum('total_amount')
        )['total']
        
        print(f"Total Revenue: ${total_revenue:,.2f}")
        print("\n✓ Database loaded successfully!")

if __name__ == "__main__":
    loader = CartWizDataLoader()
    loader.load_all_data()