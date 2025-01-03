from itertools import product
from mnemonic import Mnemonic

# Initialize the BIP39 Mnemonic generator
mnemo = Mnemonic("english")

# Words from the BIP39 word list based on provided constraints
words_p = ["panel", "panda", "panic", "parade", "parent", "park", "party", "patient", "pattern", "pause", "payment"]
words_m = ["machine", "magic", "magnet", "major", "make", "mammal", "manage", "maple", "market", "marriage", "material", "matrix"]
words_long = ["academy", "another", "blanket", "coconut", "comment", "company", "connect", "economy", "holiday", "journey", "saturday"]

# Generate all plausible combinations based on constraints
plausible_combinations = list(product(words_p, words_m, words_long, words_p))

# Reconstruct the seed phrase for each combination
base_phrase = ["enforce", "hope", "faith", "riot", "virtual", "lunch", "faculty", "cinnamon"]

# Validate combinations against BIP39 checksum
valid_combinations = []
for combo in plausible_combinations:
    candidate_phrase = [combo[0], combo[1]] + base_phrase + [combo[2], combo[3]]
    if mnemo.check(" ".join(candidate_phrase)):
        valid_combinations.append(candidate_phrase)

# Display results
for phrase in valid_combinations:
    print(" ".join(phrase))

