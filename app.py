"""
Resume Search UI - Streamlit App
Simple MVP interface for searching resumes
"""

import streamlit as st
from llama_index.core import StorageContext, load_index_from_storage
import os
import base64
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Resume Search Engine",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS for better looking cards
st.markdown("""
<style>
    .resume-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .score-badge {
        background-color: #4CAF50;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    .score-medium {
        background-color: #FF9800;
    }
    .score-low {
        background-color: #f44336;
    }
    .filename {
        font-size: 18px;
        font-weight: bold;
        color: #1976D2;
        margin-bottom: 10px;
    }
    .preview-text {
        color: #555;
        line-height: 1.6;
        margin-top: 10px;
        font-size: 14px;
    }
    .search-box {
        font-size: 16px;
    }
    .stButton>button {
        width: 100%;
        background-color: #1976D2;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_search_index():
    """Load the search index (cached)"""
    persist_dir = "./storage"
    
    if not os.path.exists(persist_dir):
        st.error("❌ Search index not found! Please run the indexing script first.")
        st.info("Run: python resume_search_working.py")
        st.stop()
    
    try:
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context)
        return index
    except Exception as e:
        st.error(f"❌ Failed to load index: {e}")
        st.stop()

def get_score_class(score):
    """Return CSS class based on score"""
    if score >= 0.8:
        return "score-badge"
    elif score >= 0.6:
        return "score-badge score-medium"
    else:
        return "score-badge score-low"

def display_resume_card(result, rank):
    """Display a single resume card"""
    filename = result['filename']
    file_path = result.get('file_path', '')
    score = result['score']
    preview = result['preview']
    full_text = result['full_text']
    
    # Create card HTML
    score_class = get_score_class(score)
    
    # Main card
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f"""
        <div class="resume-card">
            <span class="{score_class}">Score: {score:.2f}</span>
            <div class="filename">#{rank} - {filename}</div>
            <div class="preview-text">{preview}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Preview button - use simple unique key
        modal_key = f'modal_{rank}'
        
        if st.button("👁️ View Full", key=f"btn_{rank}"):
            st.session_state[modal_key] = not st.session_state.get(modal_key, False)
            st.rerun()
    
    # Show full content if toggled on
    if st.session_state.get(f'modal_{rank}', False):
        st.markdown("---")
        st.markdown(f"### 📄 Full Resume: {filename}")
        
        # Try to display PDF if file exists
        if file_path and os.path.exists(file_path) and file_path.lower().endswith('.pdf'):
            try:
                with open(file_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                
                # Display PDF in iframe
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
                
                # Also provide download link
                st.download_button(
                    label="⬇️ Download PDF",
                    data=open(file_path, "rb"),
                    file_name=filename,
                    mime="application/pdf",
                    key=f"download_{rank}"
                )
            except Exception as e:
                st.error(f"Could not display PDF: {e}")
                st.text_area(
                    "Resume Text",
                    value=full_text if full_text else "No content available",
                    height=400,
                    key=f"text_{rank}",
                    label_visibility="collapsed"
                )
        else:
            # Fallback to text display
            st.text_area(
                "Resume Text",
                value=full_text if full_text else "No content available",
                height=400,
                key=f"text_{rank}",
                label_visibility="collapsed"
            )
        
        if st.button("✖️ Close", key=f"close_{rank}"):
            st.session_state[f'modal_{rank}'] = False
            st.rerun()
        st.markdown("---")

def search_resumes(query, top_k=10):
    """Search resumes and return results"""
    index = st.session_state.index
    
    try:
        query_engine = index.as_query_engine(similarity_top_k=top_k)
        response = query_engine.query(query)
        
        results = []
        resume_dir = "/Users/test/Desktop/test-repo/sourcing-mvp/resumes"
        
        for node in response.source_nodes:
            filename = node.metadata.get('file_name', 'unknown')
            # Try to get file_path from metadata, or construct it
            file_path = node.metadata.get('file_path', '')
            if not file_path and filename != 'unknown':
                file_path = os.path.join(resume_dir, filename)
            
            results.append({
                'filename': filename,
                'file_path': file_path,
                'score': node.score,
                'preview': node.text[:300].replace('\n', ' ').strip() + "...",
                'full_text': node.text
            })
        
        return results, str(response)
        
    except Exception as e:
        st.error(f"Search error: {e}")
        return [], None

def main():
    # Title
    st.title("🔍 Resume Search Engine")
    st.markdown("Search through resumes using natural language queries")
    
    # Load index
    if 'index' not in st.session_state:
        with st.spinner("Loading search index..."):
            st.session_state.index = load_search_index()
        st.success("✅ Search engine ready!")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        top_k = st.slider(
            "Number of results",
            min_value=5,
            max_value=20,
            value=10,
            step=1
        )
        
        st.divider()
        
        st.subheader("💡 Search Tips")
        st.markdown("""
        - **Be specific**: "React developer 5+ years"
        - **Mention skills**: "Python ML TensorFlow"
        - **Include requirements**: "Full stack Node.js MongoDB"
        - **Try variations**: "frontend" vs "UI developer"
        """)
        
        st.divider()
        
        st.subheader("📊 Example Queries")
        example_queries = [
            "React developer with 5 years experience",
            "Python machine learning engineer",
            "Full stack JavaScript developer",
            "DevOps AWS Kubernetes Docker",
            "Java Spring Boot microservices"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{query}", use_container_width=True):
                st.session_state.search_query = query
                st.session_state.trigger_search = True
                st.rerun()
    
    # Search section
    st.divider()
    
    # Search input
    # Initialize search_query in session state if not present
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ''
    
    # Use session state key directly for the text input
    st.text_input(
        "🔎 Enter your search query",
        placeholder="e.g., React developer with 5 years experience",
        key="search_query"
    )
    
    # Get the value from session state
    search_query = st.session_state.search_query
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_button = st.button("🚀 Search", type="primary", use_container_width=True)
    
    with col2:
        if st.button("🔄 Clear", use_container_width=True):
            # Delete session state keys instead of setting to empty
            if 'search_query' in st.session_state:
                del st.session_state.search_query
            if 'last_results' in st.session_state:
                del st.session_state.last_results
            if 'last_summary' in st.session_state:
                del st.session_state.last_summary
            if 'last_query' in st.session_state:
                del st.session_state.last_query
            st.rerun()
    
    # Perform search (either from button click or triggered by example query)
    should_search = (search_button or st.session_state.get('trigger_search', False)) and search_query
    
    # Reset trigger flag
    if st.session_state.get('trigger_search', False):
        st.session_state.trigger_search = False
    
    # Perform search and store in session state
    if should_search:
        with st.spinner("Searching resumes..."):
            results, summary = search_resumes(search_query, top_k)
            # Store results in session state so they persist across reruns
            st.session_state.last_results = results
            st.session_state.last_summary = summary
            st.session_state.last_query = search_query
    
    # Display results from session state (persists across reruns)
    if st.session_state.get('last_results') and st.session_state.get('last_query') == search_query:
        results = st.session_state.last_results
        summary = st.session_state.last_summary
        
        if results:
            # Display summary
            st.success(f"✅ Found {len(results)} matching resumes")
            
            # AI Summary
            if summary:
                with st.expander("🤖 AI Summary", expanded=True):
                    st.info(summary)
            
            st.divider()
            
            # Display results
            st.subheader(f"📋 Top {len(results)} Results (Sorted by Relevance)")
            
            for i, result in enumerate(results, 1):
                display_resume_card(result, i)
        else:
            st.warning("No results found. Try different keywords.")
    
    elif search_button and not search_query:
        st.warning("⚠️ Please enter a search query")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #888; padding: 20px;'>
        <p>Resume Search Engine MVP | Powered by LlamaIndex & OpenAI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()