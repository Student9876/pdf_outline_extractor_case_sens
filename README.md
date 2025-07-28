# Adobe - Connecting the Dots Challenge (Round 1A & 1B)

## Overview

We are excited to be selected for the **"Connecting the Dots"** challenge by Adobe.  
Our system handles both **Round 1A** (PDF outline extraction) and **Round 1B** (Persona-driven document intelligence).

## Round 1A: PDF Outline Extraction

### Problem Statement
Extract the structural hierarchy of a PDF document to enable smarter, contextual document understanding.

### Functional Requirements
- Accept a PDF file (≤ 50 pages)
- Extract:
  - `Title`
  - `Headings` (H1, H2, H3 with `level`, `text`, `page`)

## Round 1B: Persona-Driven Document Intelligence

### Problem Statement
Build a system that acts as an intelligent document analyst, extracting and prioritizing the most relevant sections from a collection of documents based on a specific persona and their job-to-be-done.

### Input Specification
- Document Collection: 3-10 related PDFs
- Persona Definition: Role description with specific expertise and focus areas
- Job-to-be-Done: Concrete task the persona needs to accomplish

### Sample Input Format
```json
{
  "documents": ["doc1.pdf", "doc2.pdf", "doc3.pdf"],
  "persona": "PhD Researcher in Computational Biology",
  "job": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
}
```

## How to Build & Run

### Round 1A (Default)
- Place PDFs in `/app/input`
- System automatically processes all PDFs and generates corresponding `.json` outputs in `/app/output`

### Round 1B (Persona-driven)
- Place PDFs and `input.json` (with persona and job specification) in `/app/input`
- System detects `input.json` and runs persona-driven analysis
- Generates `challenge1b_output.json` in `/app/output`

## Tech Stack

- Python (core logic)
- PyMuPDF (PDF parsing)
- Pytesseract (OCR fallback)
- Docker for containerization

## Status

- ✅ Round 1A: PDF outline extraction completed
- ✅ Round 1B: Persona-driven document intelligence implemented
- 📄 Both rounds integrated into unified system