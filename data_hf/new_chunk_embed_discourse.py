import os			
import json			
from tqdm import tqdm			
from openai import OpenAI			
			
api_key = os.getenv("AIPIPE_TOKEN")			
if not api_key:			
    raise ValueError("Missing AIPIPE_TOKEN environment variable")			
			
client = OpenAI(			
    api_key=api_key,			
    base_url="https://aipipe.org/openai/v1"			
)			
			
input_file = 'processed_discourse.jsonl'			
output_file = 'chunked_embeddings.jsonl'			
			
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
        start = end - overlap  # overlap for next chunk			
    return chunks			
			
with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:			
    for line in tqdm(f_in, desc="Processing posts"):			
        post = json.loads(line)			
        text = post.get('text', '').strip()			
        if not text:			
            continue			
			
        url_info = post.get('url_info', {})			
			
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
                'url_info': url_info			
            }			
            f_out.write(json.dumps(out_obj, ensure_ascii=False) + '\n')			
