from typing import Optional

from .tools import fetch_exam_content

class ContentRetrievalAgent:
    def __init__(self, domain="math", exam_file: Optional[str] = None):
        self.domain = domain
        self.exam_file = exam_file
        self.content = None

    def retrieve_content(self):
        """
        Retrieve exam content (questions, study material) for the specified domain.
        """
        self.content = fetch_exam_content(self.domain, exam_file=self.exam_file)
        return self.content

    def display_content(self):
        """
        Display the retrieved content.
        """
        if not self.content:
            print("No content retrieved yet.")
        else:
            for item in self.content:
                print(item)