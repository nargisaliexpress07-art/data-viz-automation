import matplotlib
matplotlib.use('Agg') # Headless backend

import json
import os
import glob
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import shutil

def render_professional_video(config_path):
    print(f"🎬 Starting Industrial Render: {config_path}")
    
    # Load Data
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    video_id = config['id']
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"video_{video_id}.mp4")
    
    # Temp folder for frames (Unique per job to allow parallel processing)
    temp_dir = f"temp_frames_{video_id}"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # Data
    labels = config['data']['labels']
    values = config['data']['values']
    
    # Setup Figure
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(9, 16), dpi=100)
    ax = fig.add_subplot(111)
    
    # Styling
    fig.patch.set_facecolor('#050505')
    ax.set_facecolor('#050505')
    ax.grid(True, linestyle=':', alpha=0.3, color='#333333')
    
    # Text
    plt.text(0.5, 0.93, config['title'], transform=fig.transFigure, 
             ha='center', fontsize=26, fontweight='bold', color='white')
    plt.text(0.5, 0.04, f"Source: {config['source']}", transform=fig.transFigure,
             ha='center', fontsize=12, color='#666666')

    # Axis
    ax.set_xlim(0, len(labels)-1)
    ax.set_ylim(min(values)*0.95, max(values)*1.05)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, color='#888888')

    # Plot Lines
    line, = ax.plot([], [], color='#00ff88', linewidth=6)
    val_text = ax.text(0.5, 0.80, "", transform=ax.transAxes, 
                       ha='center', fontsize=50, fontweight='bold', color='#00ff88')

    # --- FRAME GENERATION LOOP ---
    print(f"📸 Generating {len(values)} frames...")
    
    # We will interpolate to make the video smoother (30 frames total per data point is too fast)
    # Let's create 150 frames total (5 seconds)
    total_frames = 150
    x_indices = np.linspace(0, len(values)-1, total_frames)
    interp_values = np.interp(x_indices, range(len(values)), values)
    
    for i in range(total_frames):
        # Current progress
        curr_x_idx = x_indices[i]
        
        # Prepare data slice
        # We need to plot up to current index
        plot_x = x_indices[:i+1]
        plot_y = interp_values[:i+1]
        
        line.set_data(plot_x, plot_y)
        val_text.set_text(f"{interp_values[i]:,.2f}")
        
        # Save Frame
        frame_path = os.path.join(temp_dir, f"frame_{i:03d}.png")
        plt.savefig(frame_path, format='png', bbox_inches='tight', facecolor='#050505')
        
        # Progress indicator
        if i % 30 == 0:
            print(f"  - Rendered frame {i}/{total_frames}")

    plt.close()

    # --- FFMPEG STITCHING ---
    print("🧵 Stitching frames with FFmpeg...")
    
    cmd = [
        'ffmpeg',
        '-y',                  # Overwrite output
        '-framerate', '30',    # 30 fps
        '-i', f"{temp_dir}/frame_%03d.png", # Input pattern
        '-c:v', 'libx264',     # Codec
        '-pix_fmt', 'yuv420p', # Pixel format for compatibility
        '-preset', 'slow',     # High quality
        '-crf', '18',          # High quality (lower is better)
        output_file
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        size = os.path.getsize(output_file)
        print(f"✅ Success! Video size: {size/1024/1024:.2f} MB")
        
        # Cleanup frames
        shutil.rmtree(temp_dir)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg Error: {e}")
        # Print ffmpeg error log if needed
        # print(e.stderr.decode())
        exit(1)

if __name__ == "__main__":
    queue_files = glob.glob('data/render_queue/*.json')
    if not queue_files:
        print("⚠️ No jobs found.")
    else:
        for f in queue_files:
            render_professional_video(f)
