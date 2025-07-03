# Resume Optimizer for the Spanish Job Market

This application allows users to upload their resume and paste a job description. It uses Claude AI (Anthropic API) to optimize the resume so it aligns better with the job post.

## Features

- Upload a PDF resume
- Paste a job description
- Generate an optimized resume in Markdown and PDF format
- Download the result
- Suggestions for improving skills, certifications, and projects

## How It Works

1. The app extracts the text from the uploaded PDF resume.
2. It sends the resume and job description to Claude (Anthropic API) with specific instructions to optimize the content.
3. Claude returns a rewritten resume in Markdown format.
4. The app displays the result and provides download options in Markdown or PDF.

## Requirements

- requirements.txt
- An Claude API KEY 

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
