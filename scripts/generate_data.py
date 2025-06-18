"""
CartWiz: Medium Scale Data Generator
Generates 5 million transactions - perfect balance of realism and speed
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import json

# Initialize Faker for realistic data
fake = Faker('en_US')
Faker.seed(42)
np.random.seed(42)
random.seed(42)

class CartWizMediumGenerator:
    def __init__(self):
        self.states = [
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        ]
        
        self.store_types = ['Urban Flagship', 'Suburban Standard', 'Rural Compact', 'Outlet Center']
        self.product_categories = ['Electronics', 'Apparel', 'Home & Garden', 'Groceries', 'Sports & Outdoors']
        self.brands = ['CartWiz Brand', 'Premium Choice', 'Value Select', 'National Brand A', 'National Brand B']
        
    def generate_stores(self, num_stores=500):
        """Generate 500 stores across all 50 US states"""
        print(f"Generating {num_stores} stores across all 50 US states...")
        stores = []
        
        for store_id in range(1, num_stores + 1):
            state = random.choice(self.states)
            city = fake.city()
            store_type = random.choice(self.store_types)
            
            # Assign realistic square footage based on store type
            sq_ft_ranges = {
                'Urban Flagship': (15000, 25000),
                'Suburban Standard': (8000, 15000),
                'Rural Compact': (3000, 8000),
                'Outlet Center': (5000, 12000)
            }
            square_footage = random.randint(*sq_ft_ranges[store_type])
            
            stores.append({
                'store_id': f'ST{store_id:04d}',
                'store_name': f'CartWiz {city}',
                'address': fake.street_address(),
                'city': city,
                'state': state,
                'zip_code': fake.zipcode(),
                'store_type': store_type,
                'square_footage': square_footage,
                'opening_date': fake.date_between(start_date='-10y', end_date='-1y'),
                'manager_name': fake.name(),
                'region': self._assign_region(state),
                'district': f'D{random.randint(1, 50):02d}'
            })
            
        return pd.DataFrame(stores)
    
    def generate_products(self, num_products=10000):
        """Generate 10K products - good variety without being overwhelming"""
        print(f"Generating {num_products} products across 5 major categories...")
        products = []
        
        for product_id in range(1, num_products + 1):
            category = random.choice(self.product_categories)
            subcategory = self._get_subcategory(category)
            brand = random.choice(self.brands)
            
            # Generate realistic pricing based on category
            cost, msrp = self._generate_pricing(category)
            
            products.append({
                'product_id': f'PRD{product_id:06d}',
                'sku': f'{category[:3].upper()}{product_id:06d}',
                'name': self._generate_product_name(category, brand),
                'brand': brand,
                'category': category,
                'subcategory': subcategory,
                'cost': round(cost, 2),
                'msrp': round(msrp, 2),
                'launch_date': fake.date_between(start_date='-5y', end_date='today'),
                'seasonal_flag': random.choice([True, False]),
                'abc_classification': random.choices(['A', 'B', 'C'], weights=[20, 30, 50])[0]
            })
            
            if product_id % 1000 == 0:
                print(f"  Generated {product_id:,} products...")
                
        return pd.DataFrame(products)
    
    def generate_customers(self, num_customers=50000):
        """Generate 50K customers - represents active loyalty member base"""
        print(f"Generating {num_customers} loyalty customers...")
        customers = []
        
        for customer_id in range(1, num_customers + 1):
            join_date = fake.date_between(start_date='-8y', end_date='-30d')
            last_purchase = fake.date_between(start_date=join_date, end_date='today')
            
            customers.append({
                'customer_id': f'CUST{customer_id:08d}',
                'email_hash': fake.sha256(),
                'age_range': random.choices(['18-25', '26-35', '36-45', '46-55', '56-65', '65+'], 
                                          weights=[15, 25, 20, 20, 15, 5])[0],
                'gender': random.choice(['M', 'F', 'Other']),
                'zip_code': fake.zipcode(),
                'loyalty_tier': random.choices(['Bronze', 'Silver', 'Gold', 'Platinum'], 
                                             weights=[40, 30, 20, 10])[0],
                'join_date': join_date,
                'last_purchase_date': last_purchase,
                'preferred_channel': random.choice(['In-Store', 'Online', 'Mobile App']),
                'total_lifetime_value': round(random.uniform(50, 5000), 2)
            })
            
            if customer_id % 5000 == 0:
                print(f"  Generated {customer_id:,} customers...")
                
        return pd.DataFrame(customers)
    
    def generate_sales_transactions(self, stores_df, products_df, customers_df, num_transactions=10000000):
        """Generate 10 million sales transactions - serious enterprise scale"""
        print(f"Generating {num_transactions:,} sales transactions...")
        print("This will take about 30-40 minutes...")
        
        transactions = []
        
        # Pre-sample data for efficiency
        store_ids = stores_df['store_id'].tolist()
        customer_ids = customers_df['customer_id'].tolist()
        product_data = products_df[['product_id', 'msrp', 'category']].to_dict('records')
        
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 12, 31)
        total_days = (end_date - start_date).days
        
        # Payment methods with realistic distribution
        payment_methods = ['Credit Card', 'Debit Card', 'Cash', 'Digital Wallet']
        payment_weights = [45, 30, 15, 10]
        
        for txn_id in range(1, num_transactions + 1):
            # Generate realistic seasonal patterns
            random_days = random.randint(0, total_days)
            transaction_date = start_date + timedelta(days=random_days)
            
            # Add some seasonality (higher sales in Nov-Dec)
            month = transaction_date.month
            if month in [11, 12]:  # Holiday season
                seasonal_multiplier = 1.3
            elif month in [6, 7, 8]:  # Summer
                seasonal_multiplier = 1.1
            else:
                seasonal_multiplier = 1.0
            
            # Select random store, customer, product
            store_id = random.choice(store_ids)
            customer_id = random.choice(customer_ids)
            product = random.choice(product_data)
            
            # Generate realistic quantity based on category
            if product['category'] == 'Groceries':
                quantity = random.choices([1, 2, 3, 4, 5, 6], weights=[30, 25, 20, 15, 7, 3])[0]
            else:
                quantity = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
            
            # Calculate pricing with realistic discounts
            unit_price = product['msrp']
            
            # More discounts during holiday season
            if month in [11, 12]:
                discount_percent = random.choices([0, 10, 15, 20, 25, 30], 
                                                weights=[30, 20, 20, 15, 10, 5])[0]
            else:
                discount_percent = random.choices([0, 5, 10, 15, 20], 
                                                weights=[65, 15, 10, 7, 3])[0]
            
            discount_amount = round(unit_price * (discount_percent / 100), 2)
            final_price = unit_price - discount_amount
            total_amount = round(final_price * quantity, 2)
            
            # Realistic return probability (higher for some categories)
            return_prob = 0.08 if product['category'] == 'Apparel' else 0.03
            return_flag = random.random() < return_prob
            
            transactions.append({
                'transaction_id': f'TXN{txn_id:08d}',
                'store_id': store_id,
                'customer_id': customer_id,
                'product_id': product['product_id'],
                'transaction_date': transaction_date.date(),
                'quantity': quantity,
                'unit_price': unit_price,
                'discount_percent': discount_percent,
                'discount_amount': discount_amount,
                'final_price': final_price,
                'total_amount': total_amount,
                'payment_method': random.choices(payment_methods, weights=payment_weights)[0],
                'return_flag': return_flag,
                'season': 'Holiday' if month in [11, 12] else 'Summer' if month in [6, 7, 8] else 'Regular'
            })
            
            # Progress indicator every 500K transactions
            if txn_id % 500000 == 0:
                progress = (txn_id / num_transactions) * 100
                print(f"  Generated {txn_id:,} transactions ({progress:.1f}% complete)...")
                
        return pd.DataFrame(transactions)
    
    def _assign_region(self, state):
        """Assign geographic regions"""
        regions = {
            'Northeast': ['CT', 'ME', 'MA', 'NH', 'RI', 'VT', 'NJ', 'NY', 'PA'],
            'Southeast': ['DE', 'FL', 'GA', 'MD', 'NC', 'SC', 'VA', 'WV', 'KY', 'TN', 'AL', 'MS', 'AR', 'LA'],
            'Midwest': ['IL', 'IN', 'MI', 'OH', 'WI', 'IA', 'KS', 'MN', 'MO', 'NE', 'ND', 'SD'],
            'Southwest': ['AZ', 'NM', 'TX', 'OK'],
            'West': ['AK', 'CA', 'CO', 'HI', 'ID', 'MT', 'NV', 'OR', 'UT', 'WA', 'WY']
        }
        
        for region, states in regions.items():
            if state in states:
                return region
        return 'Other'
    
    def _get_subcategory(self, category):
        """Generate realistic subcategories"""
        subcategories = {
            'Electronics': ['Smartphones', 'Laptops', 'Audio', 'Gaming', 'Accessories'],
            'Apparel': ['Mens Clothing', 'Womens Clothing', 'Kids Clothing', 'Shoes', 'Accessories'],
            'Home & Garden': ['Furniture', 'Decor', 'Kitchen', 'Bath', 'Garden'],
            'Groceries': ['Fresh Produce', 'Packaged Foods', 'Beverages', 'Snacks', 'Health'],
            'Sports & Outdoors': ['Exercise Equipment', 'Outdoor Gear', 'Sports Apparel', 'Recreation', 'Hunting']
        }
        return random.choice(subcategories[category])
    
    def _generate_pricing(self, category):
        """Generate realistic cost and MSRP based on category"""
        price_ranges = {
            'Electronics': (50, 1500),
            'Apparel': (15, 200),
            'Home & Garden': (20, 500),
            'Groceries': (1, 50),
            'Sports & Outdoors': (25, 300)
        }
        
        msrp = random.uniform(*price_ranges[category])
        cost = msrp * random.uniform(0.4, 0.7)
        return cost, msrp
    
    def _generate_product_name(self, category, brand):
        """Generate realistic product names"""
        adjectives = ['Premium', 'Essential', 'Professional', 'Deluxe', 'Classic', 'Modern']
        
        category_items = {
            'Electronics': ['Smartphone', 'Laptop', 'Headphones', 'Speaker', 'Tablet'],
            'Apparel': ['T-Shirt', 'Jeans', 'Jacket', 'Dress', 'Sneakers'],
            'Home & Garden': ['Chair', 'Table', 'Lamp', 'Vase', 'Pillow'],
            'Groceries': ['Snacks', 'Beverage', 'Cereal', 'Sauce', 'Bread'],
            'Sports & Outdoors': ['Bike', 'Tent', 'Shoes', 'Ball', 'Equipment']
        }
        
        adjective = random.choice(adjectives)
        item = random.choice(category_items[category])
        model = random.randint(100, 999)
        
        return f"{brand} {adjective} {item} {model}"

# Usage
if __name__ == "__main__":
    generator = CartWizMediumGenerator()
    
    print("=== CartWiz Enterprise Dataset Generator ===")
    print("Creating realistic nationwide retail data...\n")
    
    # Generate enterprise-scale datasets
    stores = generator.generate_stores(500)        # 500 stores nationwide
    products = generator.generate_products(10000)   # 10K product catalog
    customers = generator.generate_customers(50000) # 50K active customers
    sales = generator.generate_sales_transactions(stores, products, customers, 10000000)  # 10M transactions
    
    # Save to CSV files
    print("\nSaving datasets to CSV files...")
    stores.to_csv('../data/stores.csv', index=False)
    products.to_csv('../data/products.csv', index=False)
    customers.to_csv('../data/customers.csv', index=False)
    sales.to_csv('../data/sales.csv', index=False)
    
    # Calculate dataset statistics
    total_revenue = sales['total_amount'].sum()
    avg_transaction = sales['total_amount'].mean()
    
    print(f"\n=== CartWiz Dataset Complete! ===")
    print(f"🏪 {len(stores):,} stores across all 50 states")
    print(f"🛍️  {len(products):,} products in 5 major categories") 
    print(f"👥 {len(customers):,} loyalty customers")
    print(f"💳 {len(sales):,} sales transactions")
    print(f"💰 ${total_revenue:,.2f} total revenue generated")
    print(f"📊 ${avg_transaction:.2f} average transaction value")
    print(f"\n📂 Files saved in ../data/ directory")
    print(f"🚀 Ready to build your enterprise analytics platform!")