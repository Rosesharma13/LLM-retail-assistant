import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
from dotenv import load_dotenv

# ── Load environment variables ─────────────────────────────────
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)

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


# ── Product Data (replaces MySQL) ──────────────────────────────
@st.cache_data
def load_products():
    """Load products from CSV or use built-in data."""
    # Try loading from CSV file if it exists
    if os.path.exists("products.csv"):
        return pd.read_csv("products.csv")

    # Built-in sample products (no database needed)
    data = {
        "id": list(range(1, 16)),
        "name": [
            "Samsung Galaxy S24", "Apple iPhone 15",
            "Sony WH-1000XM5 Headphones", "Nike Air Max 270",
            "Levi's 511 Slim Jeans", "HP Pavilion Laptop 15",
            "Prestige Induction Cooktop", "Adidas Ultraboost 22",
            "Boat Airdopes 141", "Titan Analog Watch",
            "Wildcraft Backpack 30L", "Allen Solly Formal Shirt",
            "LG 43 inch 4K TV", "Philips Air Fryer HD9200",
            "Woodland Casual Shoes"
        ],
        "category": [
            "Electronics", "Electronics", "Electronics", "Footwear",
            "Clothing", "Electronics", "Home Appliances", "Footwear",
            "Electronics", "Accessories", "Accessories", "Clothing",
            "Electronics", "Home Appliances", "Footwear"
        ],
        "price": [
            79999, 89999, 29999, 12999, 3999, 54999,
            2499, 14999, 1499, 4999, 1999, 1299,
            34999, 6999, 3499
        ],
        "stock": [
            15, 8, 20, 30, 50, 12, 25, 18,
            100, 35, 45, 60, 10, 20, 40
        ],
        "description": [
            "Latest Samsung flagship smartphone with AI features",
            "Apple's latest iPhone with dynamic island",
            "Industry leading noise cancelling wireless headphones",
            "Comfortable running shoes with Air Max cushioning",
            "Classic slim fit jeans in stretch denim",
            "Intel Core i5, 8GB RAM, 512GB SSD laptop",
            "2000W induction cooktop with touch panel",
            "High performance running shoes with boost cushioning",
            "TWS earbuds with 42H battery and ASAP charge",
            "Classic analog watch with leather strap",
            "Durable backpack for college and travel",
            "Regular fit formal shirt for office wear",
            "43 inch 4K UHD Smart TV with WebOS",
            "Digital air fryer with 7 preset programs",
            "Premium leather casual shoes for daily wear"
        ],
        "brand": [
            "Samsung", "Apple", "Sony", "Nike", "Levi's",
            "HP", "Prestige", "Adidas", "Boat", "Titan",
            "Wildcraft", "Allen Solly", "LG", "Philips", "Woodland"
        ],
        "rating": [
            4.5, 4.7, 4.8, 4.3, 4.4, 4.2, 4.1,
            4.6, 4.0, 4.3, 4.2, 4.1, 4.4, 4.5, 4.2
        ]
    }
    return pd.DataFrame(data)


def search_products(query: str, category: str = None, max_price: float = None):
    """Search products from DataFrame."""
    df = load_products()
    query = query.lower()

    mask = (
        df["name"].str.lower().str.contains(query, na=False) |
        df["description"].str.lower().str.contains(query, na=False) |
        df["brand"].str.lower().str.contains(query, na=False) |
        df["category"].str.lower().str.contains(query, na=False)
    )
    results = df[mask]

    if category and category != "All":
        results = results[results["category"] == category]

    if max_price:
        results = results[results["price"] <= max_price]

    results = results.sort_values("rating", ascending=False).head(5)
    return results.to_dict("records")


def get_all_categories():
    df = load_products()
    return sorted(df["category"].unique().tolist())


def get_products_by_category(category: str):
    df = load_products()
    results = df[df["category"] == category].sort_values("rating", ascending=False)
    return results.to_dict("records")


# ── Gemini AI setup ────────────────────────────────────────────
def setup_gemini():
    if not GEMINI_API_KEY:
        return None
  genai.configure(api_key=GEMINI_API_KEY, transport="rest")
model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash",
    generation_config={
        "temperature": 0.7,
        "max_output_tokens": 512,
    }
)
    return model


