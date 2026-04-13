import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """Represents a song and its audio/genre attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    # Challenge 1 — new fields with defaults so existing tests keep working
    popularity: int = 50
    release_decade: int = 2010
    mood_tags: str = ""


@dataclass
class UserProfile:
    """Represents a user's taste preferences used to score songs."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# ---------------------------------------------------------------------------
# Challenge 2 — Scoring modes
# Each mode is a dict of weights that control how much each signal contributes.
# ---------------------------------------------------------------------------

SCORING_MODES: Dict[str, Dict[str, float]] = {
    "balanced": {
        "genre_weight":      2.0,
        "mood_weight":       1.0,
        "energy_weight":     1.0,
        "valence_weight":    0.5,
        "acoustic_bonus":    0.5,
        "popularity_weight": 0.02,   # * popularity (0-100) → max +2.0
        "decade_bonus":      0.3,
        "mood_tag_weight":   0.25,   # * number of matching tags
    },
    "genre_first": {
        "genre_weight":      4.0,
        "mood_weight":       0.5,
        "energy_weight":     0.5,
        "valence_weight":    0.2,
        "acoustic_bonus":    0.3,
        "popularity_weight": 0.01,
        "decade_bonus":      0.2,
        "mood_tag_weight":   0.1,
    },
    "mood_first": {
        "genre_weight":      1.0,
        "mood_weight":       3.0,
        "energy_weight":     0.5,
        "valence_weight":    0.5,
        "acoustic_bonus":    0.5,
        "popularity_weight": 0.01,
        "decade_bonus":      0.2,
        "mood_tag_weight":   0.5,
    },
    "energy_focused": {
        "genre_weight":      1.0,
        "mood_weight":       0.5,
        "energy_weight":     3.0,
        "valence_weight":    0.3,
        "acoustic_bonus":    0.2,
        "popularity_weight": 0.015,
        "decade_bonus":      0.1,
        "mood_tag_weight":   0.1,
    },
}


class Recommender:
    """Scores and ranks Song objects against a UserProfile."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Compute a numeric score and list of reasons for a single song."""
        score = 0.0
        reasons = []

        if song.genre == user.favorite_genre:
            score += 2.0
            reasons.append(f"genre match: {song.genre} (+2.0)")

        if song.mood == user.favorite_mood:
            score += 1.0
            reasons.append(f"mood match: {song.mood} (+1.0)")

        energy_diff = abs(song.energy - user.target_energy)
        energy_pts = round(1.0 - energy_diff, 2)
        score += energy_pts
        reasons.append(f"energy closeness: {energy_pts:.2f}")

        if user.likes_acoustic and song.acousticness > 0.6:
            score += 0.5
            reasons.append("acoustic bonus (+0.5)")

        return score, reasons

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs sorted by score (highest first)."""
        scored = sorted(self.songs, key=lambda s: self._score(user, s)[0], reverse=True)
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why a song was recommended."""
        _, reasons = self._score(user, song)
        return "; ".join(reasons) if reasons else "No specific match found."


# ---------------------------------------------------------------------------
# Functional API used by src/main.py
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of dicts with typed values."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"]           = int(row["id"])
            row["energy"]       = float(row["energy"])
            row["tempo_bpm"]    = float(row["tempo_bpm"])
            row["valence"]      = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            # Challenge 1 — new columns (default gracefully if column missing)
            row["popularity"]     = int(row.get("popularity") or 50)
            row["release_decade"] = int(row.get("release_decade") or 2010)
            row["mood_tags"]      = row.get("mood_tags", "") or ""
            songs.append(row)
    return songs


