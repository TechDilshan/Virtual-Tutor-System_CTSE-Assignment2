import os
from .tools import fetch_exam_content

class ContentRetrievalAgent:
    def __init__(self, domain="math"):
        self.domain = domain
        self.content = None

    def retrieve_content(self):
        """
        Retrieve exam content (questions, study material) for the specified domain.
        """
        print(f"Retrieving content for {self.domain}...")
        self.content = fetch_exam_content(self.domain)
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