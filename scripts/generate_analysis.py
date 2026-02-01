#!/usr/bin/env python3
"""
Generate Analysis - Creates comparison-style scripts
"""

import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_analysis(data_point):
    """
    Generate news-style comparison script
    
    Args:
        data_point: Dict with 'title', 'data', 'source', 'category'
    
    Returns:
        String with voiceover script
    """
    
    title = data_point['title']
    yesterday = data_point['data']['yesterday']
    today = data_point['data']['today']
    change = data_point['data']['change']
    change_percent = data_point['data']['change_percent']
    category = data_point.get('category', 'market')
    
    direction = "up" if change > 0 else "down"
    
    # Create prompt for comparison-style script
    prompt = f"""You are an economic data analyst.Create a 15-20 second voiceover script for a YouTube Short.

Topic: {title}
Category: {category}
Yesterday: ${yesterday}
Today: ${today}
Change: {change_percent:+.2f}%

Style: News anchor delivering quick market update
Tone: Professional but energetic
Format: 
- Start with attention grabber
- State the comparison (yesterday vs today)
- Quick insight on what it means

Keep it under 40 words. Sound human and excited.
Do NOT use phrases like "Let's dive in" or "Stay tuned"."""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a financial news anchor writing quick market update scripts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=120,
            temperature=0.8
        )
        
        script = response.choices[0].message.content.strip()
        
        # Clean up quotes if any
        script = script.replace('"', '').replace("'", '')
        
        return script
        
    except Exception as e:
        print(f"Error generating analysis: {e}")
        # Fallback template
        if change > 0:
            return f"{title} jumped {abs(change_percent):.1f}% today, moving from ${yesterday} to ${today}. Investors are watching closely as momentum builds."
        else:
            return f"{title} dropped {abs(change_percent):.1f}% today, falling from ${yesterday} to ${today}. Markets react to the latest developments."

if __name__ == "__main__":
    # Test
    test_data = {
        'title': 'Bitcoin Price Update',
        'category': 'crypto',
        'data': {
            'yesterday': 42000,
            'today': 43500,
            'change': 1500,
            'change_percent': 3.57
        }
    }
    
    script = generate_analysis(test_data)
    print(f"Script: {script}")
    print(f"\nWord count: {len(script.split())}")
