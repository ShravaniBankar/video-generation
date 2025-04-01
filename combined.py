import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips

class CombinedVideoGenerator:
    def __init__(self, width=1280, height=720, output_dir="output"):
        self.width = width
        self.height = height
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_text_image(self, text, font_size=60):
        """Create an image with text and random background"""
        background_colors = ["white", "yellow", "pink"]
        background_color = random.choice(background_colors)
        color_map = {
            "white": (255, 255, 255),
            "yellow": (255, 255, 0),
            "pink": (255, 192, 203)
        }
        
        image = Image.new('RGB', (self.width, self.height), color_map[background_color])
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2
        
        draw.text((x, y), text, fill='black', font=font)
        return image
    
    def create_sample_image(self, index):
        """Create a sample image using PIL"""
        img_path = os.path.join(self.output_dir, f"sample_image{index}.jpg")
        if not os.path.exists(img_path):
            # Create image with colored background
            colors = [(255, 200, 200), (200, 255, 200)]
            image = Image.new('RGB', (self.width, self.height), colors[index % 2])
            
            # Add text to image
            draw = ImageDraw.Draw(image)
            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()
            
            text = f"Sample Image {index}"
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (self.width - text_width) // 2
            y = (self.height - text_height) // 2
            
            draw.text((x, y), text, fill='black', font=font)
            
            # Save image
            image.save(img_path)
        return img_path
    
    def create_combined_video(self, texts, image_count=2, output_filename="combined_video.mp4"):
        """Create a video with text slides and images"""
        try:
            clips = []
            frame_duration = 2.0
            
            # Combine texts and prepare clips
            all_text = " ".join(texts)
            
            # Prepare text and image clips
            for i, text in enumerate(texts):
                # Create text image
                text_image = self.create_text_image(text)
                text_img_path = os.path.join(self.output_dir, f"text_frame_{i}.png")
                text_image.save(text_img_path)
                
                # Create text clip
                text_clip = ImageClip(text_img_path).set_duration(frame_duration)
                text_clip = text_clip.fadeout(1).fadein(1)
                clips.append(text_clip)
                os.remove(text_img_path)
            
            # Add image clips
            for i in range(image_count):
                image_path = self.create_sample_image(i)
                image_clip = ImageClip(image_path).set_duration(frame_duration)
                clips.append(image_clip)
            
            # Generate speech for entire text
            temp_audio_path = os.path.join(self.output_dir, "combined_audio.mp3")
            tts = gTTS(text=all_text, lang='en')
            tts.save(temp_audio_path)
            
            # Combine clips
            final_clip = concatenate_videoclips(clips)
            audio_clip = AudioFileClip(temp_audio_path)
            final_clip = final_clip.set_audio(audio_clip)
            
            # Write video
            output_path = os.path.join(self.output_dir, output_filename)
            final_clip.write_videofile(output_path, fps=24)
            
            # Clean up
            os.remove(temp_audio_path)
            
            print(f"Combined video created: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error creating combined video: {str(e)}")
            return None

def main():
    generator = CombinedVideoGenerator()
    generator.create_combined_video([
        "Welcome to our presentation",
        "Here are some interesting images",
        "Thank you for watching"
    ])

if __name__ == "__main__":
    main()