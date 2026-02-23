## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai.tools import tool
from crewai_tools import SerperDevTool

## Creating search tool
search_tool = SerperDevTool()

## Creating custom pdf reader tool using @tool decorator
@tool("Financial Document Reader")
def read_financial_document(file_path: str = 'data/TSLA-Q2-2025-Update.pdf') -> str:
    """Reads and extracts text content from a financial PDF document.

    Args:
        file_path: Path to the PDF file to read. Defaults to 'data/TSLA-Q2-2025-Update.pdf'.

    Returns:
        The full text content extracted from the PDF document.
    """
    from langchain_community.document_loaders import PyPDFLoader

    loader = PyPDFLoader(file_path=file_path)
    docs = loader.load()

    full_report = ""
    for data in docs:
        # Clean and format the financial document data
        content = data.page_content

        # Remove extra whitespace and format properly
        while "\n\n" in content:
            content = content.replace("\n\n", "\n")

        full_report += content + "\n"

    return full_report