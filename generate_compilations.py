import os, shutil, glob, subprocess, json
from datetime import datetime

class video_operations:

    def __init__(self):
        dirs = ["Compilations", "Shorts_compilations", "Shorts_compilations_vertical_format", "Used_videos"]
        for dir in dirs:
            if not os.path.exists(dir):
                os.mkdir(dir)
                
    def video_duration(self, filename):
        result = subprocess.check_output(
            f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{filename}"',
            shell=True).decode()
        fields = json.loads(result)['streams'][0]
        return float(fields['duration'])

    def concat_videos(self, video_list=[], output_dir=""):
        output_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f") + ".mp4"
        list_path = output_name + ".txt"
        with open(list_path, "w") as f:
            for video in video_list:
                f.write("file " + video + "\n")
        output_path = output_dir + "\\" + output_name
        
        os.system("ffmpeg -f concat -i " + list_path + " -safe 0 -c:v h264_nvenc -preset 18 -c:a aac -vcodec copy -af aselect=1 " + output_path)
        cut_duration = "00:" + datetime.fromtimestamp(video_operations.video_duration(self, filename=output_path)).strftime("%M:%S.%f")
        os.system("ffmpeg -ss 00:00:01.0 -accurate_seek -i " + output_path + " -c:v h264_nvenc -preset 18 -c:a aac -t " + cut_duration + " -acodec copy -vcodec copy -qscale 0 " + output_path + "_fixed.mp4")
        os.remove(output_path)
        os.remove(list_path)

    def generate_compilation(self, video_ext="mp4", compilation_max_duration_in_seconds=45, output_path=""):
        videos = sorted(glob.glob("*" + video_ext))
        duration_counter = 0
        videos_to_concat = []
        for video in videos:
            duration = video_operations.video_duration(self, filename=video)
            duration_counter += duration
            
            if duration_counter <= compilation_max_duration_in_seconds:
                videos_to_concat.append(video)
                if video == videos[-1]:
                    video_operations.concat_videos(self, video_list=videos_to_concat, output_dir=output_path)
            elif len(videos_to_concat) > 0:
                video_operations.concat_videos(self, video_list=videos_to_concat, output_dir=output_path)
                duration_counter = duration
                videos_to_concat.clear()
                videos_to_concat.append(video)

    def move_used_videos(self):
        for video in glob.glob("*.mp4"):
            shutil.move(video, "Used_videos\\" + video)

    def create_short_format(self):
        for video in glob.glob("Shorts_compilations\\*.mp4"):
            webcam_h = '260'
            webcam = '[0:v]crop=in_h:'+webcam_h+':0:in_h[v0];'
            gameplay = '[1:v]crop=in_h:in_h-'+webcam_h+'[v1];'
            stack = '[v0][v1]vstack'
            command = 'ffmpeg -i ' + video + ' -i ' + video + ' -filter_complex "' + webcam + gameplay + stack + '" -c:v h264_nvenc -preset 18 -c:a aac Shorts_compilations_vertical_format/short_' + os.path.basename(video)
            os.system(command)

obj = video_operations()
obj.generate_compilation(video_ext="mp4", 
                        compilation_max_duration_in_seconds=45, 
                        output_path="Shorts_compilations")

obj.generate_compilation(video_ext="mp4", 
                        compilation_max_duration_in_seconds=480, 
                        output_path="Compilations")

obj.create_short_format()
obj.move_used_videos()

print("finish ...")