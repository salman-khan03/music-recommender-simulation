# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder suggests up to 5 songs from a small catalog based on a user's preferred genre, mood, energy level, and acoustic preference.

It is designed for **classroom exploration only** — to demonstrate how content-based filtering works in practice. It is not intended for production music platforms, real user data, or any commercial use.

It should **not** be used to make decisions that affect users with diverse or non-Western musical tastes, since the catalog does not represent that breadth.

---

## 3. How the Model Works

Every song in the catalog gets a numeric score by comparing it to the user's taste profile:

- If the song's **genre** matches the user's favorite genre, it earns the most points (2 points).
- If the song's **mood** matches the user's favorite mood, it earns 1 extra point.
- **Energy** is rated on a 0–1 scale. The closer the song's energy is to what the user wants, the more points it earns (up to 1 point).
- **Valence** (how emotionally positive a song feels) can add up to half a point when close to the user's preference.
- If the user likes acoustic music and the song is highly acoustic, it gets a small bonus.

Once every song is scored, the list is sorted from highest to lowest and the top 5 are returned along with a plain-language explanation of why each song ranked where it did.

---

## 4. Data

- **Catalog size**: 20 songs in `data/songs.csv`.
- **Genres represented**: pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, r&b, classical, country, edm, metal, folk, reggae, blues, electronic.
- **Moods represented**: happy, chill, intense, relaxed, focused, moody, confident, romantic, peaceful, nostalgic, euphoric, angry, melancholic, sad, energetic.
- The original 10 songs skew toward pop, lofi, and chill/happy moods. The 10 added songs were chosen deliberately to fill genre and mood gaps.
- All numeric values (energy, valence, danceability, acousticness) are on a 0.0–1.0 scale.
- **Limitations**: No real listening data, no lyrics, no language or cultural metadata, no release date. Whose taste does this reflect? Mostly Western popular music of the 2010s–2020s.

---

## 5. Strengths

- Works best for users with clear, common genre preferences (pop, lofi, rock) because those genres have multiple songs in the catalog.
- The scoring is fully transparent — every recommendation includes a reason string explaining exactly which features matched.
- Simple enough to inspect and debug without any ML knowledge.
- The "Chill Lofi Study" and "High-Energy Pop" profiles produce results that feel intuitively correct because the catalog has enough matching songs.

---

## 6. Limitations and Bias

- **Genre dominance**: Genre carries twice the weight of mood. A song that perfectly matches the user's energy and mood but is a different genre will almost always lose to a genre-matched song with poor energy fit. This creates a genre "filter bubble."
- **Dataset imbalance**: Pop and lofi are overrepresented (5 of 20 songs). Users whose favorite genre is pop will always find close matches; users who prefer reggae or blues will see fewer matches and lower absolute scores.
- **Exact string matching**: "indie pop" and "pop" are treated as completely different genres. This means a pop fan misses songs that share the pop aesthetic.
- **No artist diversity**: Nothing prevents the same artist from occupying all top-5 slots. For example, LoRoom has two lofi tracks and will dominate the lofi profile's top results.
- **Adversarial profiles**: Combinations that do not exist in the catalog (e.g., high-energy + sad mood) produce nonsensical recommendations because the system cannot interpolate — it can only match what exists.
- **One-size weighting**: The same weights are used for every user. A user who cares deeply about energy but not at all about genre has no way to express that.

---

## 7. Evaluation

Five distinct user profiles were tested:

| Profile | Top Result | Felt Correct? |
|---|---|---|
| High-Energy Pop | Gym Hero (score ~4.08) | Yes — matches genre, mood, and energy |
| Chill Lofi Study | Library Rain (score ~4.97) | Yes — genre + mood + acoustic bonus |
| Deep Intense Rock | Storm Runner (score ~4.99) | Yes — only rock song, perfect energy |
| Late Night Synthwave | Night Drive Loop (score ~4.97) | Yes — exact genre/mood match |
| Sad Acoustic Vibes | Autumn Letters (score ~4.67) | Yes — folk, melancholic, acoustic |

**Surprise**: The "Sad Acoustic Vibes" profile surfaced the blues track "Crossroads Lament" at #2 even though the genre did not match. The acoustic bonus and close energy made it competitive — demonstrating that numeric features can override genre when scores are close.

**Experiment run**: Mood check was temporarily removed. Rankings shifted noticeably for emotional profiles (sad, moody) but barely changed for energy-dominant profiles (intense rock, EDM). This confirms that mood is most important for emotionally specific users.

---

## 8. Future Work

1. **Weighted user profiles**: Let users specify their own weights (e.g., "I care 80% about mood, 20% about genre") instead of applying fixed weights to everyone.
2. **Fuzzy genre matching**: Build a genre similarity table so "indie pop" scores partial credit against "pop" rather than zero.
3. **Diversity penalty**: After selecting the top pick, penalize subsequent songs from the same artist or genre to ensure variety in the top 5.
4. **Collaborative signals**: Add even a tiny history component — tracks the user has played before could shift scores up or down.
5. **Larger, more balanced catalog**: A real system needs hundreds of songs across every genre, mood, and energy level to avoid filter bubbles.

---

## 9. Personal Reflection

Building this recommender made the abstract idea of "algorithm bias" concrete. Before this project it was easy to think of bias as something only big, opaque neural networks produce. But here, in 50 lines of Python with hand-written weights, the same problem appears: genre gets 2 points just because I wrote `+2.0`, and that single number quietly shapes every recommendation the system ever makes. If I had trained on data from my own playlist, the starting weights would embed my taste into everyone else's experience.

Using AI tools during this project was genuinely helpful for brainstorming scoring strategies and explaining the difference between `.sort()` and `sorted()` — but I had to double-check every suggestion against the actual behavior of the code. The AI's suggestions for weight values were confident but arbitrary; running the profiles showed that some of those values produced surprising results (like the blues track appearing for a folk/melancholic profile). That gap between "sounds right" and "actually works" is exactly where human judgment still matters.

What surprised me most is how much a recommender can "feel" intelligent with almost no real intelligence inside it. Five profiles, twenty songs, and six lines of arithmetic — and the results feel plausible enough that a casual user might not question them. That's a good reminder that even simple systems should be documented, tested, and questioned.
