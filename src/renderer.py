import json
import os
import glob
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

def render_professional_video(config_path):
    print(f"🎬 Starting Pro-Render for: {config_path}")
    
    # Load Data
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    video_id = config['id']
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"video_{video_id}.mp4")

    # Data Extraction
    labels = config['data']['labels']
    values = config['data']['values']
    
    # --- AESTHETICS ENGINE ---
    # Resolution: 1080x1920 (9:16 Aspect Ratio)
    # DPI: 120 ensures text is sharp
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(9, 16), dpi=120)
    ax = fig.add_subplot(111)
    
    # Colors (Financial Dark Mode)
    BG_COLOR = '#050505'  # Almost black
    GRID_COLOR = '#333333'
    TEXT_COLOR = '#FFFFFF'
    
    # Dynamic Trend Color
    start_val = values[0]
    end_val = values[-1]
    if end_val >= start_val:
        MAIN_COLOR = '#00ff88' # Neon Green
        FILL_COLOR = '#00ff88'
    else:
        MAIN_COLOR = '#ff4d4d' # Neon Red
        FILL_COLOR = '#ff4d4d'

    # Layout Setup
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    
    # Professional Grid
    ax.grid(True, linestyle=':', alpha=0.3, color=GRID_COLOR)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color(GRID_COLOR)
    
    # Typography
    # Title
    plt.text(0.5, 0.93, config['title'], transform=fig.transFigure, 
             ha='center', va='top', fontsize=28, fontweight='bold', color=TEXT_COLOR, fontfamily='sans-serif')
    
    # Source Citation (Critical for Trust)
    plt.text(0.5, 0.04, f"Source: {config['source']}", transform=fig.transFigure,
             ha='center', fontsize=12, color='#666666', fontstyle='italic')

    # Axis Formatting
    ax.set_xlim(0, len(labels)-1)
    # Add 10% padding to top/bottom so graph doesn't touch edges
    y_range = max(values) - min(values)
    ax.set_ylim(min(values) - (y_range*0.2), max(values) + (y_range*0.2))
    
    # Clean X-Axis
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, color='#AAAAAA', fontsize=10)
    ax.tick_params(axis='y', colors='#AAAAAA')

    # --- ANIMATION LOGIC ---
    line, = ax.plot([], [], color=MAIN_COLOR, linewidth=6, solid_capstyle='round')
    
    # The big number in the center
    val_text = ax.text(0.5, 0.80, "", transform=ax.transAxes, 
                       ha='center', fontsize=60, fontweight='bold', color=MAIN_COLOR)

    def init():
        line.set_data([], [])
        val_text.set_text("")
        return line, val_text

    def animate(i):
        # Smoothly draw the line
        x = range(i+1)
        y = values[:i+1]
        line.set_data(x, y)
        
        # Update the number
        val_text.set_text(f"{values[i]:,.2f}")
        
        return line, val_text

    # --- RENDERING (HIGH QUALITY) ---
    frames = len(values)
    # Slow down animation to make it readable
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=frames, interval=100, blit=True)
    
    print(f"⚙️ Rendering High-Quality Video: {output_file}")
    
    # FFmpeg Settings for YouTube Shorts (High Bitrate)
    try:
        anim.save(output_file, writer='ffmpeg', fps=30, bitrate=5000, 
                  extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'slow', '-profile:v', 'high'])
        print(f"✅ Success: {output_file}")
    except Exception as e:
        print(f"❌ Render Failed: {e}")
        exit(1)

if __name__ == "__main__":
    queue_files = glob.glob('data/render_queue/*.json')
    if not queue_files:
        print("⚠️ No jobs found in queue.")
    else:
        for f in queue_files:
            render_professional_video(f)
