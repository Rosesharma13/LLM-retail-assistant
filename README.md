# 🛍️ ShopAI — LLM-Based Intelligent Retail Assistant

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-000000?style=flat&logo=chainlink&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=flat&logo=google&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat&logo=mysql&logoColor=white)

## 📌 Overview

ShopAI is an end-to-end LLM-powered retail shopping assistant that enables customers to search and discover products using natural language. Built with Google Gemini API for intelligent response generation and MySQL for real-time product database integration.

## ✨ Features

- 🤖 **Natural Language Understanding** — Ask for products in plain English
- 💬 **Multi-turn Conversation** — Remembers context across the chat session
- 🔍 **Smart Product Search** — Searches by name, category, brand, or description
- 💰 **Price Filtering** — "Show me laptops under ₹60,000"
- 📦 **Real-time Stock Check** — Live inventory status from MySQL database
- 🗂️ **Category Browse** — Filter products by Electronics, Clothing, Footwear, etc.
- ⭐ **Rating-based Recommendations** — Top-rated products shown first
- 🎨 **Clean Chat UI** — Streamlit-based interactive web interface

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core programming language |
| **Google Gemini API** | LLM for natural language responses |
| **Streamlit** | Web interface and deployment |
| **MySQL** | Product database |
| **mysql-connector-python** | Database connectivity |
| **python-dotenv** | Environment variable management |

## 📁 Project Structure

```
llm-retail-assistant/
├── app.py              # Main Streamlit application
├── setup_db.py         # Database initialization script
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Files to exclude from Git
└── README.md           # Project documentation
```

## 🚀 How to Run

### Step 1 — Clone the repository
```bash
git clone https://github.com/yourusername/llm-retail-assistant.git
cd llm-retail-assistant
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Set up environment variables
```bash
cp .env.example .env
```
Edit `.env` and add your credentials:
```
GEMINI_API_KEY=your_gemini_api_key_here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=retail_db
```

### Step 4 — Get Gemini API Key (Free)
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy and paste into your `.env` file

### Step 5 — Set up database
```bash
python setup_db.py
```

### Step 6 — Run the app
```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501** 🎉

## 💬 Example Queries

| You ask | ShopAI does |
|---|---|
| "Show me laptops under ₹60,000" | Searches electronics with price filter |
| "I need wireless headphones" | Finds all headphone options |
| "Best rated shoes" | Returns top-rated footwear |
| "What phones do you have?" | Lists all smartphones |
| "Show me clothing options" | Displays clothing category |

## 📸 Screenshots




















## 🔑 Key Learning Outcomes

- **LLM Integration** — Connecting Google Gemini API for context-aware responses
- **Database-AI Pipeline** — Real-time MySQL queries feeding LLM context
- **Conversation Memory** — Managing multi-turn chat history
- **Streamlit Deployment** — Building and deploying interactive AI web apps
- **Prompt Engineering** — Designing effective system prompts for retail domain

## 👩‍💻 Author

**Rose Sharma**
- LinkedIn: [linkedin.com/in/rose-sharma13](https://www.linkedin.com/in/rose-sharma13)
- Email: rosesharmaa132003@gmail.com

## 📄 License

This project is licensed under the MIT License.
