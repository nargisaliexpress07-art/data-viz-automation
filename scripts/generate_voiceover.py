#!/usr/bin/env python3
"""
Generate Voiceover - Uses Edge-TTS to create audio
"""

import asyncio
import edge_tts
import os

async def generate_voiceover(text, output_file, voice="en-US-AndrewNeural"):
    """
    Generate voiceover from text
    
    Args:
        text: String to convert to speech
        output_file: Path to save MP3
        voice: Edge-TTS voice model
    """
    
    # Adjust speech rate and pitch for more natural sound
    rate = "-5%"  # Slightly slower (more authoritative)
    pitch = "-2Hz"  # Slightly lower pitch
    
    communicate = edge_tts.Communicate(
        text, 
        voice,
        rate=rate,
        pitch=pitch
    )
    
    await communicate.save(output_file)
    print(f"✅ Voiceover saved: {output_file}")

def create_voiceover(text, output_file):
    """Synchronous wrapper for async function"""
    asyncio.run(generate_voiceover(text, output_file))

if __name__ == "__main__":
    # Test
    test_text = "The US inflation rate dropped to 3.0% in June, the lowest level since 2021. This could signal that the Federal Reserve's interest rate hikes are working."
    create_voiceover(test_text, "test_voiceover.mp3")
    print("Test complete!")
