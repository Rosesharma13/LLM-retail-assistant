import streamlit as st
import google.generativeai as genai
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime

# ── Load environment variables ─────────────────────────────────
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="ShopAI — Intelligent Retail Assistant",
    page_icon="🛍️",
    layout="wide"
)

# ── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stApp { max-width: 1200px; margin: 0 auto; }
    .chat-message-user {
        background: #007bff;
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 70%;
        float: right;
        clear: both;
    }
    .chat-message-bot {
        background: white;
        color: #333;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 70%;
        float: left;
        clear: both;
        border: 1px solid #e0e0e0;
    }
    .product-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .price-tag {
        color: #e44d26;
        font-size: 20px;
        font-weight: bold;
    }
    .in-stock { color: #28a745; font-weight: bold; }
    .out-stock { color: #dc3545; font-weight: bold; }
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a3c6e;
        text-align: center;
    }
    .header-sub {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Database connection ────────────────────────────────────────
def get_db_connection():
    """Connect to MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "retail_db")
        )
        return conn
    except Exception as e:
        return None


def init_database():
    """Initialize database with sample products."""
    conn = get_db_connection()
    if not conn:
        return False
    cursor = conn.cursor()

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
            rating DECIMAL(3,2)
        )
    """)

    # Insert sample products if table is empty
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_products = [
            ("Samsung Galaxy S24", "Electronics", 79999, 15, "Latest Samsung flagship smartphone with AI features", "Samsung", 4.5),
            ("Apple iPhone 15", "Electronics", 89999, 8, "Apple's latest iPhone with dynamic island", "Apple", 4.7),
            ("Sony WH-1000XM5 Headphones", "Electronics", 29999, 20, "Industry leading noise cancelling wireless headphones", "Sony", 4.8),
            ("Nike Air Max 270", "Footwear", 12999, 30, "Comfortable running shoes with Air Max cushioning", "Nike", 4.3),
            ("Levi's 511 Slim Jeans", "Clothing", 3999, 50, "Classic slim fit jeans in stretch denim", "Levi's", 4.4),
            ("HP Pavilion Laptop 15", "Electronics", 54999, 12, "Intel Core i5, 8GB RAM, 512GB SSD laptop", "HP", 4.2),
            ("Prestige Induction Cooktop", "Home Appliances", 2499, 25, "2000W induction cooktop with touch panel", "Prestige", 4.1),
            ("Adidas Ultraboost 22", "Footwear", 14999, 18, "High performance running shoes with boost cushioning", "Adidas", 4.6),
            ("Boat Airdopes 141", "Electronics", 1499, 100, "TWS earbuds with 42H battery and ASAP charge", "Boat", 4.0),
            ("Titan Analog Watch", "Accessories", 4999, 35, "Classic analog watch with leather strap", "Titan", 4.3),
            ("Wildcraft Backpack 30L", "Accessories", 1999, 45, "Durable backpack for college and travel", "Wildcraft", 4.2),
            ("Allen Solly Formal Shirt", "Clothing", 1299, 60, "Regular fit formal shirt for office wear", "Allen Solly", 4.1),
            ("LG 43 inch 4K TV", "Electronics", 34999, 10, "43 inch 4K UHD Smart TV with WebOS", "LG", 4.4),
            ("Philips Air Fryer HD9200", "Home Appliances", 6999, 20, "Digital air fryer with 7 preset programs", "Philips", 4.5),
            ("Woodland Casual Shoes", "Footwear", 3499, 40, "Premium leather casual shoes for daily wear", "Woodland", 4.2),
        ]

        cursor.executemany("""
            INSERT INTO products (name, category, price, stock, description, brand, rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, sample_products)
        conn.commit()

    cursor.close()
    conn.close()
    return True


def search_products(query: str, category: str = None, max_price: float = None):
    """Search products from database based on query."""
    conn = get_db_connection()
    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)

    sql = "SELECT * FROM products WHERE (name LIKE %s OR description LIKE %s OR brand LIKE %s OR category LIKE %s)"
    params = [f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"]

    if category:
        sql += " AND category = %s"
        params.append(category)

    if max_price:
        sql += " AND price <= %s"
        params.append(max_price)

    sql += " ORDER BY rating DESC LIMIT 5"

    cursor.execute(sql, params)
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products


def get_all_categories():
    """Get all product categories."""
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
    categories = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return categories


def get_products_by_category(category: str):
    """Get products by category."""
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM products WHERE category = %s ORDER BY rating DESC",
        (category,)
    )
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products


# ── Gemini AI setup ────────────────────────────────────────────
def setup_gemini():
    """Configure Gemini API."""
    if not GEMINI_API_KEY:
        return None
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "temperature": 0.7,
            "max_output_tokens": 1024,
        }
    )
    return model


def get_ai_response(model, user_message: str, products: list, chat_history: list):
    """Generate AI response using Gemini with product context."""

    # Build product context
    product_context = ""
    if products:
        product_context = "\n\nRelevant products found in our store:\n"
        for p in products:
            stock_status = "In Stock" if p['stock'] > 0 else "Out of Stock"
            product_context += f"""
- {p['name']} by {p['brand']}
  Price: ₹{p['price']:,.0f}
  Category: {p['category']}
  Rating: {p['rating']}/5
  Stock: {stock_status} ({p['stock']} units)
  Description: {p['description']}
"""

    # Build conversation history
    history_text = ""
    for msg in chat_history[-6:]:  # Last 6 messages for context
        role = "Customer" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    # System prompt
    system_prompt = f"""You are ShopAI, a friendly and helpful retail shopping assistant for an Indian e-commerce store.

Your responsibilities:
- Help customers find products they're looking for
- Answer questions about products, prices, availability
- Make product recommendations based on customer needs
- Provide helpful shopping advice
- Be conversational, warm and helpful

Store Information:
- We sell Electronics, Clothing, Footwear, Home Appliances, and Accessories
- All prices are in Indian Rupees (₹)
- We offer fast delivery across India

Previous conversation:
{history_text}

{product_context}

Customer's message: {user_message}

Respond naturally and helpfully. If products are found, mention them naturally in your response. 
Keep responses concise but helpful. Use Indian context where appropriate."""

    try:
        response = model.generate_content(system_prompt)
        return response.text
    except Exception as e:
        return f"I'm sorry, I couldn't process that request. Please try again! Error: {str(e)}"


def extract_search_query(user_message: str):
    """Extract key search terms from user message."""
    # Remove common words
    stop_words = ["i", "want", "need", "looking", "for", "show", "me", "find",
                  "a", "an", "the", "please", "can", "you", "have", "any",
                  "buy", "get", "under", "below", "cheap", "good", "best"]
    words = user_message.lower().split()
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return " ".join(keywords[:5]) if keywords else user_message


# ── Session state initialization ──────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model" not in st.session_state:
    st.session_state.model = setup_gemini()
if "db_ready" not in st.session_state:
    st.session_state.db_ready = init_database()


# ── UI Layout ──────────────────────────────────────────────────
# Header
st.markdown('<p class="header-title">🛍️ ShopAI</p>', unsafe_allow_html=True)
st.markdown('<p class="header-sub">Your Intelligent Retail Assistant — Ask me anything about our products!</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shopping-cart.png", width=80)
    st.markdown("### 🛍️ ShopAI Assistant")
    st.markdown("---")

    st.markdown("**Browse by Category:**")
    categories = ["All"] + get_all_categories()
    selected_category = st.selectbox("Select Category", categories)

    if selected_category and selected_category != "All":
        cat_products = get_products_by_category(selected_category)
        st.markdown(f"**{len(cat_products)} products in {selected_category}:**")
        for p in cat_products:
            with st.expander(f"{p['name']} — ₹{p['price']:,.0f}"):
                st.write(f"**Brand:** {p['brand']}")
                st.write(f"**Rating:** ⭐ {p['rating']}/5")
                stock_color = "green" if p['stock'] > 0 else "red"
                st.markdown(f"**Stock:** :{stock_color}[{'In Stock' if p['stock'] > 0 else 'Out of Stock'}]")
                st.write(p['description'])

    st.markdown("---")
    st.markdown("**💡 Try asking:**")
    suggestions = [
        "Show me laptops under ₹60,000",
        "I need wireless headphones",
        "What shoes do you have?",
        "Best rated electronics",
        "Show me clothing options",
    ]
    for s in suggestions:
        if st.button(s, key=s, use_container_width=True):
            st.session_state.quick_query = s

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("**Status:**")
    if st.session_state.model:
        st.success("✅ AI Connected")
    else:
        st.error("❌ Add GEMINI_API_KEY in .env")
    if st.session_state.db_ready:
        st.success("✅ Database Ready")
    else:
        st.warning("⚠️ Running in Demo Mode")


# ── Chat Interface ─────────────────────────────────────────────
chat_container = st.container()

with chat_container:
    # Welcome message
    if not st.session_state.messages:
        st.markdown("""
        <div class="chat-message-bot">
            👋 Hello! I'm ShopAI, your intelligent shopping assistant!<br><br>
            I can help you:<br>
            🔍 Find products you're looking for<br>
            💰 Filter by price range<br>
            ⭐ Recommend top-rated items<br>
            📦 Check stock availability<br><br>
            What are you shopping for today?
        </div>
        <div style="clear:both"></div>
        """, unsafe_allow_html=True)

    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message-user">{message["content"]}</div>
            <div style="clear:both"></div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message-bot">{message["content"]}</div>
            <div style="clear:both"></div>
            """, unsafe_allow_html=True)

            # Show product cards if any
            if "products" in message and message["products"]:
                cols = st.columns(min(3, len(message["products"])))
                for i, product in enumerate(message["products"][:3]):
                    with cols[i]:
                        stock_class = "in-stock" if product['stock'] > 0 else "out-stock"
                        stock_text = f"✅ In Stock ({product['stock']})" if product['stock'] > 0 else "❌ Out of Stock"
                        st.markdown(f"""
                        <div class="product-card">
                            <strong>{product['name']}</strong><br>
                            <small>by {product['brand']}</small><br>
                            <span class="price-tag">₹{product['price']:,.0f}</span><br>
                            ⭐ {product['rating']}/5<br>
                            <span class="{stock_class}">{stock_text}</span><br>
                            <small>{product['description'][:80]}...</small>
                        </div>
                        """, unsafe_allow_html=True)


# ── Chat Input ─────────────────────────────────────────────────
# Handle quick query from sidebar buttons
if "quick_query" in st.session_state:
    user_input = st.session_state.quick_query
    del st.session_state.quick_query
else:
    user_input = None

col1, col2 = st.columns([6, 1])
with col1:
    typed_input = st.chat_input("Ask me about products, prices, availability...")
with col2:
    pass

if typed_input:
    user_input = typed_input

# ── Process user input ─────────────────────────────────────────
if user_input:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Search for relevant products
    search_query = extract_search_query(user_input)
    products = []

    if st.session_state.db_ready:
        # Extract price filter if mentioned
        max_price = None
        words = user_input.lower().split()
        for i, word in enumerate(words):
            if word in ["under", "below", "within"] and i + 1 < len(words):
                try:
                    price_str = words[i + 1].replace("₹", "").replace(",", "").replace("k", "000")
                    max_price = float(price_str)
                except:
                    pass

        products = search_products(search_query, max_price=max_price)

    # Generate AI response
    if st.session_state.model:
        with st.spinner("ShopAI is thinking..."):
            response = get_ai_response(
                st.session_state.model,
                user_input,
                products,
                st.session_state.messages[:-1]
            )
    else:
        # Demo mode without API key
        if products:
            response = f"I found {len(products)} products matching your search! Here are the top results. (Note: Add your GEMINI_API_KEY in .env file for full AI responses)"
        else:
            response = "I couldn't find exact matches, but please try different keywords. (Note: Add your GEMINI_API_KEY in .env file for full AI responses)"

    # Add assistant response with products
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "products": products
    })

    st.rerun()
