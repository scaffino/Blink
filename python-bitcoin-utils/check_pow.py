def bits_to_target(bits): 
    bits_int = int(bits, 16)
    exp = bits_int >> 24 
    coeff = bits_int & 0xFFFFFF 
    target = coeff * (2 ** (8 * (exp - 3))) # Calculate target
    # Convert the target to a hexadecimal string and ensure it is 256 bits long (64 hex characters)
    target_hex = hex(target)[2:].zfill(64)  # Remove the '0x' and zero-pad to 64 characters
    return target_hex
    

def check_pow(bits: str, block_hash):
    target = bits_to_target(bits)
    if (block_hash <= target):
        return True