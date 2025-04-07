#!/usr/bin/env python3
"""
Example demonstrating how to use Google ModelGarden models with the GenAI SDK.

This example shows how to initialize the client with ModelGarden support and
make requests to ModelGarden models.
"""

import os
from google import genai
from google.genai import types
import argparse

def main():
    """Main function demonstrating ModelGarden usage"""
    parser = argparse.ArgumentParser(description='Use Google ModelGarden models with the GenAI SDK')
    parser.add_argument('--project', type=str, help='Google Cloud project ID')
    parser.add_argument('--location', type=str, default='us-central1', 
                        help='Google Cloud location (default: us-central1)')
    parser.add_argument('--model', type=str, default='publishers/meta/models/llama3-8b-instruct',
                       help='ModelGarden model to use (default: publishers/meta/models/llama3-8b-instruct)')
    parser.add_argument('--prompt', type=str, default='Explain quantum computing in simple terms.',
                       help='Prompt to send to the model')
    
    args = parser.parse_args()
    
    # Get project from args or environment variable
    project = args.project or os.environ.get('GOOGLE_CLOUD_PROJECT')
    if not project:
        print("Error: Google Cloud project ID is required.")
        print("Please provide it via --project argument or GOOGLE_CLOUD_PROJECT environment variable.")
        return
    
    # Get location from args or environment variable
    location = args.location or os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
    
    # Create client with ModelGarden support
    print(f"Initializing client with ModelGarden support (project: {project}, location: {location})")
    client = genai.Client(
        modelgarden=True,
        project=project,
        location=location
    )
    
    model = args.model
    print(f"Using ModelGarden model: {model}")
    
    # Create the prompt
    prompt = args.prompt
    print(f"Prompt: {prompt}")
    
    # Generate content using the ModelGarden model
    print("\nGenerating response...")
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=800,
            )
        )
        
        print("\nResponse:")
        print(response.text)
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Make sure you have access to the specified ModelGarden model and that")
        print("your Google Cloud credentials have the necessary permissions.")

if __name__ == "__main__":
    main() 