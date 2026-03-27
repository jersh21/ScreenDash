from PIL import Image
import os

def process_icon():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, 'Untitled.ico')
    
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    try:
        # Load the original image (which might just be a PNG renamed to .ico or a poorly formatted .ico)
        img = Image.open(input_path).convert("RGBA")
        print(f"Loaded successfully: {img.size}")
        
        # Determine the size of the square
        max_dim = max(img.size)
        
        # Create a new square image with a black background
        square_img = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 255))
        
        # Calculate pasting coordinates to center the original image
        offset_x = (max_dim - img.width) // 2
        offset_y = (max_dim - img.height) // 2
        
        # Paste the original image
        square_img.paste(img, (offset_x, offset_y), img)
        
        # Save as PNG
        png_path = os.path.join(base_dir, 'icon.png')
        square_img.save(png_path, format="PNG")
        print(f"Saved PNG to {png_path}")
        
        # Save as proper ICO with multiple sizes
        ico_path = os.path.join(base_dir, 'icon.ico')
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        square_img.save(ico_path, format="ICO", sizes=sizes)
        print(f"Saved ICO to {ico_path}")
        
    except Exception as e:
        print(f"Error processing icon: {e}")

if __name__ == '__main__':
    process_icon()
