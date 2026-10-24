# actionable items,decisions,questions

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda,RunnablePassthrough
import os

def get_llm():
    return ChatMistralAI(
        model="ministral-8b-2512",
        temperature=0.2,
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
    )


def build_chain(system_prompt:str):
    llm=get_llm()
    chain=RunnablePassthrough()|RunnableLambda(lambda x:{"text":x})|ChatPromptTemplate.from_messages([
        ("system",system_prompt),
        ("human","{text}")
    ])|llm|StrOutputParser()
    return chain

# there will be 3 system prompts for items,decisions and quesions resp..
# for large videos make chunks same as summarizer task incomplete
def extract_action_items(transcript:str)->str:
    chain=build_chain(
         "You are an expert meeting analyst. From the meeting transcript, "
        "extract all action items. For each provide:\n"
        "- Task description\n"
        "- Owner (who is responsible)\n"
        "- Deadline (if mentioned, else write 'Not specified')\n\n"
        "Format as a numbered list. If none found say 'No action items found.'"
    )
    return chain.invoke(transcript)

def extract_key_decisions(transcript: str) -> str:
    chain = build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all key decisions made. Format as a numbered list. "
        "If none found say 'No key decisions found.'"
    )
    return chain.invoke(transcript)


def extract_questions(transcript: str) -> str:
    chain = build_chain(
        "From the meeting transcript, extract all unresolved questions "
        "or topics needing follow-up. Format as a numbered list. "
        "If none found say 'No open questions found.'"
    )
    return chain.invoke(transcript)
