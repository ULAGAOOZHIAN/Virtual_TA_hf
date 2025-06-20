import os		
import json		
from tqdm import tqdm		
from openai import OpenAI		
		
# Set up API client		
api_key = os.getenv("AIPIPE_TOKEN")		
if not api_key:		
    raise ValueError("Missing AIPIPE_TOKEN environment variable")		
		
client = OpenAI(		
    api_key=api_key,		
    base_url="https://aipipe.org/openai/v1"		
)		
		
# Parameters		
input_file = 'processed_tdscourse_2.jsonl'		
output_file = 'chunked_embeddings_tdscourse.jsonl'		
max_tokens = 400		
overlap_tokens = 40		
		
def chunk_text(text, max_len=max_tokens, overlap=overlap_tokens):		
    words = text.split()		
    chunks = []		
    start = 0		
    while start < len(words):		
        end = min(start + max_len, len(words))		
        chunk = ' '.join(words[start:end])		
        chunks.append(chunk)		
        if end == len(words):		
            break		
        start = end - overlap		
    return chunks		
		
def normalize_title_to_slug(title):		
    """Turn '1. Deployment Tools' -> '1-deployment-tools'"""		
    return title.lower().replace('.', '').replace(' ', '-')		
		
def extract_title_from_original_url(original_url):		
    """Extract and clean title from malformed 'original_url' field"""		
    if original_url.startswith('title:'):		
        return original_url.replace('title:', '').strip().strip('"')		
    return original_url.strip().strip('"')		
		
# Process and embed		
with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:		
    for line in tqdm(f_in, desc="Embedding chunks"):		
        post = json.loads(line)		
        text = post.get('content', '').strip()		
        if not text:		
            continue		
		
        raw_url = post.get('original_url', '')		
        title = extract_title_from_original_url(raw_url)		
        url_suffix = normalize_title_to_slug(title)		
		
        chunks = chunk_text(text)		
		
        for chunk in chunks:		
            embedding_response = client.embeddings.create(		
                input=chunk,		
                model="text-embedding-3-small"		
            )		
            embedding_vector = embedding_response.data[0].embedding		
		
            out_obj = {		
                'text_chunk': chunk,		
                'embedding': embedding_vector,		
                'title': title,		
                'url_suffix': url_suffix		
            }		
            f_out.write(json.dumps(out_obj, ensure_ascii=False) + '\n')		
