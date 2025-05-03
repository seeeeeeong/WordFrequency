import json
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from googletrans import Translator

app = FastAPI()

with open("final_abuse_db.json", "r", encoding="utf-8") as f:
    abuse_db = json.load(f)

translator = Translator()

def real_retranslation(text: str) -> str:
    try:
        to_english = translator.translate(text, src='ko', dest='en').text
        to_korean = translator.translate(to_english, src='en', dest='ko').text
        return to_korean
    except Exception as e:
        return f"[역번역 오류: {e}]"

class CommentRequest(BaseModel):
    comment: str

def filter_comment(comment: str) -> dict:
    total_score = 0
    method = None
    reason = []
    replacements = {}
    filtered_comment = comment
    words = comment.split()

    for db_word, info in abuse_db.items():
        targets = [db_word] + info.get("variations", [])
        for target in targets:
            if info["type"] == "감정폭발":
                if target in words:
                    total_score += info["score"]
                    reason.append(f"{db_word}({info['type']})")
            else:
                if target in filtered_comment:
                    total_score += info["score"]
                    reason.append(f"{db_word}({info['type']})")
                    replacement = info.get("replacement", "")
                    if replacement:
                        filtered_comment = filtered_comment.replace(target, replacement)
                        replacements[target] = replacement
                    else:
                        filtered_comment = filtered_comment.replace(target, "")
                        replacements[target] = ""

    if total_score >= 8:
        method = "역번역 순화"
        filtered_comment = real_retranslation(filtered_comment)
        replacements["전체 문장"] = "역번역 적용됨"
    elif total_score > 0:
        method = "부분 순화"

    result = {
        "input": comment,
        "filtered": filtered_comment,
        "score": total_score,
        "method": method or "정상",
        "reason": reason,
        "replacements": replacements,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        with open("logs.json", "r", encoding="utf-8") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []

    logs.append(result)
    with open("logs.json", "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    return result

@app.post("/filter")
async def filter_api(request: CommentRequest):
    comment = request.comment
    if not comment:
        raise HTTPException(status_code=400, detail="Bad Request: 'comment' is required.")
    result = filter_comment(comment)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
