# AI Prompt Submitter

A tool for submitting custom prompts to various AI APIs (xAI and Google Gemini) and storing the responses in a structured format.

## Overview

This project allows you to:
- Store custom prompts as text files
- Submit prompts to the xAI API (using Grok-3-beta model)
- Submit prompts to the Google Gemini API
- Save responses as markdown files with metadata
- Track submission history

## Project Structure

```
ai_prompt_submitter/
├── prompts/            # Directory for prompt text files
│   └── sample_prompt.txt
├── reports/            # Directory for AI response markdown files
├── xai_prompt_submitter.py  # Main script for xAI API
├── gemini_api.py       # Script for Google Gemini API
├── .env.example        # Example environment variables file
└── README.md
```

## Requirements

- Python 3.9+
- OpenAI Python library
- httpx
- python-dotenv
- google-genai

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

The script requires API keys. Set them in your environment or in a `.env` file in your project directory:

```
XAI_API_KEY=your_xai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

## Usage

### xAI API Usage

Run the script without arguments to select from available prompts:

```bash
python xai_prompt_submitter.py
```

Submit a specific prompt by name (without the .txt extension):

```bash
python xai_prompt_submitter.py --prompt sample_prompt
```

Specify a custom output file:

```bash
python xai_prompt_submitter.py --prompt sample_prompt --output custom_output.md
```

### Gemini API Usage

Run the Gemini API script:

```bash
python gemini_api.py
```

## Creating Prompts

Create prompt files in the `prompts/` directory with a `.txt` extension. The content of the file will be sent directly to the AI API.

## Output Format

Responses are saved as markdown files in the `reports/` directory with the following format:

```
---
prompt: prompt_name
submitted_at: YYYY-MM-DD HH:MM:SS
---

[AI response content]
```

## License

MIT
