import os
import subprocess
import cv2
import yt_dlp
import uuid

# Define temporary folders
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
FRAMES_DIR = os.path.join(TEMP_DIR, "frames")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)

def download_video(url: str) -> str:
    """Download video locally into /temp folder using yt-dlp."""
    video_id = str(uuid.uuid4())
    output_template = os.path.join(TEMP_DIR, f"{video_id}.%(ext)s")
    
    # We download lowest quality video for faster testing and since we just need frames + audio
    ydl_opts = {
        'format': 'worstvideo[ext=mp4]+worstaudio[ext=m4a]/mp4',
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Find the downloaded file path
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                # sometimes prepare_filename doesn't return the exact path for merged formats
                filename = os.path.join(TEMP_DIR, f"{video_id}.mp4")
                
            # Extract video description for NLP scanning (often contains the exact ingredients)
            description = info.get("description", "")
            
            return filename, description
    except Exception as e:
        raise Exception(f"Failed to download video: {e}")

def extract_audio(video_path: str) -> str:
    """Extract audio from video as .wav using ffmpeg."""
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = os.path.join(TEMP_DIR, f"{base_name}.wav")
    
    command = [
        "ffmpeg",
        "-y",               # Overwrite existing
        "-i", video_path,   # Input file
        "-vn",              # Disable video
        "-acodec", "pcm_s16le", # WAV format
        "-ar", "16000",     # 16kHz sample rate (good for AI/Whisper)
        "-ac", "1",         # Mono channel
        audio_path
    ]
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return audio_path
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to extract audio using ffmpeg: {e}")

def extract_frames(video_path: str) -> list[str]:
    """Extract 1 frame every 2 seconds using OpenCV and save to /temp/frames/."""
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    video_frames_dir = os.path.join(FRAMES_DIR, base_name)
    os.makedirs(video_frames_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception(f"Failed to open video file for frame extraction: {video_path}")
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = 30 # default assumption

    frame_interval = int(fps * 2) # Every 2 seconds
    
    frame_paths = []
    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            frame_filename = os.path.join(video_frames_dir, f"frame_{saved_count:04d}.jpg")
            cv2.imwrite(frame_filename, frame)
            frame_paths.append(frame_filename)
            saved_count += 1
            
        frame_count += 1
        
    cap.release()
    return frame_paths
