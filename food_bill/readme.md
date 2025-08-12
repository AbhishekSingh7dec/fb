# Social Support AI Pipeline

## Overview

This project automates the social support application process using a multimodal AI pipeline.

## Components

- **Data Pipeline**: Extracts, validates, and loads data.
- **Agents**: Perform tasks like data extraction, validation, eligibility assessment, and recommendation.
- **Interactive Chat Interface**: Allows users to interact with the system.
- **API Endpoint**: Provides a REST API for application processing.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt

2. Run the Streamlit app:
    streamlit run ui/app.py


3. Run the FastAPI app:

    uvicorn api.app:app --reload



🔧 Installation Instructions

To set up your environment with the required dependencies:

    Create a Virtual Environment (optional but recommended):

python -m venv venv

Activate the Virtual Environment:

    Windows:

        .\venv\Scripts\activate

    macOS/Linux:

        source venv/bin/activate

Install Dependencies:

    pip install -r requirements.txt

✅ Additional Notes

    CrewAI: Ensure you have Python 3.10 or higher installed, as CrewAI requires this version.
    help.crewai.com+1CrewAI+1

    Tesseract OCR: For pytesseract to function correctly, you need to have Tesseract-OCR installed on your system. Installation instructions can be found on the Tesseract GitHub repository.

    Environment Variables: Utilize the .env file to store sensitive information like database credentials and API keys. Ensure you have the python-dotenv package installed to load these variables into your application.


## Solution Architecture

        fb_reimbursement/
        │   .env              # sensitive API keys
        │   main.py           # your CrewAI flow runner
        └───config/
            │   agents.yaml   # agent definitions
            │   tasks.yaml    # task definitions


The architecture integrates multimodal data processing, agent orchestration, and interactive chat interfaces to automate the social support application process.
Components:

1. Data Ingestion & Processing:
        Text: Extract text from application forms, PDFs, resumes, and credit reports. 

        Images: Implement Optical Character Recognition (OCR) using Tesseract or Google Vision API for Emirates ID and other scanned documents.

        Tabular Data: Utilize Pandas to load, manipulate, and validate financial data from bank statements and assets/liabilities Excel files, performing necessary data cleaning and transformation, and ensuring the information meets predefined eligibility criteria.

2. Multimodal Data Processing:
        Text: Utilize NLP models for entity extraction and validation.

        Images: Apply image recognition models for document verification.

        Tabular Data: Use data validation techniques to ensure consistency.

3. Agentic AI Orchestration:
        Agents: Use Crew.AI to coordinate agents
            data_ingestor Agent: Extracts and structures data from various sources.

            evaluator Agent: Assesses eligibility based on predefined criteria.

            recommender Agent: Provides recommendations for support or enablement.

            enablement_advisor Agent: Provides recommendations on skill-development frameworks and private-public upskilling initiatives

        Orchestration Framework: Utilize tools like Crew.AI or LangChain for agent coordination.

4. Interactive Chat Interface:
        Frontend: Developed User-friendly interface for data submission using Streamlit.

        Backend: Powered by FastAPI to handle requests and communicate with agents.

        Chatbot: Integrate a Agentic AI chatbot for support assistance by understanding and processing text, images, and tables..


### Yet to be add

5. Observability & Monitoring

    LangSmith: Monitor agent interactions and performance.

    Logging: Implement structured logging using Loguru or Structlog.

    Metrics: Track application metrics with Prometheus and visualize using Grafana.

6. Documentation & Deployment

    GitHub Repository: Host all code and documentation.

    Deployment:

        Frontend: Deploy Streamlit app on Streamlit Cloud or Heroku.

        Backend: Deploy FastAPI app using Docker and host on AWS EC2 or DigitalOcean.

7. Future Enhancements

    Human-in-the-Loop: Implement a review system for flagged applications.

    Advanced Analytics: Integrate machine learning models for predictive analytics.

    Mobile Application: Develop a mobile app for on-the-go access.

This solution leverages multimodal data processing and interactive chat interactions to create an efficient and user-friendly social support application system. By integrating advanced AI models and agent orchestration, the system aims to automate the application process, reducing manual effort and improving decision-making accuracy.