def score_song(
    user_prefs: Dict,
    song: Dict,
    mode: str = "balanced",
) -> Tuple[float, List[str]]:
    """
    Score a single song dict against user preference dict.

    Challenge 1 — Extended scoring: popularity, release_decade, mood_tags.
    Challenge 2 — Mode-aware weights via SCORING_MODES.

    Scoring recipe (balanced mode):
      +2.0        genre match
      +1.0        mood match
      +0.0–1.0    energy closeness  (weight * (1 − |song_energy − target|))
      +0.0–0.5    valence closeness (weight * (1 − |song_valence − target|))
      +0.5        acoustic bonus if user likes_acoustic and acousticness > 0.6
      +0.0–2.0    popularity score  (0.02 * popularity)
      +0.3        decade bonus if song release_decade == user preferred_decade
      +0.25/tag   mood tag overlap   (0.25 * number of matching tags)

    Returns (total_score, list_of_reason_strings).
    """
    w = SCORING_MODES.get(mode, SCORING_MODES["balanced"])
    score = 0.0
    reasons = []

    # Genre match — strongest taste signal
    if song.get("genre") == user_prefs.get("genre"):
        pts = w["genre_weight"]
        score += pts
        reasons.append(f"genre match: {song['genre']} (+{pts:.1f})")

    # Mood match — primary emotional signal
    if song.get("mood") == user_prefs.get("mood"):
        pts = w["mood_weight"]
        score += pts
        reasons.append(f"mood match: {song['mood']} (+{pts:.1f})")

    # Energy closeness — rewards songs near user's target energy
    if "energy" in user_prefs:
        diff = abs(song.get("energy", 0.5) - user_prefs["energy"])
        pts = round(w["energy_weight"] * (1.0 - diff), 2)
        score += pts
        reasons.append(f"energy closeness: {pts:.2f}")

    # Valence closeness — emotional positivity proximity
    if "valence" in user_prefs:
        diff = abs(song.get("valence", 0.5) - user_prefs["valence"])
        pts = round(w["valence_weight"] * (1.0 - diff), 2)
        score += pts
        reasons.append(f"valence closeness: {pts:.2f}")

    # Acoustic bonus
    if user_prefs.get("likes_acoustic") and song.get("acousticness", 0) > 0.6:
        pts = w["acoustic_bonus"]
        score += pts
        reasons.append(f"acoustic bonus (+{pts:.1f})")

    # Challenge 1a — Popularity: linear scale, always applied
    pop = song.get("popularity", 50)
    pts = round(w["popularity_weight"] * pop, 2)
    score += pts
    reasons.append(f"popularity {pop}/100 (+{pts:.2f})")

    # Challenge 1b — Release decade match
    if "preferred_decade" in user_prefs and "release_decade" in song:
        if song["release_decade"] == user_prefs["preferred_decade"]:
            pts = w["decade_bonus"]
            score += pts
            reasons.append(f"decade match: {song['release_decade']} (+{pts:.1f})")

    # Challenge 1c — Mood tags overlap
    user_tags = set(user_prefs.get("mood_tags", []))
    song_tags = set(t.strip() for t in song.get("mood_tags", "").split(";") if t.strip())
    matching = user_tags & song_tags
    if matching:
        pts = round(w["mood_tag_weight"] * len(matching), 2)
        score += pts
        reasons.append(f"mood tags ({', '.join(sorted(matching))}) +{pts:.2f}")

    return score, reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "balanced",
) -> List[Tuple[Dict, float, str]]:
    """
    Score every song, apply diversity penalty, sort descending, return top-k.

    Challenge 2: mode selects a weight preset from SCORING_MODES.
    Challenge 3: diversity penalty — penalises repeated artists (−0.5) and
                 repeated genres (−0.3) relative to higher-ranked results.
                 Penalties are applied in raw-score order then re-sorted.

    Each result is (song_dict, adjusted_score, explanation_string).
    Uses sorted() so the original songs list is never mutated.
    """
    # Step 1: score every song
    scored = []
    for song in songs:
        raw_score, reasons = score_song(user_prefs, song, mode=mode)
        explanation = "; ".join(reasons) if reasons else "no specific match"
        scored.append([song, raw_score, explanation, list(reasons)])

    # Step 2: sort by raw score descending
    scored.sort(key=lambda x: x[1], reverse=True)

    # Step 3 (Challenge 3) — diversity penalty, applied in rank order
    seen_artists: Dict[str, int] = {}
    seen_genres: Dict[str, int] = {}

    for entry in scored:
        song, score, explanation, reasons = entry
        artist = song.get("artist", "")
        genre  = song.get("genre", "")

        penalty = 0.0
        penalty_parts = []
        if seen_artists.get(artist, 0) > 0:
            penalty += 0.5
            penalty_parts.append("artist repeat (-0.5)")
        if seen_genres.get(genre, 0) > 0:
            penalty += 0.3
            penalty_parts.append("genre repeat (-0.3)")

        if penalty > 0:
            entry[1] = round(score - penalty, 2)
            entry[2] = "; ".join(reasons + penalty_parts)

        seen_artists[artist] = seen_artists.get(artist, 0) + 1
        seen_genres[genre]   = seen_genres.get(genre, 0) + 1

    # Step 4: re-sort after penalties, return top-k
    scored.sort(key=lambda x: x[1], reverse=True)
    return [(entry[0], entry[1], entry[2]) for entry in scored[:k]]
