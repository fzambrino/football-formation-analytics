import os
import matplotlib.pyplot as plt
from mplsoccer import Pitch

def main():
    # Determine the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the output directory for visualizations (out/ folder)
    output_dir = os.path.join(script_dir, "..", "out")
    os.makedirs(output_dir, exist_ok=True)

    print("Drawing the tactical football pitch...")

    # Initialize a standard tactical pitch (120x80 meters is the default Opta standard)
    pitch = Pitch(pitch_type='opta', pitch_color='#22312b', line_color='#c7d5cc')

    # Create the matplotlib figure and axis
    fig, ax = pitch.draw(figsize=(13, 8))

    # Set a professional background color for the figure surrounding the pitch
    fig.patch.set_facecolor('#22312b')

    # Add a temporary title to verify text rendering
    ax.set_title("Tactical Pitch Baseline - Test", color='#c7d5cc', fontsize=18, pad=10)

    # Define the output file path
    output_file = os.path.join(output_dir, "tactical_pitch_baseline.png")

    # Save the figure to the out/ folder
    plt.savefig(output_file, facecolor=fig.get_facecolor(), edgecolor='none', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Success! The pitch image has been saved to: {output_file}")

if __name__ == "__main__":
    main()