import matplotlib
# 🛑 CRITICAL FIX: Tell Matplotlib we are on a headless server
matplotlib.use('Agg') 

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

    # Data
    labels = config['data']['labels']
    values = config['data']['values']
    
    # Setup Figure (1080x1920)
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(9, 16), dpi=100)
    ax = fig.add_subplot(111)
    
    # Styling
    fig.patch.set_facecolor('#050505')
    ax.set_facecolor('#050505')
    ax.grid(True, linestyle=':', alpha=0.3, color='#333333')
    
    # Typography
    plt.text(0.5, 0.93, config['title'], transform=fig.transFigure, 
             ha='center', fontsize=26, fontweight='bold', color='white')
    plt.text(0.5, 0.04, f"Source: {config['source']}", transform=fig.transFigure,
             ha='center', fontsize=12, color='#666666')

    # Axis Limits
    ax.set_xlim(0, len(labels)-1)
    ax.set_ylim(min(values)*0.95, max(values)*1.05)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, color='#888888')

    # Plot Elements
    line, = ax.plot([], [], color='#00ff88', linewidth=6)
    val_text = ax.text(0.5, 0.80, "", transform=ax.transAxes, 
                       ha='center', fontsize=50, fontweight='bold', color='#00ff88')

    def init():
        line.set_data([], [])
        val_text.set_text("")
        return line, val_text

    def animate(i):
        x = range(i+1)
        y = values[:i+1]
        line.set_data(x, y)
        val_text.set_text(f"{values[i]:.2f}")
        return line, val_text

    # Render
    # ⚠️ CRITICAL FIX: blit=False is safer for headless servers
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=len(values), interval=100, blit=False)
    
    print(f"⚙️ Rendering to {output_file}...")
    
    try:
        # standardizing the writer
        anim.save(output_file, writer='ffmpeg', fps=30, 
                  extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p'])
        
        # Verify size immediately
        size = os.path.getsize(output_file)
        print(f"✅ Render Complete. Size: {size/1024/1024:.2f} MB")
        
        if size < 100000: # Less than 100KB
            print("❌ ERROR: File too small. Rendering failed.")
            exit(1)
            
    except Exception as e:
        print(f"❌ Render Failed: {e}")
        exit(1)

if __name__ == "__main__":
    queue_files = glob.glob('data/render_queue/*.json')
    if not queue_files:
        print("⚠️ No jobs found.")
    else:
        for f in queue_files:
            render_professional_video(f)
