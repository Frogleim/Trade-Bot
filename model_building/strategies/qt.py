import base58
import hashlib
import ecdsa
import itertools

def wif_to_private_key(wif_key):
    decoded = base58.b58decode(wif_key)
    private_key_hex = decoded[1:-4].hex()
    return private_key_hex

def private_key_to_public_key(private_key_hex):
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex), curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    public_key = b'\x04' + vk.to_string()
    return public_key

def public_key_to_address(public_key):
    sha256 = hashlib.sha256(public_key).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256)
    pubkey_hash = ripemd160.digest()
    network_byte = b'\x00'
    checksum = hashlib.sha256(hashlib.sha256(network_byte + pubkey_hash).digest()).digest()[:4]
    address = base58.b58encode(network_byte + pubkey_hash + checksum).decode('utf-8')
    return address

known_start = '5KSFWJ'
known_end = 'jsLi2RuJF'
btc_address = '198aMn6ZYAczwrE5NvNTUMyJ5qkfy4g3Hi'

possible_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

for middle_part in itertools.product(possible_chars, repeat=35):
    candidate_wif = known_start + ''.join(middle_part) + known_end
    try:
        private_key_hex = wif_to_private_key(candidate_wif)
        public_key = private_key_to_public_key(private_key_hex)
        derived_address = public_key_to_address(public_key)
        if derived_address == btc_address:
            print(f'Found valid WIF key: {candidate_wif}')
            break
    except Exception as e:
        continue

# Note: This script is for illustration purposes and is not practically executable due to the vast number of combinations.
