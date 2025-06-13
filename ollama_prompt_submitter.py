# Script: ollama_prompt_submitter.py
# date_created: 2025-06-02T13:28:49+02:00
# date_modified: 2025-06-13T22:04:58+02:00

"""
Ollama Prompt Submitter
Submits custom prompts to a local Ollama LLM and saves the responses as markdown files.
"""

import os
import logging
from pathlib import Path
from datetime import datetime
import argparse
import sys
import ollama

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROMPTS_DIR = "prompts"
REPORTS_DIR = "reports"
DEFAULT_MODEL = "gemma3:12b-it-q8_0"

class OllamaPromptSubmitter:
    def __init__(self, model: str = None):
        """Initialize with the specified Ollama model."""
        self.model = model or DEFAULT_MODEL
        logger.info(f"Initialized Ollama client with model: {self.model}")
        
        # Check if model is available, pull if not
        try:
            response = ollama.list()
            model_found = False
            
            # Check if the model is in the list of available models
            if 'models' in response and response['models']:
                for model_info in response['models']:
                    # Handle different response formats - check both 'model' and 'name' keys
                    model_name = model_info.get('model') or model_info.get('name', '')
                    if model_name == self.model or model_name.startswith(f"{self.model}:"):
                        model_found = True
                        logger.info(f"Found model: {model_name}")
                        break
            
            if not model_found:
                logger.info(f"Model '{self.model}' not found locally. Attempting to pull...")
                ollama.pull(self.model)
                logger.info(f"Successfully pulled model: {self.model}")
                
        except Exception as e:
            logger.error(f"Error initializing Ollama: {str(e)}")
            logger.error("Make sure the Ollama service is running. You can start it with 'ollama serve'")
            raise

    def read_prompt(self, prompt_file: Path) -> str:
        """Read the prompt from a text file."""
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()

    def submit_prompt(self, prompt: str) -> str:
        """Submit the prompt to the local Ollama model and get the response."""
        logger.info(f"Submitting prompt to Ollama model '{self.model}'. Prompt length: {len(prompt)}")
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={"temperature": 0.5, "num_ctx": 4096}
            )
            logger.info("Ollama generation complete. Response received.")
            return response.get("response", "No response generated.")
            
        except Exception as e:
            error_msg = f"Error calling Ollama API: {str(e)}"
            logger.error(error_msg)
            return f"# Ollama API Error\n\n```\n{error_msg}\n```"

    def save_response(self, response: str, output_file: Path, prompt_name: str, submission_time: str):
        """Save the Ollama response to a markdown file."""
        try:
            # Add metadata to the top of the file
            metadata = (
                f"---\n"
                f"model: {self.model}\n"
                f"prompt: {prompt_name}\n"
                f"submitted_at: {submission_time}\n"
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
    os.makedirs(prompts_dir, exist_ok=True)
    
    if not prompt_name:
        # List available prompts
        prompts = list(prompts_dir.glob("*.txt"))
        if not prompts:
            logger.error(f"No prompt files found in {prompts_dir}")
            print(f"No prompt files found in {prompts_dir}. Please create a prompt file in the 'prompts' directory.")
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
            print(f"Error: Prompt file '{prompt_name}.txt' not found in the 'prompts' directory.")
            sys.exit(1)
        return prompt_file

def main():
    parser = argparse.ArgumentParser(description="Ollama Prompt Submitter")
    parser.add_argument('--prompt', type=str, help="Name of the prompt file to use (without .txt extension)")
    parser.add_argument('--output', type=Path, help="Path to the output markdown file (optional)")
    parser.add_argument('--model', type=str, default=DEFAULT_MODEL, 
                      help=f"Ollama model to use (default: {DEFAULT_MODEL})")
    parser.add_argument('--list-models', action='store_true', help="List available Ollama models and exit")
    
    args = parser.parse_args()
    
    if args.list_models:
        try:
            print("Available Ollama models:")
            response = ollama.list()
            if 'models' in response:
                for model in response['models']:
                    model_name = model.get('name', 'unnamed')
                    model_size = model.get('size', 0)
                    if model_size > 0:
                        model_size = f"{model_size/1024/1024/1024:.1f}GB"
                    else:
                        model_size = "N/A"
                    modified = model.get('modified_at', 'N/A')
                    print(f"- {model_name} (size: {model_size}, modified: {modified})")
            else:
                print("No models found. Try running 'ollama pull <model_name>' first.")
            return
        except Exception as e:
            print(f"Error listing models: {str(e)}")
            print("Make sure the Ollama service is running. You can start it by running 'ollama serve' in a terminal.")
            return

    # Find prompt file
    prompt_file = find_prompt_file(args.prompt)
    prompt_name = prompt_file.stem
    
    # Set up output file
    submission_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    reports_dir = Path(REPORTS_DIR)
    os.makedirs(reports_dir, exist_ok=True)
    
    output_file = args.output if args.output else reports_dir / f"ollama_{prompt_name}_{submission_time}.md"

    # Initialize submitter and process prompt
    try:
        submitter = OllamaPromptSubmitter(model=args.model)
        prompt = submitter.read_prompt(prompt_file)
        response = submitter.submit_prompt(prompt)
        
        # Save the response
        formatted_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        submitter.save_response(response, output_file, prompt_name, formatted_time)
        print(f"\nResponse saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
