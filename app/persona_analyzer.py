# filepath: c:\Repos\pdf_outline_extractor\app\persona_analyzer.py

import os
import json
import fitz
from datetime import datetime
from typing import List, Dict, Any
import re
from collections import Counter

class PersonaAnalyzer:
    def __init__(self):
        self.keyword_weights = {
            'methodology': 0.9,
            'method': 0.8,
            'approach': 0.7,
            'dataset': 0.8,
            'data': 0.6,
            'performance': 0.8,
            'benchmark': 0.8,
            'result': 0.7,
            'evaluation': 0.7,
            'analysis': 0.6,
            'revenue': 0.9,
            'financial': 0.8,
            'investment': 0.8,
            'market': 0.7,
            'strategy': 0.7,
            'concept': 0.8,
            'mechanism': 0.8,
            'reaction': 0.7,
            'kinetics': 0.8,
            'theory': 0.6,
        }

    def extract_text_blocks(self, pdf_path: str) -> List[Dict]:
        """Extract text blocks with metadata from PDF"""
        doc = fitz.open(pdf_path)
        blocks = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Get text blocks
            text_dict = page.get_text("dict")
            for block in text_dict["blocks"]:
                if "lines" in block:
                    block_text = ""
                    for line in block["lines"]:
                        for span in line["spans"]:
                            block_text += span["text"] + " "
                    
                    if block_text.strip():
                        blocks.append({
                            "text": block_text.strip(),
                            "page": page_num + 1,
                            "bbox": block["bbox"]
                        })
        
        doc.close()
        return blocks

    def score_relevance(self, text: str, persona: str, job: str) -> float:
        """Score text relevance based on persona and job requirements"""
        text_lower = text.lower()
        persona_lower = persona.lower()
        job_lower = job.lower()
        
        score = 0.0
        
        # Check for direct keyword matches from job description
        job_keywords = re.findall(r'\b\w+\b', job_lower)
        for keyword in job_keywords:
            if len(keyword) > 3 and keyword in text_lower:
                score += 0.3
        
        # Check for persona-related terms
        persona_keywords = re.findall(r'\b\w+\b', persona_lower)
        for keyword in persona_keywords:
            if len(keyword) > 3 and keyword in text_lower:
                score += 0.2
        
        # Check for weighted keywords
        for keyword, weight in self.keyword_weights.items():
            if keyword in text_lower:
                score += weight
        
        # Boost score for longer, substantive text
        if len(text) > 200:
            score += 0.5
        
        return min(score, 10.0)  # Cap at 10

    def extract_sections(self, documents: List[str], persona: str, job: str) -> Dict[str, Any]:
        """Extract and rank relevant sections from documents"""
        all_sections = []
        
        for doc_path in documents:
            doc_name = os.path.basename(doc_path)
            blocks = self.extract_text_blocks(doc_path)
            
            for block in blocks:
                if len(block["text"]) > 50:  # Filter out very short blocks
                    relevance_score = self.score_relevance(block["text"], persona, job)
                    
                    all_sections.append({
                        "document": doc_name,
                        "page_number": block["page"],
                        "section_title": self.generate_section_title(block["text"]),
                        "content": block["text"],
                        "relevance_score": relevance_score
                    })
        
        # Sort by relevance score
        all_sections.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Take top 10-15 sections
        top_sections = all_sections[:15]
        
        # Assign importance ranks
        for i, section in enumerate(top_sections):
            section["importance_rank"] = i + 1
        
        return top_sections

    def generate_section_title(self, text: str) -> str:
        """Generate a concise section title from text content"""
        sentences = text.split('.')
        if sentences:
            first_sentence = sentences[0].strip()
            if len(first_sentence) > 80:
                first_sentence = first_sentence[:77] + "..."
            return first_sentence
        return text[:80] + "..." if len(text) > 80 else text

    def extract_subsections(self, sections: List[Dict]) -> List[Dict]:
        """Extract and refine subsections from top sections"""
        subsections = []
        
        for section in sections[:10]:  # Process top 10 sections
            text = section["content"]
            
            # Split into logical subsections (sentences or paragraphs)
            parts = []
            if '\n\n' in text:
                parts = text.split('\n\n')
            else:
                sentences = text.split('. ')
                # Group sentences into chunks of 2-3
                for i in range(0, len(sentences), 3):
                    chunk = '. '.join(sentences[i:i+3])
                    if chunk:
                        parts.append(chunk)
            
            for i, part in enumerate(parts):
                if len(part.strip()) > 30:
                    subsections.append({
                        "document": section["document"],
                        "page_number": section["page_number"],
                        "subsection_title": f"Subsection {i+1} - {section['section_title'][:30]}...",
                        "refined_text": part.strip()[:500] + "..." if len(part) > 500 else part.strip()
                    })
        
        return subsections[:20]  # Limit to top 20 subsections

    def analyze_documents(self, input_data: Dict) -> Dict[str, Any]:
        """Main analysis function"""
        documents = input_data["documents"]
        persona = input_data["persona"]
        job = input_data["job"]
        
        # Extract and rank sections
        sections = self.extract_sections(documents, persona, job)
        
        # Extract subsections
        subsections = self.extract_subsections(sections)
        
        # Build output
        output = {
            "metadata": {
                "input_documents": [os.path.basename(doc) for doc in documents],
                "persona": persona,
                "job_to_be_done": job,
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": [
                {
                    "document": section["document"],
                    "page_number": section["page_number"],
                    "section_title": section["section_title"],
                    "importance_rank": section["importance_rank"]
                }
                for section in sections
            ],
            "subsection_analysis": [
                {
                    "document": sub["document"],
                    "page_number": sub["page_number"],
                    "subsection_title": sub["subsection_title"],
                    "refined_text": sub["refined_text"]
                }
                for sub in subsections
            ]
        }
        
        return output