#!/usr/bin/env python3
"""
Generate Analysis - Uses GPT-4 to create insights from data
"""

import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_analysis(data_point):
    """
    Generate a 2-sentence analysis of the data
    
    Args:
        data_point: Dict with 'title', 'data', 'source'
    
    Returns:
        String with analysis
    """
    
    # Extract key metrics
    title = data_point['title']
    values = data_point['data']['values']
    latest = values[-1]
    previous = values[-2] if len(values) > 1 else latest
    change = latest - previous
    
    # Create prompt for GPT
    prompt = f"""You are an economic data analyst. Analyze this data briefly.

Data: {title}
Latest value: {latest}
Previous value: {previous}
Change: {change:+.1f}

Write exactly 2 sentences:
1. State what happened (the change)
2. Explain what this means for everyday people

Keep it simple, conversational, and under 50 words total.
Do NOT use words like "furthermore", "moreover", or "in conclusion".
Sound like a human explaining to a friend."""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Cheaper model
            messages=[
                {"role": "system", "content": "You are a data analyst who explains economics simply."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        analysis = response.choices[0].message.content.strip()
        return analysis
        
    except Exception as e:
        print(f"Error generating analysis: {e}")
        # Fallback to simple template
        direction = "increased" if change > 0 else "decreased"
        return f"{title} {direction} to {latest}%. This could impact consumer spending and economic growth."

if __name__ == "__main__":
    # Test with sample data
    test_data = {
        'title': 'US Inflation Rate',
        'data': {
            'values': [3.4, 3.2, 3.5, 3.4, 3.3, 3.0]
        }
    }
    
    analysis = generate_analysis(test_data)
    print(f"Analysis: {analysis}")
