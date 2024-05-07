import re


def unbold_text(text):
    # Mapping of bold numbers to their regular equivalents
    bold_numbers = {
        '𝟬': '0', '𝟭': '1', '𝟮': '2', '𝟯': '3', '𝟰': '4',
        '𝟱': '5', '𝟲': '6', '𝟳': '7', '𝟴': '8', '𝟵': '9'
    }

    # Function to convert bold characters (letters and numbers)
    def convert_bold_char(match):
        char = match.group(0)
        # Convert bold numbers
        if char in bold_numbers:
            return bold_numbers[char]
        # Convert bold uppercase letters
        elif '\U0001D5D4' <= char <= '\U0001D5ED':
            return chr(ord(char) - 0x1D5D4 + ord('A'))
        # Convert bold lowercase letters
        elif '\U0001D5EE' <= char <= '\U0001D607':
            return chr(ord(char) - 0x1D5EE + ord('a'))
        else:
            return char  # Return the character unchanged if it's not a bold number or letter

    # Regex for bold characters (numbers, uppercase, and lowercase letters)
    bold_pattern = re.compile(r'[\U0001D5D4-\U0001D5ED\U0001D5EE-\U0001D607\U0001D7CE-\U0001D7FF]')
    text = bold_pattern.sub(convert_bold_char, text)

    return text


def unitalic_text(text):
    # Function to convert italic characters (both letters)
    def convert_italic_char(match):
        char = match.group(0)
        # Unicode ranges for italic characters
        if '\U0001D608' <= char <= '\U0001D621':  # Italic uppercase A-Z
            return chr(ord(char) - 0x1D608 + ord('A'))
        elif '\U0001D622' <= char <= '\U0001D63B':  # Italic lowercase a-z
            return chr(ord(char) - 0x1D622 + ord('a'))
        else:
            return char  # Return the character unchanged if it's not an italic letter

    # Regex for italic characters (uppercase and lowercase letters)
    italic_pattern = re.compile(r'[\U0001D608-\U0001D621\U0001D622-\U0001D63B]')
    text = italic_pattern.sub(convert_italic_char, text)

    return text

def remove_emojis_and_symbols(text):
    # Extended pattern to include specific symbols like ↓ (U+2193) or ↳ (U+21B3)
    emoji_and_symbol_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002193"             # downwards arrow
        u"\U000021B3"             # downwards arrow with tip rightwards
        u"\U00002192"             # rightwards arrow
                           "]+", flags=re.UNICODE)
    
    return emoji_and_symbol_pattern.sub(r' ', text)

def replace_urls_with_placeholder(text, placeholder="[URL]"):
    # Regular expression pattern for matching URLs
    url_pattern = r'https?://\S+|www\.\S+'
    
    return re.sub(url_pattern, placeholder, text)