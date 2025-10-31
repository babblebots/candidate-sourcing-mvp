"""
Resume Search - Fixed Encoding Issues
Saves progress so we don't lose work if something fails
"""

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.core import Settings
import os
import pickle

def clean_text(text):
    """Remove problematic characters - keep as much data as possible"""
    if not text:
        return ""
    
    try:
        # Replace surrogates and problematic unicode
        # This keeps most characters but removes the ones causing issues
        cleaned = text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        # Remove any remaining surrogates
        cleaned = ''.join(char for char in cleaned if ord(char) < 0x110000 and not (0xD800 <= ord(char) <= 0xDFFF))
        return cleaned
    except Exception as e:
        # Last resort: just replace problem characters
        return text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')

def load_and_clean_resumes(resume_path, cache_file="resumes_cache.pkl"):
    """Load resumes with caching"""
    
    # Check if we have cached clean documents
    if os.path.exists(cache_file):
        print(f"📦 Found cached resumes, loading from {cache_file}...")
        with open(cache_file, 'rb') as f:
            documents = pickle.load(f)
        print(f"✅ Loaded {len(documents)} resumes from cache!")
        return documents
    
    print(f"⏳ Loading fresh resumes from: {resume_path}")
    
    try:
        documents = SimpleDirectoryReader(
            input_dir=resume_path,
            recursive=False,
            required_exts=[".pdf", ".doc", ".docx"],
            errors='ignore'  # Skip files that can't be read
        ).load_data()
        
        print(f"🔧 Cleaning {len(documents)} documents...")
        
        cleaned_docs = []
        problem_files = []
        
        for i, doc in enumerate(documents):
            try:
                # Clean the text - be lenient
                if doc.text:
                    doc.text = clean_text(doc.text)
                else:
                    doc.text = ""
                
                # Only verify it's not empty
                if len(doc.text.strip()) > 10:  # At least 10 characters
                    cleaned_docs.append(doc)
                else:
                    filename = doc.metadata.get('file_name', f'doc_{i}')
                    problem_files.append(f"{filename} (empty/too short)")
                
                if (i + 1) % 50 == 0:
                    print(f"   Cleaned {i + 1}/{len(documents)} documents...")
                    
            except Exception as e:
                filename = doc.metadata.get('file_name', f'doc_{i}')
                problem_files.append(f"{filename} (error: {str(e)[:30]})")
                continue
        
        print(f"✅ Successfully cleaned {len(cleaned_docs)} resumes!")
        
        if problem_files:
            print(f"⚠️  Skipped {len(problem_files)} problematic files:")
            for f in problem_files[:5]:
                print(f"   - {f}")
            if len(problem_files) > 5:
                print(f"   ... and {len(problem_files) - 5} more")
        
        # Cache the cleaned documents
        print(f"💾 Saving cleaned resumes to cache...")
        with open(cache_file, 'wb') as f:
            pickle.dump(cleaned_docs, f)
        print(f"✅ Cache saved!")
        
        return cleaned_docs
        
    except Exception as e:
        print(f"❌ Error loading documents: {e}")
        return None

def create_or_load_index(documents, persist_dir="./storage"):
    """Create index with persistence"""
    
    # Check if index already exists
    if os.path.exists(persist_dir):
        print(f"📦 Found existing index at {persist_dir}")
        print("   Loading from disk (much faster!)...")
        try:
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            index = load_index_from_storage(storage_context)
            print("✅ Index loaded from disk!")
            return index
        except Exception as e:
            print(f"⚠️  Could not load index: {e}")
            print("   Creating fresh index...")
    
    # Create new index
    print(f"⏳ Creating search index (generating embeddings)...")
    print("   This will take 3-5 minutes for 400 resumes...")
    
    try:
        index = VectorStoreIndex.from_documents(
            documents,
            show_progress=True
        )
        
        # Persist to disk
        print(f"💾 Saving index to {persist_dir}...")
        index.storage_context.persist(persist_dir=persist_dir)
        print("✅ Index created and saved!")
        
        return index
        
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_search(index):
    """Run test searches"""
    
    print("\n" + "=" * 60)
    print("TESTING SEARCHES")
    print("=" * 60)
    
    test_queries = [
        "Find candidates with React experience",
        "Python developer with machine learning skills",
        "Full stack developer with 5+ years experience",
        "Java backend developer"
    ]
    
    query_engine = index.as_query_engine(similarity_top_k=5)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test Query {i}: '{query}'")
        print("-" * 60)
        
        try:
            response = query_engine.query(query)
            print(f"Answer: {str(response)[:300]}...")
            
            print(f"\nTop matching files:")
            for j, node in enumerate(response.source_nodes[:3], 1):
                filename = node.metadata.get('file_name', 'unknown')
                score = node.score
                print(f"  {j}. {filename} (similarity: {score:.3f})")
                
        except Exception as e:
            print(f"❌ Search error: {e}")

def interactive_search(index):
    """Interactive search mode"""
    
    print("\n" + "=" * 60)
    print("INTERACTIVE MODE")
    print("Type your queries, or 'quit' to exit")
    print("=" * 60)
    
    query_engine = index.as_query_engine(similarity_top_k=5)
    
    while True:
        query = input("\n🔍 Your query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not query:
            continue
        
        try:
            response = query_engine.query(query)
            print(f"\n📝 Answer: {response}")
            
            print(f"\n📄 Top matching files:")
            for i, node in enumerate(response.source_nodes[:5], 1):
                filename = node.metadata.get('file_name', 'unknown')
                score = node.score
                preview = node.text[:100].replace('\n', ' ')
                print(f"\n{i}. {filename} (score: {score:.3f})")
                print(f"   Preview: {preview}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function"""
    
    print("=" * 60)
    print("RESUME SEARCH ENGINE - FIXED VERSION")
    print("=" * 60)
    
    resume_path = "/Users/test/Desktop/test-repo/sourcing-mvp/resumes"
    
    # Check path
    if not os.path.exists(resume_path):
        print(f"❌ Error: Path not found: {resume_path}")
        return
    
    # Step 1: Load and clean resumes
    documents = load_and_clean_resumes(resume_path)
    
    if not documents:
        print("❌ Failed to load documents")
        return
    
    # Step 2: Create or load index
    index = create_or_load_index(documents)
    
    if not index:
        print("❌ Failed to create index")
        return
    
    # Step 3: Run tests
    test_search(index)
    
    # Step 4: Interactive mode
    interactive_search(index)

if __name__ == "__main__":
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not found!")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        print("\nContinue anyway? (y/n)")
        if input().strip().lower() != 'y':
            exit()
    
    main()