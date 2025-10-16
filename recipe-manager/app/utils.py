import hashlib

def get_color_from_string(s: str) -> str:
    """
    Generates a deterministic, visually pleasing hex color from a string.
    """
    # Use a hash to get a consistent integer value for the string
    hash_object = hashlib.md5(s.encode())
    hash_digest = hash_object.hexdigest()
    hash_int = int(hash_digest, 16)

    # Generate HSL values for more pleasing colors
    # We'll keep saturation and lightness constant for a consistent theme
    hue = hash_int % 360  # Hue from 0 to 359
    saturation = 70      # Saturation in %
    lightness = 80       # Lightness in %

    return f"hsl({hue}, {saturation}%, {lightness}%)"