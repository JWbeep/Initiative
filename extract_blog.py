import re
import html

def extract_text_from_html(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple extraction: find all text within tags, but specifically the main content area if possible.
        # Naver blog content often resides in 'se-main-container' or similar.
        # But let's just strip all tags for now and see if we get the good stuff.
        # A better regex might be targeting the specific class names I saw earlier: 'se-text-paragraph'
        
        # Pattern for Naver SmartEditor text paragraphs
        # <p class="se-text-paragraph ..."><span>TEXT</span></p>
        
        # Let's try to find text inside <span ... class="... se-ff-nanumgothic ..."> ... </span>
        # or just all spans.
        
        # Regex to find text inside span tags
        span_pattern = re.compile(r'<span[^>]*>(.*?)</span>', re.DOTALL)
        matches = span_pattern.findall(content)
        
        extracted_text = []
        for match in matches:
            # Clean up the match
            clean_text = re.sub(r'<[^>]+>', '', match) # Remove any internal tags
            clean_text = html.unescape(clean_text).strip()
            if clean_text and clean_text != "​": # Skip empty or zero-width space
                extracted_text.append(clean_text)
                
        # Join with newlines
        full_text = '\n'.join(extracted_text)
        
        # Print a preview
        print(f"--- Extracted Text Preview (First 500 chars) ---\n{full_text[:500]}\n...")
        print(f"\n--- Total Length: {len(full_text)} characters ---")
        
        return full_text

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    # Reconfigure stdout to utf-8 if possible
    if sys.version_info >= (3, 7):
        sys.stdout.reconfigure(encoding='utf-8')
    
    text = extract_text_from_html(r"c:\Python Practice\Ollama\temp_blog.html")
    
    output_path = r"c:\Python Practice\Ollama\extracted_blog_content.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"Extraction complete. Saved to {output_path}")
