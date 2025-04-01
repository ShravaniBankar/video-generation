from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from gtts import gTTS
import os
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip
import random
class SimpleVideoGenerator:
    def __init__(self):
        self.width = 1280
        self.height = 720
        self.duration = 5  # video duration in seconds
        self.fps = 24
        
    def create_text_image(self, text):
        """Create an image with text"""
        # Create a blank image with white background
        color = ["yellow","pink","white"]
        mychoice = random.choice(color)
        image = Image.new('RGB', (self.width, self.height), mychoice)
        draw = ImageDraw.Draw(image)
        
        # Try to use Arial font, fall back to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        # Draw text in the center of image
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2
        
        draw.text((x, y), text, fill='black', font=font)
        return image
    
    def create_video(self, text, output_path="output.mp4"):
        try:
            # Create image with text
            image = self.create_text_image(text)
            
            # Save image temporarily
            temp_image_path = "temp_frame.png"
            image.save(temp_image_path)
            
            # Create audio file
            temp_audio_path = "temp_audio.mp3"
            tts = gTTS(text=text, lang='en')
            tts.save(temp_audio_path)
            
            # Create video from image
            image_clip = ImageClip(temp_image_path).set_duration(self.duration)
            
            # Load audio and set duration
            audio_clip = AudioFileClip(temp_audio_path)
            
            # Combine image and audio
            video = image_clip.set_audio(audio_clip)
            
            # Write the final video
            video.write_videofile(output_path, fps=self.fps)
            
            # Clean up temporary files
            os.remove(temp_image_path)
            os.remove(temp_audio_path)
            
            print(f"Video created successfully at: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error creating video: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    # Create a video generator instance
    generator = SimpleVideoGenerator()
    
    # Generate a video with some text
    text = input("enter the text you want to create video of ")
    generator.create_video(text, "output_video.mp4")