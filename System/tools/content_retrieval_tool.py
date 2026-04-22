import os

def fetch_exam_content(domain):
    """
    Fetch exam content (questions, past papers) based on the subject/domain.
    """
    content_dir = f"content/{domain}"
    content = []

    if not os.path.exists(content_dir):
        print(f"No content found for {domain}.")
        return content

    for filename in os.listdir(content_dir):
        if filename.endswith(".txt"):
            with open(os.path.join(content_dir, filename), 'r') as file:
                content.append(file.read())
    
    return content