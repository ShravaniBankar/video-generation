import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
import cv2

class IntegratedVideoGenerator:
    def __init__(self, width=1280, height=720, output_dir="output"):
        self.width = width
        self.height = height
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def create_text_image(self, text, font_size=60):
        """Create an image with text and random background color"""
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
    
    def create_text_video(self, text, duration=5, output_filename="text_video.mp4"):
        """Create a video with text and speech"""
        try:
            # Create text image
            image = self.create_text_image(text)
            temp_image_path = os.path.join(self.output_dir, "temp_frame.png")
            image.save(temp_image_path)
            
            # Generate speech
            temp_audio_path = os.path.join(self.output_dir, "temp_audio.mp3")
            tts = gTTS(text=text, lang='en')
            tts.save(temp_audio_path)
            
            # Create video clip
            image_clip = ImageClip(temp_image_path).set_duration(duration)
            audio_clip = AudioFileClip(temp_audio_path)
            
            video = image_clip.set_audio(audio_clip)
            output_path = os.path.join(self.output_dir, output_filename)
            
            video.write_videofile(output_path, fps=24)
            
            # Clean up temporary files
            os.remove(temp_image_path)
            os.remove(temp_audio_path)
            
            print(f"Video created successfully: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error creating video: {str(e)}")
            return None
    
    def create_multi_text_video(self, text_list, output_filename="multi_text_video.mp4"):
        """Create a video with multiple text slides"""
        try:
            clips = []
            duration_per_text = 3
            
            for i, text in enumerate(text_list):
                # Create image with text
                text_image = self.create_text_image(text)
                temp_image_path = os.path.join(self.output_dir, f"temp_frame_{i}.png")
                text_image.save(temp_image_path)
                
                # Create clip
                clip = ImageClip(temp_image_path).set_duration(duration_per_text)
                clip = clip.set_start(i * duration_per_text)
                clip = clip.fadeout(1).fadein(1)
                
                clips.append(clip)
                os.remove(temp_image_path)
            
            # Generate speech
            temp_audio_path = os.path.join(self.output_dir, "temp_multi_audio.mp3")
            tts = gTTS(text=" ".join(text_list), lang='en')
            tts.save(temp_audio_path)
            
            # Combine clips
            final_clip = CompositeVideoClip(clips)
            audio_clip = AudioFileClip(temp_audio_path)
            final_clip = final_clip.set_audio(audio_clip)
            
            # Write video
            output_path = os.path.join(self.output_dir, output_filename)
            final_clip.write_videofile(output_path, fps=24)
            
            os.remove(temp_audio_path)
            
            print(f"Multi-text video created: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error creating multi-text video: {str(e)}")
            return None
    
    def create_image_video(self, image_paths, frame_duration=3.0, output_filename="image_video.mp4"):
        """Create a video from a sequence of images"""
        try:
            clips = []
            for img_path in image_paths:
                if not os.path.exists(img_path):
                    raise FileNotFoundError(f"Image file not found: {img_path}")
                
                image_clip = ImageClip(img_path).set_duration(frame_duration)
                clips.append(image_clip)
            
            final_clip = concatenate_videoclips(clips)
            output_path = os.path.join(self.output_dir, output_filename)
            final_clip.write_videofile(output_path, fps=24)
            
            print(f"Image video created: {output_path}")
            return output_path
        
        except Exception as e:
            print(f"Error creating image video: {str(e)}")
            return None

def main():
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Initialize video generator
    generator = IntegratedVideoGenerator()
    
    # Example 1: Single text video
    generator.create_text_video("Welcome to our presentation")
    
    # Example 2: Multi-text video
    generator.create_multi_text_video([
        "This is slide 1",
        "Second slide content",
        "Final slide coming up"
    ])
    
    # Example 3: Image video (assuming sample images exist)
    sample_images = [
        "output/image1.jpg", 
        "output/image2.jpg"
    ]
    generator.create_image_video(sample_images)

if __name__ == "__main__":
    main()