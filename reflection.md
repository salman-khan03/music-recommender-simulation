# Reflection: Comparing Profile Outputs

## Profile Pair 1 — High-Energy Pop vs. Chill Lofi Study

The High-Energy Pop profile consistently surfaces upbeat, danceable pop and EDM tracks (Gym Hero, Pulse Drop, Sunrise City). The Chill Lofi Study profile surfaces quiet, acoustic, low-energy lofi and ambient tracks (Library Rain, Midnight Coding, Spacewalk Thoughts).

This makes complete sense: energy is the feature that varies most between these two profiles (0.85 vs. 0.38), and genre is also opposite (pop vs. lofi). Every point in the scoring recipe pushes them apart. The contrast is the clearest possible demonstration that the scoring logic is working as intended.

## Profile Pair 2 — Deep Intense Rock vs. Sad Acoustic Vibes

The Rock profile tops out with Storm Runner (the only rock song) and then pulls in other high-energy tracks like Pulse Drop and Iron Curtain because energy scores are competitive even without a genre match. The Sad Acoustic Vibes profile tops out with Autumn Letters (folk, melancholic) and then pulls in Crossroads Lament (blues, sad) and Library Rain (lofi, chill, high acousticness).

What is interesting here: the Sad Acoustic Vibes profile is more "open" to genre-crossing than the Rock profile because it awards an acoustic bonus (+0.5) that can partially compensate for a genre miss. A blues or lofi song with high acousticness can beat a folk song with low acousticness. This shows that acoustic preference acts as a kind of cross-genre bridge — which feels musically accurate.

## Profile Pair 3 — Late Night Synthwave vs. High-Energy Pop

Both profiles want moderately-to-high energy, but they diverge on genre and mood. The Synthwave profile is almost "trapped" — there is only one synthwave song (Night Drive Loop), so after that it falls back on other high-energy tracks with no genre bonus. The High-Energy Pop profile has more songs to choose from (pop + indie pop), so its top 5 feel more cohesive.

This comparison exposes the catalog imbalance: niche genre users get worse recommendations simply because there are fewer songs for them. In a real system, this would be a serious fairness problem — users of less-common genres receive a degraded experience through no fault of their own preferences.
