from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import PyPDF2
import os
import json
from dotenv import load_dotenv

load_dotenv()

# ============ GROQ API SETUP ============
from groq import Groq

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print("✅ Using Groq API (FREE & FAST)")

# ============ SQLITE DATABASE SETUP ============
os.makedirs("./data", exist_ok=True)
DATABASE_URL = "sqlite:///./data/contracts.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============ DATABASE MODELS ============
class Contract(Base):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="pending")
    file_path = Column(String(500))
    analysis = relationship("AnalysisResult", back_populates="contract", uselist=False)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    parties = Column(Text)
    contract_value = Column(String(100))
    start_date = Column(String(50))
    end_date = Column(String(50))
    key_terms = Column(Text)
    risks = Column(Text)
    risk_score = Column(Float)
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    contract = relationship("Contract", back_populates="analysis")

# Auto-create tables
Base.metadata.create_all(bind=engine)

# ============ FASTAPI APP SETUP ============
app = FastAPI(title="Contract Analysis API - Powered by Groq")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ HELPER FUNCTIONS ============
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")
    return text

def analyze_with_groq(text: str) -> dict:
    """Analyze contract using Groq AI (Llama 3.1)"""
    prompt = f"""Analyze this construction contract and extract the following information:

1. Parties involved (Client and Contractor names)
2. Contract value (total amount)
3. Start date and End date
4. Key terms (3-5 important clauses)
5. Potential risks (identify 2-3 risks with severity: low/medium/high)

Contract text:
{text[:4000]}

You must return ONLY valid JSON in this exact format (no markdown, no extra text):
{{
    "parties": "Client: [name], Contractor: [name]",
    "contract_value": "₹X,XX,XX,XXX or $X,XXX,XXX",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "key_terms": ["term1", "term2", "term3"],
    "risks": [
        {{"description": "risk description", "severity": "high"}},
        {{"description": "risk description", "severity": "medium"}}
    ]
}}"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Extract JSON from response
        content = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        result = json.loads(content.strip())
        
        # Calculate risk score
        risk_score = sum(
            3 if r["severity"] == "high" else 2 if r["severity"] == "medium" else 1
            for r in result.get("risks", [])
        )
        result["risk_score"] = min(risk_score, 10)
        
        return result
    except json.JSONDecodeError as e:
        # Fallback with basic analysis
        print(f"JSON parsing failed: {e}")
        return {
            "parties": "Client: [Not clearly specified], Contractor: [Not clearly specified]",
            "contract_value": "Not specified",
            "start_date": "Not specified",
            "end_date": "Not specified",
            "key_terms": ["Payment terms mentioned", "Project scope defined", "Timeline specified"],
            "risks": [
                {"description": "Contract details need manual review", "severity": "medium"}
            ],
            "risk_score": 5.0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq AI analysis failed: {str(e)}")

# ============ API ENDPOINTS ============
@app.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    """Upload and analyze contract"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    # Save file
    file_path = f"./uploads/{file.filename}"
    os.makedirs("./uploads", exist_ok=True)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Create DB entry
    db = SessionLocal()
    contract = Contract(filename=file.filename, file_path=file_path, status="analyzing")
    db.add(contract)
    db.commit()
    db.refresh(contract)
    
    try:
        # Extract and analyze
        text = extract_text_from_pdf(file_path)
        analysis = analyze_with_groq(text)
        
        # Save analysis
        result = AnalysisResult(
            contract_id=contract.id,
            parties=analysis["parties"],
            contract_value=analysis["contract_value"],
            start_date=analysis["start_date"],
            end_date=analysis["end_date"],
            key_terms=json.dumps(analysis["key_terms"]),
            risks=json.dumps(analysis["risks"]),
            risk_score=analysis["risk_score"]
        )
        db.add(result)
        contract.status = "completed"
        db.commit()
        
        return {"contract_id": contract.id, "status": "success"}
    
    except Exception as e:
        contract.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/contracts")
async def get_contracts():
    """Get all contracts"""
    db = SessionLocal()
    contracts = db.query(Contract).all()
    db.close()
    
    return [
        {
            "id": c.id,
            "filename": c.filename,
            "upload_date": c.upload_date.isoformat(),
            "status": c.status
        }
        for c in contracts
    ]

@app.get("/contracts/{contract_id}")
async def get_contract_analysis(contract_id: int):
    """Get contract analysis"""
    db = SessionLocal()
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    analysis = contract.analysis
    
    result = {
        "contract": {
            "id": contract.id,
            "filename": contract.filename,
            "upload_date": contract.upload_date.isoformat(),
            "status": contract.status
        },
        "analysis": None
    }
    
    if analysis:
        result["analysis"] = {
            "parties": analysis.parties,
            "contract_value": analysis.contract_value,
            "start_date": analysis.start_date,
            "end_date": analysis.end_date,
            "key_terms": json.loads(analysis.key_terms),
            "risks": json.loads(analysis.risks),
            "risk_score": analysis.risk_score,
            "analyzed_at": analysis.analyzed_at.isoformat()
        }
    
    db.close()
    return result

@app.get("/")
async def root():
    return {
        "message": "Contract Analysis API", 
        "status": "running",
        "ai_provider": "Groq (Llama 3.1 70B)",
        "version": "1.0"
    }

# ============ RUN SERVER ============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)