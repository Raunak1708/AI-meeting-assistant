from dotenv import load_dotenv
load_dotenv()

from core.transcriber import transcribe_all
from utils.audio_processing import process_input
from core.extractor import extract_action_items,extract_key_decisions,extract_questions
from core.summarize import summarize,generate_title
print("All things imported")

# import os

source="https://www.youtube.com/watch?v=9LfJq4xXifg"
language="english"

chunks=process_input(source)
transcript=transcribe_all(chunks,language=language)


print("-----------------------Summary-----------------------------")
print(summarize(transcript))
print("-"*50)

print("-----------------------Actionable objects-----------------------------")
print(extract_action_items(transcript))
print("-"*50)

print("-----------------------Key decisions-----------------------------")
print(extract_key_decisions(transcript))
print("-"*50)

print("-----------------------Questions-----------------------------")
print(extract_questions(transcript))
print("-"*50)
