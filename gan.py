import os
from PIL import Image
import numpy as np
import cv2
from moviepy.editor import (
    VideoFileClip, 
    AudioFileClip, 
    ImageClip, 
    concatenate_videoclips,
    CompositeAudioClip  # Added this import
)
from gtts import gTTS
from typing import List, Dict, Tuple
import subprocess
import sys

def check_dependencies():
    """Check and install required dependencies."""
    required_packages = {
        'pydub': 'pydub',
        'SpeechRecognition': 'speech_recognition',
        'moviepy': 'moviepy',
        'Pillow': 'PIL',
        'numpy': 'numpy',
        'opencv-python': 'cv2',
        'gTTS': 'gtts'
    }
    
    missing_packages = []
    
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"Successfully installed {package}")
            except subprocess.CalledProcessError:
                print(f"Failed to install {package}. Please install it manually using:")
                print(f"pip install {package}")
                sys.exit(1)
    
    # After installing, import the required packages
    global AudioSegment, sr
    from pydub import AudioSegment
    import speech_recognition as sr

# Run dependency check at module level
check_dependencies()

class MultimediaProcessor:
    def __init__(self, output_dir: str = "output"):
        """Initialize the multimedia processor with output directory."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def text_to_speech(self, dialogue_dict: Dict[str, str], lang: str = 'en') -> Dict[str, str]:
        """
        Convert dialogue text to speech files.
        
        Args:
            dialogue_dict: Dictionary with scene IDs and corresponding dialogue text
            lang: Language code for text-to-speech
            
        Returns:
            Dictionary mapping scene IDs to voice-over audio file paths
        """
        voice_overs = {}
        for scene_id, text in dialogue_dict.items():
            output_path = os.path.join(self.output_dir, f"voice_{scene_id}.mp3")
            tts = gTTS(text=text, lang=lang)
            tts.save(output_path)
            voice_overs[scene_id] = output_path
        return voice_overs

    def process_background_music(self, music_path: str, duration: float, 
                               volume: float = 0.5) -> str:
        """
        Process background music for the video.
        
        Args:
            music_path: Path to background music file
            duration: Required duration in seconds
            volume: Volume level (0.0 to 1.0)
            
        Returns:
            Path to processed background music file
        """
        try:
            audio = AudioSegment.from_file(music_path)
            
            # Loop if audio is shorter than required duration
            while len(audio) < duration * 1000:  # pydub works in milliseconds
                audio = audio + audio
                
            # Trim to exact duration
            audio = audio[:int(duration * 1000)]
            
            # Adjust volume
            audio = audio - (20 * (1 - volume))  # Reduce volume by dB
            
            output_path = os.path.join(self.output_dir, "background_music.mp3")
            audio.export(output_path, format="mp3")
            return output_path
        except Exception as e:
            print(f"Error processing background music: {str(e)}")
            return None

    def create_video_from_images(self, image_paths: List[str], 
                               frame_duration: float = 3.0) -> str:
        """
        Create video from a sequence of images.
        
        Args:
            image_paths: List of paths to image files
            frame_duration: Duration for each frame in seconds
            
        Returns:
            Path to output video file
        """
        try:
            clips = []
            for img_path in image_paths:
                image_clip = ImageClip(img_path).set_duration(frame_duration)
                clips.append(image_clip)
                
            final_clip = concatenate_videoclips(clips)
            output_path = os.path.join(self.output_dir, "output_video.mp4")
            final_clip.write_videofile(output_path, fps=24)
            return output_path
        except Exception as e:
            print(f"Error creating video from images: {str(e)}")
            return None

    def combine_audio_video(self, video_path: str, 
                          voice_overs: Dict[str, str], 
                          background_music_path: str) -> str:
        """
        Combine video with voice-overs and background music.
        
        Args:
            video_path: Path to video file
            voice_overs: Dictionary mapping scene IDs to voice-over audio paths
            background_music_path: Path to background music file
            
        Returns:
            Path to final video with audio
        """
        try:
            video = VideoFileClip(video_path)
            bg_music = AudioFileClip(background_music_path)
            
            # Combine all voice-overs
            voice_clips = []
            current_time = 0
            for scene_id, audio_path in voice_overs.items():
                voice = AudioFileClip(audio_path)
                voice = voice.set_start(current_time)
                voice_clips.append(voice)
                current_time += voice.duration
                
            # Mix background music with voice-overs
            final_audio = CompositeAudioClip([bg_music] + voice_clips)
            final_video = video.set_audio(final_audio)
            
            output_path = os.path.join(self.output_dir, "final_video.mp4")
            final_video.write_videofile(output_path)
            return output_path
        except Exception as e:
            print(f"Error combining audio and video: {str(e)}")
            return None

    def transcribe_video(self, video_path: str) -> str:
        """
        Generate transcription from video audio.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Transcribed text
        """
        try:
            video = VideoFileClip(video_path)
            audio_path = os.path.join(self.output_dir, "temp_audio.wav")
            video.audio.write_audiofile(audio_path)
            
            recognizer = sr.Recognizer()
            transcription = []
            
            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio)
                    transcription.append(text)
                except sr.UnknownValueError:
                    print("Speech recognition could not understand the audio")
                except sr.RequestError:
                    print("Could not request results from speech recognition service")
                    
            os.remove(audio_path)  # Clean up temporary file
            return " ".join(transcription)
        except Exception as e:
            print(f"Error transcribing video: {str(e)}")
            return ""

    def summarize_dialogue(self, text: str, max_length: int = 100) -> str:
        """
        Create a summary of dialogue text.
        
        Args:
            text: Input text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summarized text
        """
        try:
            sentences = text.split('.')
            summary = []
            current_length = 0
            
            for sentence in sentences:
                if current_length + len(sentence) <= max_length:
                    summary.append(sentence)
                    current_length += len(sentence)
                else:
                    break
                    
            return '. '.join(summary) + '.'
        except Exception as e:
            print(f"Error summarizing dialogue: {str(e)}")
            return text

def main():
    # Example usage
    processor = MultimediaProcessor()
    
    # Sample dialogue
    dialogues = {
        "scene1": "Welcome to our presentation about machine learning.",
        "scene2": "Let's explore the fascinating world of artificial intelligence.",
    }
    
    # Sample image paths
    image_paths = ["image1.jpg", "image2.jpg"]
    
    # Create voice-overs
    voice_overs = processor.text_to_speech(dialogues)
    
    # Process background music
    bg_music = processor.process_background_music(
        "background.mp3", 
        duration=len(image_paths) * 3,  # 3 seconds per image
        volume=0.3
    )
    
    if bg_music is None:
        print("Failed to process background music. Exiting.")
        return
    
    # Create video from images
    video_path = processor.create_video_from_images(image_paths)
    
    if video_path is None:
        print("Failed to create video from images. Exiting.")
        return
    
    # Combine everything
    final_video = processor.combine_audio_video(
        video_path, 
        voice_overs, 
        bg_music
    )
    
    if final_video is None:
        print("Failed to combine audio and video. Exiting.")
        return
    
    # Generate transcription
    transcription = processor.transcribe_video(final_video)
    
    # Create summary
    summary = processor.summarize_dialogue(transcription)
    
    print(f"Final video created: {final_video}")
    print(f"Transcription: {transcription}")
    print(f"Summary: {summary}")

if __name__ == "__main__":
    main()