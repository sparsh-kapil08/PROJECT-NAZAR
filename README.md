PROJECT NAZAR is an automated maintenance system for DTU. It uses a multi-model AI approach to detect campus issues, score severity, and dispatch tickets via Supabase.

🚀 Key Features
Dual-Layer AI: Combines local Computer Vision (FastAPI) with Google Gemini for high-level visual reasoning.

Live Inspection: Real-time camera stream for instant issue detection.

Automated Workflow: Detects, categorizes, and archives tickets in Supabase for maintenance dispatch.

Smart Scoring: Auto-assigns severity (High/Medium/Low) and identifies safety risks.

🛠️ Tech Stack
Frontend: JavaScript (ES6+), Tailwind CSS.

AI: Google Gemini (3 Flash & 2.5 Flash).

Backend: Supabase (PostgreSQL).

ML Engine: Python FastAPI (Local Context).

💻 Setup
Environment: Set API_KEY (Gemini) and Supabase credentials.

ML Engine: Run python -m uvicorn main:app --port 8000.

Frontend: Serve index.html via npx serve.

Install the requirements.txt in ml_engine
