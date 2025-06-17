# === MODIFIED main.py with dynamic URL construction ===
import os
import numpy as np
import uvicorn
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from openai import OpenAI
from PIL import Image
import base64
import io
from sentence_transformers.util import cos_sim

app = FastAPI()

# === Load backend DB ===
data = np.load("compressed_embeddings_combined3.npz", allow_pickle=True)
stored_embeddings = data["embeddings"].astype(np.float32)
stored_embeddings = torch.tensor(stored_embeddings)
stored_texts = data['texts']
metadata = data.get('metadata', [{}] * len(stored_texts))

# === OpenAI Client Setup ===
api_key = os.getenv("AIPIPE_TOKEN")
if not api_key:
    raise ValueError("Missing AIPIPE_TOKEN environment variable")

client = OpenAI(
    api_key=api_key,
    base_url="https://aipipe.org/openai/v1"
)

# === Helper Functions ===
def embed_text(text: str, model="text-embedding-3-small"):
    response = client.embeddings.create(input=[text], model=model)
    return np.array(response.data[0].embedding)

def get_image_description(image_b64: str) -> str:
    image_data = base64.b64decode(image_b64)
    image = Image.open(io.BytesIO(image_data))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": "Describe the content of this image in detail."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
            ]}
        ]
    )
    return response.choices[0].message.content

def construct_url(meta):
    source = meta.get("source")
    info = meta.get("url_info")

    if source == "tdscourse":
        # info is a string like "wikipedia-data-with-python"
        return f"https://tds.s-anand.net/#/{info}"

    elif source == "discourse":
        # info is a tuple: (topic_slug, topic_id, post_number)
        if isinstance(info, (tuple, list)) and len(info) == 3:
            topic_slug, topic_id, post_number = info
            return f"https://discourse.onlinedegree.iitm.ac.in/t/{topic_slug}/{topic_id}/{post_number}"

    return ""

def find_top_k_similar(query_embedding, k=10):
    scores = cos_sim(query_embedding, stored_embeddings)[0].numpy()
    top_indices = np.argsort(scores)[-k:][::-1]
    results = []
    for idx in top_indices:
        results.append({
            "score": float(scores[idx]),
            "text": stored_texts[idx],
            "metadata": metadata[idx]
        })
    return results

# === API Schema ===
class LinkOut(BaseModel):
    url: str
    text: str

class AnswerOut(BaseModel):
    answer: str
    links: List[LinkOut]

class QuestionIn(BaseModel):
    question: str
    images: Optional[List[str]] = None

# === Endpoint ===
@app.post("/api/", response_model=AnswerOut)
def ask_question(payload: QuestionIn):
    combined_text = payload.question
    if payload.images:
        for b64_image in payload.images:
            description = get_image_description(b64_image)
            combined_text += "\n" + description

    embedding_np = embed_text(combined_text)
    query_embedding = torch.tensor(embedding_np, dtype=torch.float32)
    top_chunks = find_top_k_similar(query_embedding, k=10)
    retrieved_context = "\n---\n".join([chunk['text'] for chunk in top_chunks])

    system_prompt = "You are a helpful assistant for answering course-related questions. Use the context provided."
    user_prompt = f"Context:\n{retrieved_context}\n\nQuestion:\n{payload.question}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    answer = response.choices[0].message.content

    # Construct links
    links = []
    for chunk in top_chunks[:2]:
        meta = chunk.get("metadata", {})
        url = construct_url(meta)
        if url:
            links.append({"url": url, "text": chunk['text'][:80]})

    return {"answer": answer, "links": links}
