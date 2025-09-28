import pdfplumber
import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional
from textwrap import dedent

load_dotenv()

OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY environment variable not set")

openai_client: OpenAI = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT: str = dedent("""
    You are an expert information extractor. You will be provided with the text content of a potentially verly long document.
    Your task is to identify and extract all relevant events mentioned in the document. An event is defined as any occurrence involving people, organizations, locations, or significant actions that took place at a specific time.
    For each event, extract the following details:
    - Title: A brief, descriptive title of the event.
    - Summary: A concise summary of the event, capturing the key details and context.
    - Date: The date when the event occurred, in YYYY-MM-DD format. If the exact date is not mentioned, provide the closest approximation (e.g., month and year).
    - Location: The specific location or address where the event took place, if available.
    - Entities: A list of people or organizations involved in the event.
    If certain details are not explicitly mentioned in the text, use your best judgment to infer them based on the context provided.
    """).strip()



class Event(BaseModel):
    title: str = Field(..., max_length=200,
                       description="Brief descriptive title of the event")
    summary: str = Field(..., description="Detailed description of the event")
    date: str = Field(..., description="Date of the event in YYYY-MM-DD format",
                      pattern=r"^\d{4}-\d{2}-\d{2}$")
    location: Optional[str] = Field(...,
                                    description="Specific location/address of the event")
    entities: List[str] = Field(
        None, description="List of entities (people/organizations) involved in the event")


class CAT(BaseModel):
    events: List[Event] = Field(default_factory=list)


def extract_text_from_pdf(file_path: str) -> str:
    text: list[str] = []
    with pdfplumber.open(file_path) as pdf:
        text: list[str] = [page.extract_text() for page in pdf.pages]
    return "\n".join(text)


def process_document(file_path: str) -> CAT:
    text = extract_text_from_pdf(file_path)
    response = openai_client.responses.parse(
        model="gpt-5",
        reasoning={
            "effort": "moderate",
        },
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "The text is: " + text + "\n\n======\nExtract the events as per the instructions."}
        ],
        text_format=CAT
    )
    output_parsed = response.output_parsed
    return output_parsed
