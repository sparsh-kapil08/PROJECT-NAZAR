🚀 PROJECT NAZAR
AI-Powered Multi-Intelligence Campus Monitoring & Issue Management Platform

Team Name: TEAM STYLUS
Project: PROJECT NAZAR

📖 Table of Contents

Overview

System Architecture

Intelligence Layer Design

End-to-End Execution Flow

Intelligence Modules (1–5)

API Design

Technology Stack

Scalability & Deployment

Performance Goals

Privacy & Ethics

Future Roadmap

🌍 1. Overview

Project NAZAR is a real-time multi-intelligence computer vision platform that proactively detects and manages physical infrastructure issues across large campuses using camera inputs.

Instead of relying on:

❌ Manual inspection
❌ Complaint-based reporting
❌ Reactive maintenance

NAZAR continuously monitors environments and automatically identifies:

• Water leaks & spills
• Energy wastage
• Waste & litter accumulation
• Broken infrastructure
• Unauthorized room access

The system produces:

✅ Visual evidence
✅ Structured alerts
✅ Severity scoring
✅ API-ready outputs

🏗️ 2. System Architecture
Camera / Image Upload
        ↓
Preprocessing Layer
        ↓
Multi-Intelligence Router
        ↓
┌───────────────┐
│ Energy Model  │
│ Water Model   │
│ Waste Model   │
│ Infra Model   │
│ Access Model  │
└───────────────┘
        ↓
Decision Engine
        ↓
API Response + Evidence Storage
        ↓
Dashboard / Alerts / Analytics


Each intelligence layer operates independently and can be scaled or upgraded without affecting others.

🧠 3. Intelligence Layer Philosophy

Project NAZAR avoids overfitting-heavy deep learning whenever unnecessary.

It combines:

Deep learning where perception is needed (YOLO, MediaPipe)

Classical computer vision where structure matters

Rule-based decision intelligence for explainability

This hybrid approach gives:

✔ Stability
✔ Interpretability
✔ Low compute cost
✔ High real-world robustness

🔄 4. End-to-End Execution Flow

Frame received (CCTV, API upload, snapshot)

Routed to selected intelligence module

Visual analysis performed

Context logic applied

Temporal validation if required

Evidence captured

Structured response returned

⚡ INTELLIGENCE 1 — ENERGY WASTE DETECTION
🎯 Goal

Detect energy consumption in empty spaces.

🧩 Detection Logic

Human presence via MediaPipe pose detection

Light intensity via brightness histogram

Fan motion via frame differencing

Time persistence buffering

🔍 Trigger Condition
No human present
AND lights/fans active
FOR threshold duration
→ Energy waste confirmed

📤 Output
{
  "issue": "energy_waste",
  "duration": 120,
  "status": "confirmed"
}

💧 INTELLIGENCE 2 — WATER LEAKAGE & SPILL DETECTION
🎯 Goal

Detect real water accumulation while rejecting glare, humans, and sunlight.

🧠 Pipeline

Floor-only ROI extraction

HSV-based reflective water signature

Texture shimmer analysis

Shape irregularity checks

Optical flow validation

Temporal persistence buffer

📊 Classification
Condition	Interpretation
Flowing + small area	Indoor leak
Static + large area	Outdoor clog
Expanding	Active spill
📤 Output
{
  "issue": "water_leak",
  "severity": "HIGH",
  "area": 1340
}

🗑️ INTELLIGENCE 3 — WASTE & LITTER DETECTION
🎯 Goal

Detect clutter anywhere and trash inside dustbins.

🧠 Approach

YOLOv8 detects waste objects

Validator filters non-waste shapes

Context awareness checks bin proximity

♻ Supported Classes (expandable)

Plastic bottles

Cups

Cans

Bags

Wrappers

Paper waste

Food containers

📤 Output
{
  "issue": "waste_detected",
  "count": 6,
  "objects": [...]
}

🪑 INTELLIGENCE 4 — BROKEN INFRASTRUCTURE MODEL
🧠 Core Idea

Detect structural abnormality instead of damage types.

⚙️ Detailed Flow
Step 1 — Object Detection

YOLOv8 identifies:

Chairs

Desks

Tables

Step 2 — ROI Cropping

Each object isolated for clean analysis.

Step 3 — Geometry Processing

Grayscale

Blur

Edge detection

Contour extraction

Step 4 — Abnormality Rules

Distorted aspect ratio

Broken shape continuity

Structural collapse

Step 5 — Reporting
{
  "issue": "broken_infrastructure",
  "detections": [...]
}

🏆 Engineering Advantage

✔ No massive dataset required
✔ Works on noisy cameras
✔ Explainable decisions

🚪 INTELLIGENCE 5 — UNAUTHORIZED ROOM ACCESS
🎯 Goal

Detect human presence outside allowed access hours.

🔍 Components
Visual Layer

MediaPipe human presence detection

Context Layer

Time window validation

Decision Layer
Person detected AND time outside allowed → violation

📤 Output
{
  "violation": true,
  "timestamp": "22:41",
  "evidence": "alerts/frame_0021.jpg"
}

🌐 6. API DESIGN

Each intelligence is exposed via FastAPI endpoints:

Endpoint	Function
/energy-detect	Energy waste
/water-detect	Water issues
/waste-detect	Waste & litter
/infra-detect	Broken assets
/access-detect	Unauthorized entry

All endpoints support:

✔ Image uploads
✔ JSON responses
✔ Swagger testing

🛠️ 7. Technology Stack
Vision & ML

OpenCV

YOLOv8

MediaPipe

NumPy

Backend

FastAPI

Python

Frontend

React

HTML/CSS

Cloud

Supabase

📈 8. Scalability

Stateless APIs

Camera-agnostic

Modular intelligence layers

Cloud-ready inference

Supports:

✔ Hundreds of cameras
✔ Snapshot uploads
✔ Mobile integration

🔐 9. Privacy & Ethics

No face recognition

No identity tracking

Event-based evidence only

Time-limited storage

Designed to comply with surveillance best practices.

🚀 10. Future Roadmap

Predictive maintenance

Issue heatmaps

Automated ticket routing

Smart campus analytics

IoT sensor fusion

🎯 Final Vision

Project NAZAR converts raw camera feeds into real-time campus intelligence.

From passive recording → to proactive problem solving.
