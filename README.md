# PyMedusa VideoConverter

**Video Converter** is a script designed to be run with pymedusa and ffmpeg on linux, other systems may or may not work
- https://pymedusa.com/
- https://www.ffmpeg.org/
 
## How to use
- Download and place the script into a known directory
- The script will be run after Medusas own post processing
- Modify any settings inside the script as desired
- Enter the script path in Medusa
    - For Windows C:\Python36\pythonw.exe C:\Script\test.py
    - For Linux: python /Script/test.py
- The script uses args passed by medusa
    - Found here: https://github.com/pymedusa/Medusa/wiki/Post-Processing#extra-scripts

## Defaults
    DESIRED_VIDEO_CODEC = "h264"  # Default is h264
    DESIRED_AUDIO_CODEC = "aac"  # Default is aac
    
    MAX_WIDTH = 854  # Default is 854
    MAX_HEIGHT = 480  # Default is 480
    
    OUT_VLIB = "libx264"  # Default is libx264
    OUT_ALIB = "aac"  # Default is aac
    OUT_EXTENSION = ".mp4"  # Default is .mp4
    MKV_EXTENSION = ".mkv"  # Default is .mkv
    TEMP_EXTENSION = ".tmp.mp4"  # Default is .tmp.mp4
    
    PRESET = "fast"  # Visit https://trac.ffmpeg.org/wiki/Encode/H.264
    CRF = "22"  # For an explanation on what do to with these variables

## Credit
>_Designed by my father for personal use, I merely helped him with python syntax and cleaned up the code_
