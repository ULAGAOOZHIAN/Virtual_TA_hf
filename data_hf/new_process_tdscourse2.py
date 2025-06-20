import os		
import json		
from bs4 import BeautifulSoup		
import markdown		
		
md_folder = r"C:\Users\ulaga\VSCODE101\my_project\TDS-Project1-Data\tds_pages_md"		
output_file = r"C:\Users\ulaga\VSCODE101\my_project\TDS-Project1-Data\processed_tdscourse.jsonl"		
		
def extract_markdown_content(file_path):		
    with open(file_path, "r", encoding="utf-8") as f:		
        lines = f.readlines()		
		
    if len(lines) < 4:		
        print(f"Skipping {file_path} - not enough lines")		
        return None		
		
    title = lines[0].strip()		
    original_url = lines[1].strip()		
		
    # Remove root from URL		
    original_url = original_url.replace("https://tds.s-anand.net/#", "").strip()		
		
    # Skip downloaded_at and repeated title		
    content = "".join(lines[3:]).strip()		
		
    # Remove footer navigation links (if present)		
    if "[Previous" in content:		
        content = content.split("[Previous")[0].strip()		
		
    # Convert to plain text via HTML parsing		
    html = markdown.markdown(content)		
    soup = BeautifulSoup(html, "html.parser")		
    clean_text = soup.get_text(separator="\n", strip=True)		
		
    return {		
        "original_url": original_url,		
        "title": title,		
        "content": clean_text		
    }		
		
def main():		
    with open(output_file, "w", encoding="utf-8") as outfile:		
        for filename in os.listdir(md_folder):		
            if filename.endswith(".md"):		
                file_path = os.path.join(md_folder, filename)		
                result = extract_markdown_content(file_path)		
                if result:		
                    json.dump(result, outfile, ensure_ascii=False)		
                    outfile.write("\n")		
		
    print(f"✅ Cleaned content saved to {output_file}")		
		
if __name__ == "__main__":		
    main()		
