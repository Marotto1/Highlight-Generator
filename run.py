from moviepy.video.io.VideoFileClip import VideoFileClip
import os

os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

clip = VideoFileClip("test_in.mp4")
clipped = clip.subclip(10, 20)
clipped.write_videofile("test_out.mp4", codec="libx264")
