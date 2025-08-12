# Install dependencies:
# pip install crewai pdfplumber pytesseract pdf2image pydantic

from crewai import Agent, Task, Crew, Process
from crewai.flow import Flow, start, listen, router
import pdfplumber, pytesseract
from PIL import Image
import re, hashlib
from pydantic import BaseModel

# — Database placeholder —
previous_receipts = set()  # store hashes of processed receipts

class Claim(BaseModel):
    employee_id: str
    employee_name: str
    claimed_amount: float
    date: str  # ISO format
    receipt_file: str  # path or uploaded file

# — Agents —
extract_agent = Agent(
    role="Document Ingestor",
    goal="Extract text from receipts in PDF/image format",
    backstory="Use OCR techniques to convert documents into text",
    verbose=True
)

parse_agent = Agent(
    role="Data Parser",
    goal="Parse extracted text and return merchant, date, amount",
    backstory="Identify key fields using regex and heuristics",
    verbose=True
)

validate_agent = Agent(
    role="Claim Validator",
    goal="Compare parsed data with submitted claim to detect discrepancies",
    backstory="Validate amounts, dates, and employee info; detect duplicates",
    verbose=True
)

notify_agent = Agent(
    role="Notification Agent",
    goal="Inform finance team or employee about validation results",
    backstory="Compose concise messages when discrepancies are found",
    verbose=True
)

# — Flow definition —
class ExpenseValidationFlow(Flow):
    def __init__(self, claim: Claim):
        super().__init__()
        self.state['claim'] = claim
        self.state['extracted_text'] = None
        self.state['parsed_fields'] = None
        self.state['validation_success'] = False

    @start()
    async def ingest_receipt(self):
        claim = self.state['claim']
        file_path = claim.receipt_file
        text = ""
        # Example: handle PDF vs. image
        if file_path.lower().endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        else:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)

        self.state['extracted_text'] = text
        # Return raw text as the result of the task
        return Task(
            description=f"Extracted text from {file_path}",
            agent=extract_agent,
            expected_output=text
        )

    @listen(ingest_receipt)
    async def parse_fields(self, ingestion_result):
        text = self.state['extracted_text']
        # Simple regex patterns; adjust for your receipts
        amount = None
        amount_match = re.search(r'(\$|₹)\s?([0-9]+(?:\.[0-9]{1,2})?)', text)
        if amount_match:
            amount = float(amount_match.group(2))
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
        date = date_match.group(1) if date_match else None
        merchant = None
        # Extract first line as merchant name (placeholder)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            merchant = lines[0]

        parsed = {"amount": amount, "date": date, "merchant": merchant}
        self.state['parsed_fields'] = parsed
        return Task(
            description="Parsed receipt fields",
            agent=parse_agent,
            expected_output=parsed
        )

    @listen(parse_fields)
    async def validate_claim(self, parse_result):
        claim: Claim = self.state['claim']
        parsed = self.state['parsed_fields']
        # Check amount and employee name
        amount_ok = parsed['amount'] is not None and abs(parsed['amount'] - claim.claimed_amount) < 1e-2
        date_ok = parsed['date'] == claim.date
        name_ok = claim.employee_name.lower() in self.state['extracted_text'].lower()
        # Duplicate detection
        # Compute a simple hash of merchant+date+amount
        receipt_key = hashlib.sha256(
            f"{parsed['merchant']}_{parsed['date']}_{parsed['amount']}".encode()
        ).hexdigest()
        duplicate = receipt_key in previous_receipts

        # Check policy (e.g., limit)
        within_limit = parsed['amount'] <= 5000  # example per‑meal limit

        success = amount_ok and date_ok and name_ok and not duplicate and within_limit
        self.state['validation_success'] = success

        if success:
            previous_receipts.add(receipt_key)

        result_desc = (
            "Approved" if success else
            f"Discrepancy found: amount_ok={amount_ok}, date_ok={date_ok}, "
            f"name_ok={name_ok}, duplicate={duplicate}, within_limit={within_limit}"
        )
        return Task(
            description="Validate claim against parsed data",
            agent=validate_agent,
            expected_output=result_desc
        )

    @listen(validate_claim)
    async def notify(self, validation_result):
        success = self.state['validation_success']
        claim = self.state['claim']
        if success:
            message = (
                f"Expense claim for {claim.employee_name} on {claim.date} (₹{claim.claimed_amount}) "
                "has been approved."
            )
        else:
            message = (
                f"Discrepancy detected in claim for {claim.employee_name} on {claim.date}. "
                f"Details: {validation_result.expected_output}"
            )
        return Task(
            description="Send notification",
            agent=notify_agent,
            expected_output=message
        )

# Example usage
# claim = Claim(employee_id="E123", employee_name="Anita Singh",
#               claimed_amount=250.00, date="09/08/2025", receipt_file="/path/to/receipt.pdf")
# flow = ExpenseValidationFlow(claim)
# asyncio.run(flow.start())  # orchestrates ingestion → parsing → validation → notification
