from dotenv import load_dotenv
load_dotenv(verbose=True)
from gpt import chat_completion
import os, pathlib

NO_ANSWER = "ANSWER_NOT_FOUND"

def generate_questions(text: str, n: int):
    res = chat_completion([{
        "role": "user",
        "content": "\n".join([
            f"以下の文章に書かれている内容が答えになる質問を最大で{n}個、箇条書きで書いてください。各項目の前にはハイフン(-)をつけてください。",
            f"質問の答えは文章中に書かれている内容でなければなりません。派生する質問があっても書かないでください。",
            "質問がない場合には無理に質問を作らないでください。",
            "",
            "フォーマット:",
            "- 質問1",
            "- 質問2",
            ""
            f"{text}"
        ])
    }])
    lines = res.split("\n")
    prefix = "- "
    qs = [ln[len(prefix):] if ln.startswith(prefix) else ln for ln in lines]
    return qs

def find_answer(q:str, source: str):
    answer = chat_completion([{
        "role": "user",
        "content": "\n".join([
            f"以下の文章を解釈して質問に答えてください。答えが文章中に見つからなかった場合には、「{NO_ANSWER}」とだけ答えてください。",
            f"あなたが答えを知っていても、文章中に書かれていなければ「{NO_ANSWER}」とだけ答えてください。",
            f"「{NO_ANSWER}」と答える場合にはそれ以外の文字は書かないでください。",
            "",
            f"質問: {q}",
            "",
            f"回答を探す文章: {source}",
            "",
            "回答:"
        ])
    }])
    return None if NO_ANSWER in answer else answer

def validate_answer(text: str, source: str):
    answer = chat_completion([{
        "role": "system",
        "content": "You just read the text and answer the question. Please do not include what you know."
    },
    {
        "role": "user",
        "content": "\n".join([
            f"以下の文章を解釈して、「{text}」という内容が書かれている場合には、「YES」それ以外には「NO」とだけ答えてください。",
            "",
            f"文章: {source}",
        ])
    }])
    return answer == "YES"

def generate_qa(text: str, n: int):
    qa_pairs = []
    questions = generate_questions(text, n)
    for q in questions:
        a = find_answer(q, text)
        if a is not None:
            included = validate_answer(a, text)
            if included:
                qa_pairs.append((q, a))
    return qa_pairs

GPT4_DOC = pathlib.Path(os.path.dirname(__file__)).joinpath("../docs/gpt-4.txt")
APE_DOC = pathlib.Path(os.path.dirname(__file__)).joinpath("../docs/ape.txt")
MEETING_DOC = pathlib.Path(os.path.dirname(__file__)).joinpath("../docs/meeting_notes.txt")

if __name__ == "__main__":
  n = 10
  doc_path = MEETING_DOC
  with open(doc_path, "r", encoding="utf-8") as f:
      text = f.read()
      qas = generate_qa(text, n) 
      for p in qas:
        print(f"Q: {p[0]}")
        print(f"A: {p[1]}")
        print("====================")