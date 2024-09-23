import re


def get_neural_name(accent='us', gender='female'):
    switch = {
        ('indian', 'female'): 'en-IN-Neural2-D',
        ('indian', 'male'): 'en-IN-Neural2-C',
        ('uk', 'female'): 'en-GB-Neural2-C',
        ('uk', 'male'): 'en-GB-Neural2-D',
        ('us', 'male'): 'en-US-Neural2-D',
        ('us', 'female'): 'en-US-Neural2-C'
    }
    return switch.get((accent.lower(), gender.lower()), 'en-US-Neural2-C')


def remove_ssml_tags(text):
  # Define a regular expression pattern that matches any SSML tag
  pattern = r"<[^>]+>"
  # Use re.sub() to replace the matched tags with empty strings
  result = re.sub(pattern, "", text)
  # Return the result
  return result

""" Gets open ai voices based on gender selected """
def get_voice(gender='female'):
    switch = {
        'female': 'nova',
        'male': 'onyx'
    }
    return switch.get(gender.lower(), 'nova')