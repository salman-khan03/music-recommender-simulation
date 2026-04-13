"""
Command line runner for the Music Recommender Simulation.

Run from the project root with:
    python -m src.main
"""

import sys
import os

# Allow running as `python -m src.main` from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tabulate import tabulate  # noqa: E402
from src.recommender import load_songs, recommend_songs, SCORING_MODES  # noqa: E402


# ---------------------------------------------------------------------------
# User profiles — each dict is a full taste profile sent to the recommender
# ---------------------------------------------------------------------------

PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "valence": 0.80,
        "likes_acoustic": False,
        "preferred_decade": 2020,
        "mood_tags": ["euphoric", "uplifting", "feel-good"],
    },
    "Chill Lofi Study": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.38,
        "valence": 0.58,
        "likes_acoustic": True,
        "preferred_decade": 2020,
        "mood_tags": ["calm", "focused", "cozy"],
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "valence": 0.45,
        "likes_acoustic": False,
        "preferred_decade": 2010,
        "mood_tags": ["intense", "powerful", "adrenaline"],
    },
    "Late Night Synthwave": {
        "genre": "synthwave",
        "mood": "moody",
        "energy": 0.72,
        "valence": 0.50,
        "likes_acoustic": False,
        "preferred_decade": 2010,
        "mood_tags": ["moody", "dreamy", "nostalgic"],
    },
    "Sad Acoustic Vibes": {
        "genre": "folk",
        "mood": "melancholic",
        "energy": 0.30,
        "valence": 0.40,
        "likes_acoustic": True,
        "preferred_decade": 2010,
        "mood_tags": ["melancholic", "nostalgic", "calm"],
    },
}


def print_recommendations(
    profile_name: str,
    user_prefs: dict,
    recommendations: list,
    mode: str = "balanced",
    label: str = "",
) -> None:
    """Print a tabulate fancy_grid table of recommendations for one profile."""
    title = f"Profile: {profile_name}"
    if label:
        title += f"  [{label}]"
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(
        f"  Mode: {mode}  |  genre={user_prefs['genre']}  "
        f"mood={user_prefs['mood']}  energy={user_prefs['energy']}"
    )
    print(f"{'=' * 70}")

    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        # Split reasons onto separate lines for readability
        reasons_wrapped = "\n".join(explanation.split("; "))
        rows.append([
            rank,
            f"{song['title']}\n{song['artist']}",
            f"{score:.2f}",
            reasons_wrapped,
        ])

    print(tabulate(
        rows,
        headers=["#", "Song / Artist", "Score", "Why"],
        tablefmt="grid",
    ))


def main() -> None:
    """Load songs and run all demo sections."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # ------------------------------------------------------------------
    # Section 1 — All profiles in balanced mode (standard run)
    # ------------------------------------------------------------------
    print("\n\n" + "#" * 70)
    print("  SECTION 1 -- All profiles | Balanced mode")
    print("#" * 70)
    for profile_name, user_prefs in PROFILES.items():
        recs = recommend_songs(user_prefs, songs, k=5, mode="balanced")
        print_recommendations(profile_name, user_prefs, recs, mode="balanced")

    # ------------------------------------------------------------------
    # Section 2 — Scoring mode comparison (Challenge 2)
    # Same profile, every mode — shows how weights shift rankings
    # ------------------------------------------------------------------
    print("\n\n" + "#" * 70)
    print("  SECTION 2 -- Scoring Mode Comparison (High-Energy Pop, top 3)")
    print("#" * 70)
    pop_prefs = PROFILES["High-Energy Pop"]
    for mode in SCORING_MODES:
        recs = recommend_songs(pop_prefs, songs, k=3, mode=mode)
        print_recommendations("High-Energy Pop", pop_prefs, recs, mode=mode)

    # ------------------------------------------------------------------
    # Section 3 — Diversity penalty on/off comparison (Challenge 3)
    # ------------------------------------------------------------------
    print("\n\n" + "#" * 70)
    print("  SECTION 3 -- Diversity Penalty Comparison (Chill Lofi Study)")
    print("#" * 70)
    lofi_prefs = PROFILES["Chill Lofi Study"]

    recs_standard = recommend_songs(lofi_prefs, songs, k=5, mode="balanced")
    print_recommendations(
        "Chill Lofi Study", lofi_prefs, recs_standard,
        mode="balanced", label="no diversity penalty",
    )

    # Temporarily patch recommend_songs to enable diversity
    # (diversity is always ON in this version — shown via the penalty reasons)
    recs_diverse = recommend_songs(lofi_prefs, songs, k=5, mode="balanced")
    # Force diversity: re-import with penalty visible by calling internal logic
    from src.recommender import score_song  # noqa: E402

    def _diverse_recommend(user_prefs, songs_list, k=5, mode="balanced"):
        """Local helper that always applies the diversity penalty."""
        scored = []
        for s in songs_list:
            raw, reasons = score_song(user_prefs, s, mode=mode)
            scored.append([s, raw, list(reasons)])
        scored.sort(key=lambda x: x[1], reverse=True)

        seen_artists: dict = {}
        seen_genres: dict = {}
        for entry in scored:
            s, score, reasons = entry
            penalty, parts = 0.0, []
            if seen_artists.get(s["artist"], 0) > 0:
                penalty += 0.5
                parts.append("artist repeat (-0.5)")
            if seen_genres.get(s["genre"], 0) > 0:
                penalty += 0.3
                parts.append("genre repeat (-0.3)")
            if penalty:
                entry[1] = round(score - penalty, 2)
                reasons = reasons + parts
            entry[2] = "; ".join(reasons)
            seen_artists[s["artist"]] = seen_artists.get(s["artist"], 0) + 1
            seen_genres[s["genre"]] = seen_genres.get(s["genre"], 0) + 1

        scored.sort(key=lambda x: x[1], reverse=True)
        return [(e[0], e[1], e[2]) for e in scored[:k]]

    recs_diverse = _diverse_recommend(lofi_prefs, songs, k=5, mode="balanced")
    print_recommendations(
        "Chill Lofi Study", lofi_prefs, recs_diverse,
        mode="balanced", label="WITH diversity penalty",
    )


if __name__ == "__main__":
    main()