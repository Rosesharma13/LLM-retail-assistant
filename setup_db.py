"""
Database setup script for ShopAI Retail Assistant
Run this once before starting the app: python setup_db.py
"""

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    print("Setting up ShopAI database...")

    # Connect to MySQL server
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "")
        )
        cursor = conn.cursor()

        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS retail_db")
        cursor.execute("USE retail_db")
        print("✅ Database 'retail_db' created")

        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(100),
                price DECIMAL(10,2),
                stock INT DEFAULT 0,
                description TEXT,
                brand VARCHAR(100),
                rating DECIMAL(3,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Products table created")

        # Create orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT,
                customer_query TEXT,
                quantity INT DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        print("✅ Orders table created")

        # Insert sample products
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]

        if count == 0:
            sample_products = [
                ("Samsung Galaxy S24", "Electronics", 79999, 15,
                 "Latest Samsung flagship smartphone with Galaxy AI features, 50MP camera, 4000mAh battery", "Samsung", 4.5),
                ("Apple iPhone 15", "Electronics", 89999, 8,
                 "Apple's latest iPhone with dynamic island, 48MP camera and A16 Bionic chip", "Apple", 4.7),
                ("Sony WH-1000XM5 Headphones", "Electronics", 29999, 20,
                 "Industry leading noise cancelling wireless headphones with 30hr battery", "Sony", 4.8),
                ("OnePlus 12", "Electronics", 64999, 22,
                 "Flagship killer with Snapdragon 8 Gen 3, 50MP Hasselblad camera", "OnePlus", 4.6),
                ("Redmi Note 13 Pro", "Electronics", 24999, 40,
                 "200MP camera, 67W fast charging, 5000mAh battery", "Redmi", 4.3),
                ("Nike Air Max 270", "Footwear", 12999, 30,
                 "Comfortable running shoes with Max Air unit for all-day cushioning", "Nike", 4.3),
                ("Adidas Ultraboost 22", "Footwear", 14999, 18,
                 "High performance running shoes with Boost cushioning technology", "Adidas", 4.6),
                ("Woodland Casual Shoes", "Footwear", 3499, 40,
                 "Premium leather casual shoes for daily office and outdoor wear", "Woodland", 4.2),
                ("Puma RS-X Sneakers", "Footwear", 8999, 25,
                 "Retro style chunky sneakers with RS cushioning system", "Puma", 4.1),
                ("Levi's 511 Slim Jeans", "Clothing", 3999, 50,
                 "Classic slim fit jeans in stretch denim fabric, available in multiple colors", "Levi's", 4.4),
                ("Allen Solly Formal Shirt", "Clothing", 1299, 60,
                 "Regular fit formal shirt for office wear, wrinkle resistant fabric", "Allen Solly", 4.1),
                ("Van Heusen Polo T-Shirt", "Clothing", 999, 80,
                 "Cotton blend polo shirt for casual and semi-formal occasions", "Van Heusen", 4.0),
                ("HP Pavilion Laptop 15", "Electronics", 54999, 12,
                 "Intel Core i5 12th Gen, 8GB RAM, 512GB SSD, Windows 11, 15.6 inch FHD display", "HP", 4.2),
                ("Dell Inspiron 15", "Electronics", 49999, 8,
                 "AMD Ryzen 5, 8GB RAM, 512GB SSD, ideal for students and professionals", "Dell", 4.3),
                ("LG 43 inch 4K TV", "Electronics", 34999, 10,
                 "43 inch 4K UHD Smart TV with WebOS, ThinQ AI, built-in Alexa", "LG", 4.4),
                ("Prestige Induction Cooktop", "Home Appliances", 2499, 25,
                 "2000W induction cooktop with feather touch panel and 8 power levels", "Prestige", 4.1),
                ("Philips Air Fryer HD9200", "Home Appliances", 6999, 20,
                 "Digital air fryer 4.1L with 7 preset cooking programs, 90% less fat", "Philips", 4.5),
                ("Crompton Ceiling Fan", "Home Appliances", 1899, 35,
                 "High speed ceiling fan with anti-dust technology and 5 star rating", "Crompton", 4.0),
                ("Boat Airdopes 141", "Electronics", 1499, 100,
                 "TWS earbuds with 42H total battery, ASAP charge, IPX4 water resistance", "Boat", 4.0),
                ("Titan Analog Watch", "Accessories", 4999, 35,
                 "Classic analog watch with genuine leather strap and sapphire crystal glass", "Titan", 4.3),
                ("Wildcraft Backpack 30L", "Accessories", 1999, 45,
                 "Durable 30L backpack with laptop compartment, ideal for college and travel", "Wildcraft", 4.2),
                ("American Tourister Trolley", "Accessories", 4499, 20,
                 "Hard shell 55cm cabin trolley with TSA lock and 360 degree spinner wheels", "American Tourister", 4.4),
            ]

            cursor.executemany("""
                INSERT INTO products (name, category, price, stock, description, brand, rating)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, sample_products)
            conn.commit()
            print(f"✅ {len(sample_products)} sample products inserted")
        else:
            print(f"ℹ️  Database already has {count} products")

        cursor.close()
        conn.close()
        print("\n🎉 Database setup complete! Run: streamlit run app.py")

    except mysql.connector.Error as e:
        print(f"❌ MySQL Error: {e}")
        print("\nMake sure MySQL is running and credentials in .env are correct")

if __name__ == "__main__":
    setup_database()
