import yt_dlp
from pydub import AudioSegment
import os
from pathlib import Path
Download_directory="downloads"
os.makedirs(Download_directory,exist_ok=True)

def download_youtube_audio(url:str)->str:
    output_path = os.path.join(Download_directory, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = str(Path(ydl.prepare_filename(info)).with_suffix(".wav"))
    return filename

def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz
    audio.export(output_path, format="wav")
    return output_path

# chunking

def chunking(wav_path:str,chunk_minutes:int =10)->list:
    audio=AudioSegment.from_wav(wav_path)
    chunk_ms=chunk_minutes*60*1000
    chunks=[]
    for i,start in enumerate(range(0,len(audio),chunk_ms)):
        chunk=audio[start:start+chunk_ms]
        chunk_path=f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path,format="wav")
        chunks.append(chunk_path)
    
    return chunks

def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunking(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks
