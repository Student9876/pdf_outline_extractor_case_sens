# filepath: c:\Repos\pdf_outline_extractor\app\main_1b.py

import os
import json
from persona_analyzer import PersonaAnalyzer

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

def main():
    # Check if input.json exists for Round 1B
    input_file = os.path.join(INPUT_DIR, "input.json")
    
    if os.path.exists(input_file):
        # Round 1B: Persona-driven analysis
        with open(input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)
        
        # Convert relative paths to absolute paths
        documents = []
        for doc_name in input_data["documents"]:
            doc_path = os.path.join(INPUT_DIR, doc_name)
            if os.path.exists(doc_path):
                documents.append(doc_path)
        
        if documents:
            analyzer = PersonaAnalyzer()
            
            analysis_input = {
                "documents": documents,
                "persona": input_data["persona"],
                "job": input_data["job"]
            }
            
            result = analyzer.analyze_documents(analysis_input)
            
            # Save output
            output_file = os.path.join(OUTPUT_DIR, "challenge1b_output.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"Round 1B analysis completed. Output saved to {output_file}")
    else:
        print("No input.json found. Expected format:")
        print({
            "documents": ["doc1.pdf", "doc2.pdf"],
            "persona": "PhD Researcher in Computational Biology",
            "job": "Prepare a comprehensive literature review"
        })

if __name__ == "__main__":
    main()