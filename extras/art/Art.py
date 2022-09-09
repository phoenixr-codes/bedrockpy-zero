import art
import time
from ansi_art import print_bedrock

text = "bedrockpy"

art.tprint(text, font = "small")

art.tprint("py", font = "doh")
art.tprint("bedrock", font = "3-d")


for letter in text:
    art.tprint(letter, font = "alpha")
    
print_bedrock()