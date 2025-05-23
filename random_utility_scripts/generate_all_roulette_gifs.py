import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Polygon, Circle
from PIL import Image
import os
import random

generated_nums = []

# --- CONFIGURATION ---
segments = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
colors = ['green', 'red', 'black', 'red', 'black', 'red', 'black', 'red', 'black', 'red',
          'black', 'red', 'black', 'red', 'black', 'red', 'black', 'red', 'black', 'red',
          'black', 'red', 'black', 'red', 'black', 'red', 'black', 'red', 'black', 'red',
          'black', 'red', 'black', 'red', 'black', 'red', 'black']

frame_count = 120
spin_rounds = 6

# --- EASING FUNCTION ---
def ease_out_quad(t):
    return 1 - (1 - t) ** 4

while True:
    # --- RANDOM FINAL ANGLE ---
    segment_angle = 360 / len(segments)
    # Choose a completely random final spin angle over multiple rounds
    random_angle_offset = random.uniform(0, 360)
    final_angle = 360 * spin_rounds + random_angle_offset

    # --- FRAME ANGLES WITH EASING ---
    t_values = np.linspace(0, 1, frame_count)
    angles = [ease_out_quad(t) * final_angle for t in t_values]

    # --- Determine final angle from last frame angle ---
    final_spin_angle = (angles[-1]+ 90) % 360
    segment = final_spin_angle/segment_angle
    winning_segment = segments[int(segment)]

    if winning_segment not in generated_nums:
        print(f"generating {winning_segment} win gif - {len(generated_nums)+1}/37")
        generated_nums.append(winning_segment)
        output_gif = f'roulette_{winning_segment}.gif'
    else:
        continue

    if len(generated_nums) == 37:
        break

    # --- OUTPUT SETUP ---
    frames_dir = 'wheel_frames'
    os.makedirs(frames_dir, exist_ok=True)
    image_paths = []

    # --- DRAW EACH FRAME ---
    for i, angle in enumerate(angles):
        fig, ax = plt.subplots(figsize=(10, 10))
        plt.tight_layout()
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.axis('off')
        fig.patch.set_facecolor('#424549')
        
        # Draw wheel segments
        for j, label in enumerate(segments):
            start_angle = j * segment_angle - angle % 360
            wedge = Wedge((0, 0), 4, start_angle, start_angle + segment_angle,
                        facecolor=colors[j], edgecolor='black')
            ax.add_patch(wedge)

            # Text label
            theta = np.radians(start_angle + segment_angle / 2)
            ax.text(3.6 * np.cos(theta), 3.6 * np.sin(theta), label,
                    ha='center', va='center', fontsize=30, rotation=0, color='white')
        
        center_circle = Circle((0, 0), 3.2, facecolor='white', edgecolor='black', zorder=10)
        ax.add_patch(center_circle)

        
        pointer = Polygon([[0, 4.1], [-0.3, 4.5], [0.3, 4.5]], closed=True, facecolor='red', edgecolor='black')
        ax.add_patch(pointer)

        # Save frame
        frame_path = os.path.join(frames_dir, f'frame_{i:03d}.png')
        plt.savefig(frame_path, dpi=100)
        plt.close()
        image_paths.append(frame_path)

        # --- COMBINE TO GIF ---
    images = [Image.open(p) for p in image_paths]

    # --- HOLD LAST FRAME ---
    last_frame = images[-1]
    for _ in range(100):
        images.append(last_frame)


    images[0].save(output_gif, save_all=True, append_images=images[1:], duration=50, loop=0)

print("DONE!!!!")
    