def get_ai_response(model, user_message: str, products: list, chat_history: list):
    product_context = ""
    if products:
        product_context = "\n\nRelevant products found:\n"
        for p in products:
            stock_status = "In Stock" if p["stock"] > 0 else "Out of Stock"
            product_context += f"- {p['name']} by {p['brand']} | ₹{p['price']:,} | {p['category']} | ⭐{p['rating']} | {stock_status}\n"

    history_text = ""
    for msg in chat_history[-4:]:
        role = "Customer" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    system_prompt = f"""You are ShopAI, a friendly retail shopping assistant for an Indian e-commerce store.
Help customers find products, answer questions about prices and availability, and make recommendations.
All prices are in Indian Rupees (₹). Be concise and helpful.

Previous conversation:
{history_text}
{product_context}

Customer: {user_message}"""

    try:
        response = model.generate_content(system_prompt)
        return response.text
    except Exception as e:
        return f"I'm sorry, I couldn't process that request. Please try again! Error: {str(e)}"


def extract_search_query(user_message: str):
    stop_words = ["i", "want", "need", "looking", "for", "show", "me", "find",
                  "a", "an", "the", "please", "can", "you", "have", "any",
                  "buy", "get", "under", "below", "cheap", "good", "best"]
    words = user_message.lower().split()
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return " ".join(keywords[:5]) if keywords else user_message


# ── Session state ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model" not in st.session_state:
    st.session_state.model = setup_gemini()


# ── UI Layout ──────────────────────────────────────────────────
st.markdown('<p class="header-title">🛍️ ShopAI</p>', unsafe_allow_html=True)
st.markdown('<p class="header-sub">Your Intelligent Retail Assistant — Ask me anything about our products!</p>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🛍️ ShopAI Assistant")
    st.markdown("---")
    st.markdown("**Browse by Category:**")
    categories = ["All"] + get_all_categories()
    selected_category = st.selectbox("Select Category", categories)

    if selected_category and selected_category != "All":
        cat_products = get_products_by_category(selected_category)
        st.markdown(f"**{len(cat_products)} products in {selected_category}:**")
        for p in cat_products:
            with st.expander(f"{p['name']} — ₹{p['price']:,}"):
                st.write(f"**Brand:** {p['brand']}")
                st.write(f"**Rating:** ⭐ {p['rating']}/5")
                stock_color = "green" if p["stock"] > 0 else "red"
                st.markdown(f"**Stock:** :{stock_color}[{'In Stock' if p['stock'] > 0 else 'Out of Stock'}]")
                st.write(p["description"])

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
        st.error("❌ Add GEMINI_API_KEY in Secrets")
    st.success("✅ Database Ready")


# ── Chat Interface ─────────────────────────────────────────────
chat_container = st.container()
with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div class="chat-message-bot">
            👋 Hello! I'm ShopAI, your intelligent shopping assistant!<br><br>
            I can help you find products, check prices, and recommend items.<br><br>
            What are you shopping for today?
        </div>
        <div style="clear:both"></div>
        """, unsafe_allow_html=True)

    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message-user">{message["content"]}</div><div style="clear:both"></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message-bot">{message["content"]}</div><div style="clear:both"></div>', unsafe_allow_html=True)
            if "products" in message and message["products"]:
                cols = st.columns(min(3, len(message["products"])))
                for i, product in enumerate(message["products"][:3]):
                    with cols[i]:
                        stock_class = "in-stock" if product["stock"] > 0 else "out-stock"
                        stock_text = f"✅ In Stock ({product['stock']})" if product["stock"] > 0 else "❌ Out of Stock"
                        st.markdown(f"""
                        <div class="product-card">
                            <strong>{product['name']}</strong><br>
                            <small>by {product['brand']}</small><br>
                            <span class="price-tag">₹{product['price']:,}</span><br>
                            ⭐ {product['rating']}/5<br>
                            <span class="{stock_class}">{stock_text}</span><br>
                            <small>{product['description'][:80]}...</small>
                        </div>
                        """, unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────
if "quick_query" in st.session_state:
    user_input = st.session_state.quick_query
    del st.session_state.quick_query
else:
    user_input = None

typed_input = st.chat_input("Ask me about products, prices, availability...")
if typed_input:
    user_input = typed_input

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    search_query = extract_search_query(user_input)
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

    if st.session_state.model:
        with st.spinner("ShopAI is thinking..."):
            response = get_ai_response(
                st.session_state.model,
                user_input,
                products,
                st.session_state.messages[:-1]
            )
    else:
        if products:
            response = f"I found {len(products)} products matching your search! (Add GEMINI_API_KEY in Streamlit Secrets for full AI responses)"
        else:
            response = "I couldn't find exact matches. Try different keywords! (Add GEMINI_API_KEY in Streamlit Secrets for full AI responses)"

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "products": products
    })
    st.rerun()
