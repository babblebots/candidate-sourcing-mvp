"""
Resume Search - WORKING VERSION
Creates new Document objects instead of modifying existing ones
"""

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document
from llama_index.core import StorageContext, load_index_from_storage
import os
import pickle

def clean_text(text):
    """Remove problematic unicode characters (like emojis)"""
    if not text:
        return ""
    try:
        # Remove surrogate pairs and other problematic unicode
        cleaned = text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        return cleaned
    except:
        return text

def load_and_clean_resumes(resume_path, cache_file="clean_resumes.pkl"):
    """Load and clean all resumes"""
    
    # Use cache if available
    if os.path.exists(cache_file):
        print(f"📦 Loading from cache: {cache_file}")
        with open(cache_file, 'rb') as f:
            clean_docs = pickle.load(f)
        print(f"✅ Loaded {len(clean_docs)} resumes from cache!\n")
        return clean_docs
    
    print(f"⏳ Loading resumes from: {resume_path}")
    
    # Load all documents
    documents = SimpleDirectoryReader(
        input_dir=resume_path,
        recursive=False,
        required_exts=[".pdf", ".doc", ".docx"],
        errors='ignore'
    ).load_data()
    
    print(f"✅ Loaded {len(documents)} document chunks\n")
    
    # Clean documents by creating NEW Document objects
    print(f"🔧 Cleaning documents and creating new objects...")
    
    clean_docs = []
    problem_count = 0
    
    for i, doc in enumerate(documents):
        try:
            # Check if text needs cleaning
            try:
                doc.text.encode('utf-8')
                # Text is fine, keep as is
                clean_docs.append(doc)
            except UnicodeEncodeError:
                # Text has issues, create new cleaned document
                cleaned_text = clean_text(doc.text)
                new_doc = Document(
                    text=cleaned_text,
                    metadata=doc.metadata.copy()
                )
                clean_docs.append(new_doc)
                problem_count += 1
                
            if (i + 1) % 100 == 0:
                print(f"   Processed {i + 1}/{len(documents)} documents...")
                
        except Exception as e:
            print(f"   ⚠️  Error with document {i}: {e}")
            continue
    
    print(f"\n✅ Successfully processed {len(clean_docs)} documents")
    if problem_count > 0:
        print(f"   🔧 Cleaned {problem_count} documents with encoding issues")
    
    # Save to cache
    print(f"\n💾 Saving to cache: {cache_file}")
    with open(cache_file, 'wb') as f:
        pickle.dump(clean_docs, f)
    print(f"✅ Cache saved!\n")
    
    return clean_docs

def create_or_load_index(documents, persist_dir="./storage"):
    """Create or load the search index"""
    
    # Try loading existing index
    if os.path.exists(persist_dir):
        print(f"📦 Found existing index at: {persist_dir}")
        try:
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            index = load_index_from_storage(storage_context)
            print("✅ Loaded index from disk!\n")
            return index
        except Exception as e:
            print(f"⚠️  Could not load index: {e}")
            print("   Creating fresh index...\n")
    
    # Create new index
    print(f"⏳ Creating search index...")
    print(f"   Generating embeddings for {len(documents)} documents...")
    print(f"   This will take 3-5 minutes...\n")
    
    try:
        index = VectorStoreIndex.from_documents(
            documents,
            show_progress=True
        )
        
        # Save to disk
        print(f"\n💾 Saving index to: {persist_dir}")
        index.storage_context.persist(persist_dir=persist_dir)
        print("✅ Index saved!\n")
        
        return index
        
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_searches(index):
    """Run test searches"""
    
    print("\n" + "=" * 70)
    print("RUNNING TEST SEARCHES")
    print("=" * 70)
    
    test_queries = [
        "Find React developers with 3+ years experience",
        "Python developer with machine learning and NLP skills",
        "Full stack developer Node.js and React",
        "DevOps engineer with AWS and Kubernetes experience",
        "Java backend developer with Spring Boot"
    ]
    
    query_engine = index.as_query_engine(similarity_top_k=5)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'─' * 70}")
        print(f"🔍 Query {i}: {query}")
        print(f"{'─' * 70}")
        
        try:
            response = query_engine.query(query)
            
            # Show answer
            answer = str(response)
            if len(answer) > 300:
                answer = answer[:300] + "..."
            print(f"\n📝 Answer:\n{answer}")
            
            # Show top matches
            print(f"\n📄 Top Matching Resumes:")
            for j, node in enumerate(response.source_nodes[:3], 1):
                filename = node.metadata.get('file_name', 'unknown')
                score = node.score
                preview = node.text[:150].replace('\n', ' ').strip()
                
                print(f"\n{j}. {filename}")
                print(f"   Similarity Score: {score:.3f}")
                print(f"   Preview: {preview}...")
                
        except Exception as e:
            print(f"❌ Search failed: {e}")

