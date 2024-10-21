from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips
from nba_api.stats.endpoints import playbyplay
from datetime import datetime
import os
import cv2
import pprint

# Set the path for ffmpeg
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

def make_clips(timestamps):
    clips = []
    clip = VideoFileClip("test_in.mp4")
    
    for timestamp in timestamps:
        # Ensure timestamp is valid
        if timestamp >= 0 and timestamp + 10 <= clip.duration:
            clipped = clip.subclip(timestamp, timestamp + 10)
            clips.append(clipped)

    # Combine all clips into one video
    if clips:
        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile("highlights.mp4", codec="libx264")

def display_video(video_path):
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Highlights', frame)

        # Press 'q' to exit the video window
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def make_api_call(user_game_id):
    data = playbyplay.PlayByPlay(game_id=user_game_id).get_dict()    
    plays = data['resultSets'][0]['rowSet']
    new_plays = []
    for play in plays:
        event = play[7] or play[8] or play[9] 
        if event:
            new_plays.append({
                "time": play[5],  # Play time
                "event": event
            })
    return new_plays

def check_play(play):
    good_keywords = ["puts it in", "3", "drains", "makes", "made", "bucket", "2", "score"]
    bad_keywords = ["miss", "off", "airball", "block", "stolen", "clank"]
    
    if any(keyword in play["event"].lower() for keyword in good_keywords) and not any(keyword in play["event"].lower() for keyword in bad_keywords):
        return True
    return False

def get_timestamp(play):
    try:
        # Assuming play["time"] is in "hh:mm AM/PM" format
        time_str = play["time"]
        # Convert the time string to a datetime object
        time_obj = datetime.strptime(time_str, '%I:%M %p')
        # Convert the datetime object to seconds since midnight
        return time_obj.hour * 3600 + time_obj.minute * 60
    except Exception as e:
        print(f"Error parsing timestamp: {e}")
        return 0

if __name__ == "__main__":
    user_game_id = input("Enter the game id: ")
    plays = make_api_call(user_game_id)
    
    timestamps = []
    
    for play in plays:
        if check_play(play):
            timestamp = get_timestamp(play)
            if timestamp > 0:
                print(f"Good play at {timestamp} seconds")
                timestamps.append(timestamp)
    
    # Create highlight clips from collected timestamps
    make_clips(timestamps)

    # Display the generated highlights video
    display_video('highlights.mp4')
    
    pprint.pprint(plays)
