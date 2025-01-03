import requests
from mnemonic import Mnemonic
from bip_utils import (
    Bip39SeedGenerator,
    Bip44, Bip44Coins, Bip44Changes
)

# ----------------------------------------------------------------------------
# 1) Define a method to check a P2PKH address balance via Blockstream's API
#    This method prints the full JSON response and returns the 
#    'funded_txo_sum' (satoshis) or None if an error occurs.
# ----------------------------------------------------------------------------
def check_address_balance(address):
    """
    Returns the 'funded_txo_sum' from Blockstream API (integer in satoshis)
    for the specified P2PKH 'address'. 
    Returns None if there's an error connecting or if data is invalid.
    
    Displays the address and the raw JSON response as well.
    """
    url = f"https://blockstream.info/api/address/{address}"
    try:
        response = requests.get(url)
        print(f"\n[DEBUG] Checking address: {address}")
        print(f"[DEBUG] Server raw response status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            # Display the full JSON payload:
            print(f"[DEBUG] Server response JSON:\n{data}\n")
            
            # 'funded_txo_sum' is the total satoshis that have *ever* been received
            funded_sum = data["chain_stats"]["funded_txo_sum"]
            return funded_sum
        else:
            print(f"[!] HTTP Error {response.status_code} for {address}")
            return None
    except Exception as e:
        print(f"[!] Exception while checking balance for {address}: {e}")
        return None

# ----------------------------------------------------------------------------
# 2) A function to derive and check addresses from a BIP39 phrase 
#    using the path m/44'/0'/0'/0/i (legacy P2PKH addresses).
# ----------------------------------------------------------------------------
def check_seed_for_legacy_addresses(seed_phrase, max_addresses=3):
    """
    Given a BIP39 'seed_phrase',
    - Generate the seed bytes
    - Build the bip44 wallet object for Bitcoin mainnet (Bip44Coins.BITCOIN)
    - Derive up to 'max_addresses' external addresses from m/44'/0'/0'/0/i
    - Check each address’s balance via a block explorer
    - Return any addresses that have a non-zero (or non-null) funded sum
    """
    # Convert the mnemonic to a seed (bytes)
    mnemo = Mnemonic("english")
    if not mnemo.check(seed_phrase):
        # If the seed phrase fails internal checks, skip it
        print(f"[!] Invalid BIP39 phrase: {seed_phrase}")
        return []
    
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    
    # Construct the BIP44 master key for BTC
    bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    # m/44'/0'
    #   └─ /0'  (Account=0)
    #       └─ /0   (External/change)
    bip44_acc = bip44_mst.Purpose().Coin().Account(0)
    bip44_change = bip44_acc.Change(Bip44Changes.CHAIN_EXT)
    
    existing_addresses = []
    
    # Derive up to 'max_addresses' addresses
    for i in range(max_addresses):
        bip44_addr = bip44_change.AddressIndex(i)
        p2pkh_address = bip44_addr.PublicKey().ToAddress()
        
        # Optionally check if there's a balance for each
        funded_sum = check_address_balance(p2pkh_address)
        if funded_sum is not None and funded_sum > 0:
            existing_addresses.append((p2pkh_address, funded_sum, i))
    
    return existing_addresses

# ----------------------------------------------------------------------------
# 3) Main flow: iterate over all the valid combination seeds you displayed.
#    (Below is just an example with a few seeds. You can adapt to your full list.)
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    # EXAMPLE: Replace or extend with your entire list of valid BIP39 mnemonics
    test_seed_phrases = [
        "panel machine enforce hope faith riot virtual lunch faculty cinnamon another pattern",
        "panel magic enforce hope faith riot virtual lunch faculty cinnamon another panic",
        # ... add more ...
    ]
    
    for seed in test_seed_phrases:
        print("================================================================================")
        print(f"Checking seed:\n{seed}\n")
        
        result = check_seed_for_legacy_addresses(seed, max_addresses=5)
        
        if result:
            print(f"[RESULT] Non-empty addresses found for the seed: {seed}")
            for (addr, sat_sum, index) in result:
                print(f"    - Address Index: {index}")
                print(f"      Address:       {addr}")
                print(f"      FundedSum:     {sat_sum} satoshis")
        else:
            print("[RESULT] No funded addresses found (or all calls returned None).")
        
        print("================================================================================\n")
