import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch

def main():
    # 1. Setup file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parquet_path = os.path.join(script_dir, "..", "data", "processed", "integrated_tracking_data.parquet")
    output_dir = os.path.join(script_dir, "..", "out")
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(parquet_path):
        print(f"Error: Database not found at {parquet_path}.")
        return

    print("Loading tracking database...")
    df = pd.read_parquet(parquet_path)

    print("Filtering out empty or invalid coordinates...")
    df_clean = df.dropna(subset=['x', 'y']).copy()

    # Count players per timestamp to find a high-density frame
    counts = df_clean.groupby('timestamp').size()
    max_players_found = counts.max()

    threshold = max(1, max_players_found - 2)
    valid_timestamps = counts[counts >= threshold].index.tolist()

    # Pick a valid timestamp from the middle of the match
    target_timestamp = valid_timestamps[len(valid_timestamps) // 2]
    print(f"Target timestamp selected: {target_timestamp} (contains {counts[target_timestamp]} players)")

    frame_df = df_clean[df_clean['timestamp'] == target_timestamp].copy()

    # -----------------------------------------------------------------
    # ADVANCED DATA NORMALIZATION WITH CLAMPING
    # Define standard field boundaries with center origin (0,0)
    # -----------------------------------------------------------------
    X_MIN, X_MAX = -52.5, 52.5
    Y_MIN, Y_MAX = -34.0, 34.0
    PITCH_LENGTH, PITCH_WIDTH = 105.0, 68.0

    # 1. Clamp values to keep out-of-bounds actions strictly on the pitch edges
    x_clamped = np.clip(frame_df['x'], X_MIN, X_MAX)
    y_clamped = np.clip(frame_df['y'], Y_MIN, Y_MAX)

    # 2. Min-Max normalization to shift scale from 0 to 105 (X) and 0 to 68 (Y)
    frame_df['x_normalized'] = ((x_clamped - X_MIN) / (X_MAX - X_MIN)) * PITCH_LENGTH
    frame_df['y_normalized'] = ((y_clamped - Y_MIN) / (Y_MAX - Y_MIN)) * PITCH_WIDTH
    # -----------------------------------------------------------------

    # 2. Separate the two teams (A and H)
    teams = frame_df['team'].unique()
    if len(teams) < 2:
        print("Warning: Could not find two distinct teams in this snapshot.")
        return

    team_a_name = teams[0]
    team_b_name = teams[1]

    team_a_df = frame_df[frame_df['team'] == team_a_name]
    team_b_df = frame_df[frame_df['team'] == team_b_name]

    # 3. Initialize a standard CUSTOM pitch (0 to 105 on X, 0 to 68 on Y)
    pitch = Pitch(pitch_type='custom',
                  pitch_length=PITCH_LENGTH,
                  pitch_width=PITCH_WIDTH,
                  pitch_color='#22312b',
                  line_color='#c7d5cc')

    fig, ax = pitch.draw(figsize=(13, 8))
    fig.patch.set_facecolor('#22312b')

    # 4. Plot the players using the perfectly normalized coordinates
    # Team A: Red dots
    pitch.scatter(team_a_df['x_normalized'], team_a_df['y_normalized'],
                  ax=ax, color='#e63946', edgecolors='#ffffff',
                  s=150, linewidth=1.5, label=f'Team {team_a_name}')

    # Team B: Blue dots (Team H)
    pitch.scatter(team_b_df['x_normalized'], team_b_df['y_normalized'],
                  ax=ax, color='#457b9d', edgecolors='#ffffff',
                  s=150, linewidth=1.5, label=f'Team {team_b_name}')

    # 5. Add tactical details (Title and Legend)
    safe_timestamp = str(target_timestamp).replace(":", "-").replace(".", "-")
    ax.set_title(f"Match Snapshot (Normalized) - Time: {target_timestamp}", color='#c7d5cc', fontsize=16, pad=10)
    ax.legend(facecolor='#22312b', edgecolor='#c7d5cc', labelcolor='#c7d5cc', loc='upper left')

    # 6. Save the final tactical map
    output_file = os.path.join(output_dir, f"match_snapshot_{safe_timestamp}.png")
    plt.savefig(output_file, facecolor=fig.get_facecolor(), edgecolor='none', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Success! Perfect tactical snapshot saved to: {output_file}")

if __name__ == "__main__":
    main()