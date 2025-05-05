#!/usr/bin/env python3
"""
Gemini API Prompt Submitter
Submits custom prompts to Google Gemini API and saves the responses as markdown files.
"""
import os
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import argparse
import sys

from google import genai

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file in project folder
load_dotenv()

PROMPTS_DIR = "prompts"
REPORTS_DIR = "reports"

class GeminiPromptSubmitter:
    def __init__(self, api_key: str = None):
        """Initialize with Gemini API key."""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            logger.error("GEMINI_API_KEY not found in environment variables or .env file.")
            self.client = None
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Gemini API client initialized successfully.")
            except Exception as e:
                logger.error(f"Error initializing Gemini API client: {str(e)}")
                self.client = None

    def read_prompt(self, prompt_file: Path) -> str:
        """Read the prompt from a text file."""
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()

    def submit_prompt(self, prompt: str, model: str = "gemini-2.5-flash-preview-04-17") -> str:
        """Submit the prompt to Gemini API and get the response."""
        logger.info(f"Submitting prompt to Gemini. Prompt length: {len(prompt)}. Model: {model}")
        
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model=model, 
                    contents=prompt
                )
                logger.info("Gemini submission complete. Response received.")
                logger.debug(f"Gemini response preview: {response.text[:200]}")
                return response.text
            except Exception as e:
                logger.error(f"Error calling Gemini API: {str(e)}")
                return f"# Gemini API Error\n\n```\n{str(e)}\n```"
        else:
            logger.info("[SIMULATION] Would send prompt to Gemini here...")
            # Simulate a response
            return "# Gemini Response (Simulation)\n\nThis is a simulated response because the Gemini API client was not available."

    def save_response(self, response: str, output_file: Path, prompt_name: str, submission_time: str):
        """Save the Gemini response to a markdown file."""
        try:
            # Add metadata to the top of the file
            metadata = (
                f"---\n"
                f"prompt: {prompt_name}\n"
                f"submitted_at: {submission_time}\n"
                f"model: gemini-2.5-flash-preview-04-17\n"
                f"---\n\n"
            )
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(metadata + response)
                
            logger.info(f"Response saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving response: {str(e)}")

def find_prompt_file(prompt_name: str = None) -> Path:
    """Find a prompt file by name or list available prompts if none specified."""
    prompts_dir = Path(PROMPTS_DIR)
    
    if not prompt_name:
        # List available prompts
        prompts = list(prompts_dir.glob("*.txt"))
        if not prompts:
            logger.error(f"No prompt files found in {prompts_dir}")
            sys.exit(1)
        
        print("Available prompts:")
        for i, prompt in enumerate(prompts, 1):
            print(f"{i}. {prompt.stem}")
        
        # Ask user to select a prompt
        selection = input("\nEnter prompt number to use: ")
        try:
            selected_idx = int(selection) - 1
            if 0 <= selected_idx < len(prompts):
                return prompts[selected_idx]
            else:
                logger.error("Invalid selection")
                sys.exit(1)
        except ValueError:
            logger.error("Invalid input")
            sys.exit(1)
    else:
        # Find prompt by name
        prompt_file = prompts_dir / f"{prompt_name}.txt"
        if not prompt_file.exists():
            logger.error(f"Prompt file not found: {prompt_file}")
            sys.exit(1)
        return prompt_file

def main():
    parser = argparse.ArgumentParser(description="Gemini Prompt Submitter")
    parser.add_argument('--prompt', type=str, help="Name of the prompt file to use (without .txt extension)")
    parser.add_argument('--output', type=Path, help="Path to the output markdown file (optional)")
    parser.add_argument('--model', type=str, default="gemini-2.5-flash-preview-04-17", 
                        help="Gemini model to use (default: gemini-2.5-flash-preview-04-17)")
    args = parser.parse_args()

    # Find prompt file
    prompt_file = find_prompt_file(args.prompt)
    prompt_name = prompt_file.stem
    
    # Set up output file
    submission_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    reports_dir = Path(REPORTS_DIR)
    os.makedirs(reports_dir, exist_ok=True)
    
    output_file = args.output if args.output else reports_dir / f"gemini_{prompt_name}_{submission_time}.md"

    # Initialize submitter and process prompt
    submitter = GeminiPromptSubmitter()
    prompt = submitter.read_prompt(prompt_file)
    response = submitter.submit_prompt(prompt, model=args.model)
    
    # Save the response
    formatted_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    submitter.save_response(response, output_file, prompt_name, formatted_time)

if __name__ == "__main__":
    main()
