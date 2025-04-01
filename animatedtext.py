from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from gtts import gTTS 
import os
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip

class SimpleVideoGenerator:
    def __init__(self):
        self.width = 1280
        self.height = 720
        self.background_color = (255, 255, 255)  # White
        self.text_color = (0, 0, 0)  # Black
        
    def create_text_image(self, text, font_size=60):
        """Create a PIL Image with text"""
        # Create blank image
        image = Image.new('RGB', (self.width, self.height), self.background_color)
        draw = ImageDraw.Draw(image)
        
        # Try to use Arial font, fall back to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Calculate text size and position
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Center the text
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2
        
        # Draw text
        draw.text((x, y), text, font=font, fill=self.text_color)
        
        return image
    
    def create_video(self, text, duration=5, output_path="output.mp4"):
        """Create a simple video with text and speech"""
        try:
            # Create image with text
            text_image = self.create_text_image(text)
            
            # Convert PIL image to MoviePy clip
            clip = ImageClip(np.array(text_image))
            clip = clip.set_duration(duration)
            
            # Add fade in/out effects
            clip = clip.fadeout(1).fadein(1)
            
            # Generate speech
            temp_audio = "temp_audio.mp3"
            tts = gTTS(text=text, lang='en')
            tts.save(temp_audio)
            
            # Add audio
            audio = AudioFileClip(temp_audio)
            final_clip = clip.set_audio(audio)
            
            # Write video
            final_clip.write_videofile(output_path, fps=24)
            
            # Clean up
            os.remove(temp_audio)
            
            print(f"Video created successfully: {output_path}")
            return True
        
        except Exception as e:
            print(f"Error creating video: {str(e)}")
            return False
    
    def create_multi_text_video(self, text_list, output_path="output.mp4"):
        """Create a video with multiple text segments"""
        try:
            clips = []
            duration_per_text = 3
            
            # Create clip for each text
            for i, text in enumerate(text_list):
                # Create image with text
                text_image = self.create_text_image(text)
                
                # Convert to MoviePy clip
                clip = ImageClip(np.array(text_image))
                clip = clip.set_duration(duration_per_text)
                clip = clip.set_start(i * duration_per_text)
                clip = clip.fadeout(1).fadein(1)
                
                clips.append(clip)
            
            # Combine all clips
            final_clip = CompositeVideoClip(clips)
            
            # Generate speech
            temp_audio = "temp_audio.mp3"
            tts = gTTS(text=" ".join(text_list), lang='en')
            tts.save(temp_audio)
            
            # Add audio
            audio = AudioFileClip(temp_audio)
            final_clip = final_clip.set_audio(audio)
            
            # Write video
            final_clip.write_videofile(output_path, fps=24)
            
            # Clean up
            os.remove(temp_audio)
            
            print(f"Video created successfully: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error creating video: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    generator = SimpleVideoGenerator()
    
    # Create single text video
    generator.create_video(
        text="Welcome to my video!",
        duration=5,
        output_path="simple_video.mp4"
    )
    
    # Create multi-text video
    generator.create_multi_text_video(
        text_list=[
            "Welcome to our presentation",
            "This is the second slide",
            "Thank you for watching!"
        ],
        output_path="multi_text_video.mp4"
    )