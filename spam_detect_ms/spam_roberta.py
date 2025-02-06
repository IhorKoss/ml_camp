from transformers import TFAutoModelForSequenceClassification, RobertaTokenizerFast, TextClassificationPipeline
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

loaded_model = TFAutoModelForSequenceClassification.from_pretrained("coconutsc/roberta_email_sms_spam_classifier")
tokenizer = RobertaTokenizerFast.from_pretrained("roberta-base")

spam_pipeline = TextClassificationPipeline(model=loaded_model, tokenizer=tokenizer,device=0)


def detect_spam(text):
    result = spam_pipeline(text[0].upper() + text[1:])
    label = result[0]['label']
    probability = result[0]['score']
    return {"label": label, "probability": probability}

app = FastAPI(title="Spam Detection Service")

class SpamQuery(BaseModel):
    text: str

class SpamResponse(BaseModel):
    label: str
    probability: float

@app.post("/detect_spam", response_model=SpamResponse)
def detect_spam_endpoint(request: SpamQuery):
    result = detect_spam(request.text)
    return SpamResponse(label=result["label"], probability=result["probability"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)