def interactive_mode(index):
    """Interactive search mode"""
    
    print("\n" + "=" * 70)
    print("INTERACTIVE SEARCH MODE")
    print("=" * 70)
    print("\nType your search queries below.")
    print("Commands: 'quit' or 'exit' to stop, 'help' for tips\n")
    
    query_engine = index.as_query_engine(similarity_top_k=5)
    
    while True:
        try:
            query = input("\n🔍 Your query: ").strip()
            
            if not query:
                continue
                
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
                
            if query.lower() == 'help':
                print("\n💡 Search Tips:")
                print("  - Be specific: 'React developer 5 years' vs 'developer'")
                print("  - Mention skills: 'Python machine learning TensorFlow'")
                print("  - Include requirements: 'Java Spring Boot microservices'")
                print("  - Try variations: 'frontend' vs 'front-end' vs 'UI developer'")
                continue
            
            # Perform search
            response = query_engine.query(query)
            
            # Show results
            print(f"\n{'─' * 70}")
            print(f"📝 Answer:")
            print(f"{'─' * 70}")
            print(str(response))
            
            print(f"\n{'─' * 70}")
            print(f"📄 Top Matching Resumes:")
            print(f"{'─' * 70}")
            
            for i, node in enumerate(response.source_nodes, 1):
                filename = node.metadata.get('file_name', 'unknown')
                score = node.score
                preview = node.text[:200].replace('\n', ' ').strip()
                
                print(f"\n{i}. {filename}")
                print(f"   Score: {score:.3f}")
                print(f"   {preview}...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def main():
    """Main function"""
    
    print("\n" + "=" * 70)
    print("RESUME SEARCH ENGINE v2.0")
    print("=" * 70 + "\n")
    
    resume_path = "/Users/test/Desktop/test-repo/sourcing-mvp/resumes"
    
    # Verify path exists
    if not os.path.exists(resume_path):
        print(f"❌ Error: Path not found: {resume_path}")
        return
    
    # Count files
    files = [f for f in os.listdir(resume_path) if f.endswith(('.pdf', '.doc', '.docx'))]
    print(f"📁 Resume folder: {resume_path}")
    print(f"📊 Files found: {len(files)} resumes\n")
    
    # Step 1: Load and clean resumes
    print("=" * 70)
    print("STEP 1: LOADING RESUMES")
    print("=" * 70 + "\n")
    
    documents = load_and_clean_resumes(resume_path)
    
    if not documents or len(documents) == 0:
        print("❌ No documents loaded!")
        return
    
    # Step 2: Create/load search index
    print("=" * 70)
    print("STEP 2: CREATING SEARCH INDEX")
    print("=" * 70 + "\n")
    
    index = create_or_load_index(documents)
    
    if not index:
        print("❌ Failed to create index!")
        return
    
    print("✅ Search engine ready!\n")
    
    # Step 3: Run test searches
    test_searches(index)
    
    # Step 4: Interactive mode
    interactive_mode(index)

if __name__ == "__main__":
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not found in environment!")
        print("\nTo use this script, you need an OpenAI API key.")
        print("Get one at: https://platform.openai.com/api-keys")
        print("\nSet it with:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("\nContinue anyway? (y/n): ", end="")
        
        if input().strip().lower() != 'y':
            print("Exiting.")
            exit()
    
    main()