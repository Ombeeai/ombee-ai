import os
from typing import List

def load_documents(data_dir: str = "data/holistic") -> List[dict]:
    """Load all text documents from directory."""
    documents = []
    
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.txt'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        documents.append({
                            'content': content,
                            'source': file,
                            'id': file.replace('.txt', '').replace(' ', '_')
                        })
                except Exception as e:
                    print(f"Error reading {file}: {e}")
    
    return documents