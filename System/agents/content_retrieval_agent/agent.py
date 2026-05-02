from __future__ import annotations

import logging
from typing import List, Optional

from .tools import file_reader_tool, parser_tool
from tools.content_retrieval_tool import StructuredQuestion

class ContentRetrievalAgent:
    def __init__(self, domain: str = "math", exam_file: Optional[str] = None):
        self.domain = domain
        self.exam_file = exam_file
        self.content: List[str] = []
        self.structured_content: List[StructuredQuestion] = []
        self.logger = logging.getLogger("virtual_tutor")

    def retrieve_content(self) -> List[str]:
        """
        Retrieve exam content (questions, study material) for the specified domain.
        """
        self.logger.info("ContentRetrievalAgent input: domain=%s exam_file=%s", self.domain, self.exam_file)
        self.content = file_reader_tool(self.domain, exam_file=self.exam_file)
        self.logger.info("ContentRetrievalAgent output: raw_blocks=%s", len(self.content))
        return self.content

    def retrieve_structured_content(self) -> List[StructuredQuestion]:
        """
        Retrieve content and convert into structured questions and study notes.
        """
        raw = self.retrieve_content()
        self.structured_content = parser_tool(raw)
        self.logger.info("ContentRetrievalAgent output: structured_items=%s", len(self.structured_content))
        return self.structured_content

    def display_content(self):
        """
        Display the retrieved content.
        """
        if not self.content:
            print("No content retrieved yet.")
        else:
            for item in self.content:
                print(item)