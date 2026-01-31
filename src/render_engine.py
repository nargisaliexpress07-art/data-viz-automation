import json
import glob
import os
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Configuration
QUEUE_DIR = "data/render_queue"
OUTPUT_DIR = "output"
VOICE_DIR = "outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def sanitize_text(text):
    """Clean text for FFmpeg drawtext filter"""
    return text.replace("'", "").replace(":", "-").replace("\n", " ")

def render_video(config_path):
    with open(config_path, 'r') as f:
        job = json.load(f)

    video_id = job['id']
    print(f"Processing {video_id}: {job['title']}")

    # 1. Prepare Data
    df = pd.DataFrame({
        'Label': job['data']['labels'],
        'Value': job['data']['values']
    })

    # 2. Setup Figure (9:16 aspect ratio for Shorts)
    fig, ax = plt.subplots(figsize=(9, 16), dpi=100)
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')
    
    # Style Chart
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.set_title(job['title'], color='white', fontsize=24, pad=20)

    # 3. Animation Function
    line, = ax.plot([], [], color='#00ff88', linewidth=4)
    
    def init():
        ax.set_xlim(0, len(df))
        ax.set_ylim(min(df['Value']) * 0.99, max(df['Value']) * 1.01)
        return line,

    def update(frame):
        x = range(frame)
        y = df['Value'][:frame]
        line.set_data(x, y)
        return line,

    # 4. Generate Animation (Slower: 15 FPS instead of 30)
    frames = len(df)
    anim = FuncAnimation(fig, update, init_func=init, frames=frames, interval=50)
    
    temp_video = f"{OUTPUT_DIR}/temp_{video_id}.mp4"
    # Saving at 15 FPS makes the "drawing" phase last twice as long
    anim.save(temp_video, writer='ffmpeg', fps=15, codec='libx264')
    plt.close()

    # 5. Merge Audio & Freeze Final Frame
    final_output = f"{OUTPUT_DIR}/final_{video_id}.mp4"
    voice_file = f"{VOICE_DIR}/voiceover_{video_id}.mp3"
    
    clean_analysis = sanitize_text(job['analysis'])
    
    # COMPLEX FFMPEG COMMAND EXPLAINED:
    # [0:v]tpad=stop_mode=clone:stop_duration=60 : Takes the video and "clones" the last frame for 60 seconds
    # drawtext : Draws the text on top of this extended video
    # -shortest : Cuts the video exactly when the audio finishes
    
    cmd = [
        'ffmpeg', '-y',
        '-i', temp_video,
        '-i', voice_file,
        '-filter_complex', 
        f"[0:v]tpad=stop_mode=clone:stop_duration=60[v_ext];[v_ext]drawtext=text='{clean_analysis}':fontcolor=white:fontsize=34:x=(w-text_w)/2:y=h-200:box=1:boxcolor=black@0.5[v_final]",
        '-map', '[v_final]',
        '-map', '1:a',
        '-c:v', 'libx264', '-c:a', 'aac',
        '-shortest',
        final_output
    ]
    
    subprocess.run(cmd, check=True)
    os.remove(temp_video)
    print(f"Rendered: {final_output}")

# Main Loop
files = glob.glob(f"{QUEUE_DIR}/*.json")
for file in files:
    try:
        render_video(file)
    except Exception as e:
        print(f"Failed to render {file}: {e}")
