# 🚀 MARAG System - Setup and Running Guide

## 📋 Prerequisites

Before running the MARAG system, ensure you have:

1. **Python 3.8+** installed
2. **OpenAI API Key** (required)
3. **Tavily API Key** (optional, for web search)
4. **Internet connection** for package installation

## ⚙️ Quick Setup

### 1. Environment Setup

1. **Copy the environment template:**
   ```bash
   copy .env.example .env
   ```

2. **Edit the `.env` file** and add your API keys:
   ```
   OPENAI_API_KEY=your_actual_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here  # Optional
   ```

### 2. Install Dependencies

The core dependencies have been installed, but you may need additional packages:

```bash
# Install additional packages if needed
pip install tavily-python llama-index-retrievers-pathway
```

### 3. Test Your Setup

Run the demo script to verify everything is working:

```bash
python demo.py
```

## 🏃‍♂️ Running the System

### Option 1: Interactive Demo
```bash
python demo.py
```

### Option 2: Run Specific Components

#### **Adaptive RAG System**
```bash
python final_adaptive_rag.py
```
- Advanced retrieval-augmented generation
- Uses vector databases and web search
- Supports financial document analysis

#### **Multi-Agent System**
```bash
python modular_agent.py
```
- Collaborative multi-agent framework
- Task planning and execution
- Financial analysis capabilities

#### **Financial Markets Analysis**
```bash
python financial_markets.py
```
- Stock market analysis tools
- Technical indicators (RSI, Moving Averages)
- Financial data processing

#### **Report Generation**
```bash
python report_gen/report_gen.py
```
- Automated report generation
- Financial document analysis
- Chart and graph creation

### Option 3: Jupyter Notebook Interface

If you prefer an interactive notebook experience:

1. Install Jupyter:
   ```bash
   pip install jupyter
   ```

2. Start Jupyter:
   ```bash
   jupyter notebook
   ```

3. Create a new notebook and import the modules you need.

## 📁 Project Structure

```
MARAG/
├── 🎯 Main Components
│   ├── final_adaptive_rag.py     # Advanced RAG system
│   ├── new_adaptive_rag.py       # Alternative RAG implementation
│   ├── modular_agent.py          # Multi-agent framework
│   └── financial_markets.py      # Financial analysis tools
├── 🔧 Utilities
│   ├── response_transformation.py # Response processing
│   ├── output_parser.py          # Output parsing utilities
│   ├── math_tools.py             # Mathematical operations
│   └── Architecture.py           # System architecture
├── 📊 Specialized Modules
│   ├── finance/                  # Financial analysis modules
│   ├── report_gen/              # Report generation
│   ├── search/                  # Search functionality
│   └── maths/                   # Mathematical computations
├── 📄 Data & Reports
│   ├── Financial_Reports/        # Sample financial documents
│   ├── images/                  # Generated charts and graphs
│   └── dataset_finance_bench.csv # Financial datasets
└── ⚙️ Configuration
    ├── .env.example             # Environment template
    ├── requirements.txt         # Dependencies
    └── demo.py                 # Demo script
```

## 🔑 Required API Keys

### OpenAI API Key (Required)
1. Visit [OpenAI API](https://platform.openai.com/api-keys)
2. Create an account and generate an API key
3. Add it to your `.env` file

### Tavily API Key (Optional)
1. Visit [Tavily](https://tavily.com/)
2. Sign up and get your API key
3. Add it to your `.env` file for web search functionality

## 🛠️ Troubleshooting

### Common Issues

#### **Import Errors**
```bash
# Install missing dependencies
pip install langchain langchain-community langchain-openai langgraph openai python-dotenv pydantic
```

#### **API Key Errors**
- Ensure your `.env` file is in the project root
- Check that your API keys are valid and not expired
- Verify the `.env` file format (no spaces around `=`)

#### **Network Connection Issues**
- Some packages require Rust compiler
- Try installing packages individually if batch installation fails
- Check your internet connection

#### **Path Issues**
- Ensure you're running commands from the project directory
- Use absolute paths if needed

### **Package Installation Issues**

If some packages fail to install (like `jiter` requiring Rust):

1. **Skip problematic packages** and install core dependencies only
2. **Use alternative packages** or older versions
3. **Install Rust** if you need specific packages:
   - Visit [rustup.rs](https://rustup.rs/)
   - Follow installation instructions

## 📚 Usage Examples

### Basic RAG Query
```python
from final_adaptive_rag import *
# Run a financial query
query = "What is the revenue growth of 3M Company in 2022?"
result = process_query(query)
print(result)
```

### Financial Analysis
```python
from financial_markets import *
# Analyze stock data
prices = [100, 102, 104, 103, 105, 106, 108, 110, 112, 114]
rsi = calculate_rsi(prices, period=14)
print(f"RSI: {rsi}")
```

### Multi-Agent Task
```python
from modular_agent import *
# Create and run a multi-agent task
agent = create_agent(llm, tools, prompt, joiner_prompt, 'finance')
result = agent.stream({"messages": [HumanMessage(content="Your query here")]})
```

## 🎯 Next Steps

1. **Explore the components** - Start with `demo.py` to understand the system
2. **Customize for your needs** - Modify prompts and tools in individual files
3. **Add your own data** - Place documents in `Financial_Reports/` for analysis
4. **Extend functionality** - Add new tools and agents as needed

## 🆘 Getting Help

If you encounter issues:

1. **Check the demo output** - Run `python demo.py` first
2. **Verify your API keys** - Ensure they're valid and properly set
3. **Review the logs** - Look for specific error messages
4. **Check dependencies** - Make sure all required packages are installed

## 📞 Support

For technical issues or questions about the MARAG system, please check:
- The project documentation
- Error logs for specific issues
- API key validity and quota limits