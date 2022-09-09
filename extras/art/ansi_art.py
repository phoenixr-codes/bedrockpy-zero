from PIL import Image
import powerstring as ps

def print_bedrock():
    IMG = Image.open("bedrock.png")
    PIXELS = IMG.getdata()
    
    Color = ps.Color.from_rgb
    
    for idx, rgba in enumerate(PIXELS):
        r, g, b, _ = rgba
        if idx % 16 == 0:
            print()
        ps.printc("  ", Color(r,g,b).bg, end = "")
    
if __name__ == "__main__":
    print_bedrock()