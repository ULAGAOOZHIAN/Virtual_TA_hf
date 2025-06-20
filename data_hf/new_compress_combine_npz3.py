import json				
import numpy as np				
				
# File paths				
file1 = r"C:\Users\ulaga\VSCODE101\my_project\TDS-Project1-Data\chunked_embeddings_discourse.jsonl"				
file2 = r"C:\Users\ulaga\VSCODE101\my_project\TDS-Project1-Data\chunked_embeddings_tdscourse.jsonl"				
output_npz = r"C:\Users\ulaga\VSCODE101\my_project\TDS-Project1-Data\compressed_embeddings_combined3.npz"				
				
				
# Containers				
embeddings = []				
texts = []				
titles = []				
metadata = []				
				
# Helper function to construct metadata				
def build_metadata(obj	 source):			
    if source == "discourse":				
        url_info = obj.get("url_info"	 {})			
        return {				
            "source": "discourse"				
            "url_info": (				
                url_info.get("topic_slug")				
                url_info.get("topic_id")				
                url_info.get("post_number")				
            )				
        }				
    elif source == "tdscourse":				
        return {				
            "source": "tdscourse"				
            "url_info": obj.get("url_suffix")				
        }				
    else:				
        return {				
            "source": source				
            "url_info": None				
        }				
				
# Process each file with source tag				
for file_path	 source in [(file1	 "discourse")	 (file2	 "tdscourse")]:
    with open(file_path	 'r'	 encoding='utf-8') as f:		
        for line in f:				
            obj = json.loads(line)				
            embeddings.append(obj["embedding"])				
            texts.append(obj["text_chunk"])				
            titles.append(obj.get("title"	 ""))			
            metadata.append(build_metadata(obj	 source))			
				
# Save as .npz				
np.savez_compressed(				
    output_npz				
    embeddings=np.array(embeddings	 dtype=np.float32)			
    texts=texts				
    titles=titles				
    metadata=np.array(metadata	 dtype=object)			
)				
				
print(f"? Compressed embeddings saved to: {output_npz}")				
