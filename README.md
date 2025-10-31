# 🔍 Resume Search Engine

AI-powered semantic search for resumes using LlamaIndex and OpenAI embeddings. Search through hundreds of resumes using natural language queries.

## 🌟 Features

- **Semantic Search**: Natural language queries like "React developer with 5 years experience"
- **AI-Powered Summaries**: Get intelligent summaries of matching resumes
- **PDF Preview**: View resume PDFs directly in the browser
- **Smart Ranking**: Results ranked by relevance score
- **Modern UI**: Beautiful, responsive interface with example queries

## 🚀 Live Demo

[Deploy on Streamlit Community Cloud]

## 📋 Prerequisites

- Python 3.10+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd sourcing-mvp
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up OpenAI API key

```bash
export OPENAI_API_KEY='your-api-key-here'
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

### 5. Prepare your data

Place resume files (PDF, DOC, DOCX) in the `resumes/` directory.

### 6. Build search index

```bash
python diagnose_resumes.py
```

This will:
- Load and clean all resumes
- Generate embeddings (takes 3-5 minutes)
- Save the search index to `storage/`

### 7. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

## 📁 Project Structure

```
sourcing-mvp/
├── app.py                 # Main Streamlit UI
├── diagnose_resumes.py    # Index builder & search engine
├── requirements.txt       # Python dependencies
├── resumes/              # Resume files (not in git)
├── storage/              # Search index (not in git)
└── README.md
```

## 🔧 Configuration

### Search Parameters

In the app sidebar, you can adjust:
- **Number of results**: 5-20 top matches
- **Example queries**: Quick-start templates

### Indexing Options

In `diagnose_resumes.py`:
- Resume directory path
- File types to index
- Embedding model

## 🎯 Example Queries

- "React developer with 5 years experience"
- "Python machine learning engineer"
- "Full stack JavaScript developer"
- "DevOps AWS Kubernetes Docker"
- "Java Spring Boot microservices"

## 🚢 Deployment on Streamlit Cloud

### 1. Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Configure Secrets

In Streamlit Cloud, add your secrets:
```toml
OPENAI_API_KEY = "your-api-key-here"
```

### 3. Pre-build Index

⚠️ **Important**: Build the index locally before deploying:
1. Run `python diagnose_resumes.py` locally
2. Commit the `storage/` directory (temporarily remove from `.gitignore`)
3. Push to GitHub

### 4. Deploy

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repo
3. Select `app.py` as the main file
4. Deploy!

## 📝 Notes

- **Privacy**: Resume files are not committed to git
- **Index Cache**: The search index is cached for fast loading
- **API Costs**: Embedding generation uses OpenAI API (one-time cost per resume)

## 🤝 Contributing

Contributions welcome! Feel free to open issues or submit PRs.

## 📄 License

MIT License

## 🙋 Support

For issues or questions, please open a GitHub issue.

---

**Built with**:
- [Streamlit](https://streamlit.io/)
- [LlamaIndex](https://www.llamaindex.ai/)
- [OpenAI](https://openai.com/)

