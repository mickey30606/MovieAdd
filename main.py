from PyQt5.QtWidgets import (QMainWindow, QApplication, QFileDialog, QMessageBox)
from UI import Ui_MainWindow
from PyQt5.QtCore import (pyqtSignal)
import sys
import os
import subprocess
import re
from moviepy.editor import *


class MainWindow(QMainWindow):
    videoPath = ""
    videoStartMinute = 0
    videoStartSecond = 0
    videoEndMinute = 0
    videoEndSecond = 0
    animatePath = ""
    imgPath = ""
    saveConfig = []

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # init ui
        self.ui.VideoPath.setText("尚未選擇檔案")
        self.ui.ImgPath.setText("尚未選擇檔案")
        self.ui.AnimatePath.setText("尚未選擇檔案")

        # button to slot
        self.ui.VideoLoadButton.clicked.connect(self.S_button_video_choosepath)
        self.ui.VideoCut.clicked.connect(self.S_button_video_cut)
        self.ui.ImgLoadButton.clicked.connect(self.S_button_img_choosepath)
        self.ui.AnimateLoadButton.clicked.connect(self.S_button_animate_choosepath)
        self.ui.StartButton.clicked.connect(self.S_button_start)
        # print(self.get_video_resolution('b.mp4')[0])

# functions

    def get_video_resolution(self, video_path):
        command = ['ffmpeg', '-i', video_path]

        # 执行FFmpeg命令并捕获输出
        output = ""
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode()
        except subprocess.CalledProcessError as grepexc:                                                                                                   
            # print("error code", grepexc.returncode, grepexc.output)
            output = grepexc.output.decode()

        print(output)
        # 使用正则表达式从输出中提取分辨率信息
        pattern = r" (\d+)x(\d+) "
        match = re.search(pattern, output)

        if match:
            width = int(match.group(1))
            height = int(match.group(2))
            return (width, height)
        else:
            return None
    


# slots
    def S_button_img_choosepath(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Image files (*.png)")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        if file_dialog.exec_():
            self.imgPath = file_dialog.selectedFiles()
        list_string = "\n".join(str(item) for item in self.imgPath)
        self.ui.ImgPath.setText(list_string)
        return

    def S_button_animate_choosepath(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Video files (*.mp4)")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        if file_dialog.exec_():
            self.animatePath = file_dialog.selectedFiles()
        list_string = "\n".join(str(item) for item in self.animatePath)
        self.ui.AnimatePath.setText(list_string)
        return

    def S_button_video_choosepath(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Video files (*.mp4)")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        if file_dialog.exec_():
            self.videoPath = file_dialog.selectedFiles()
        list_string = "\n".join(str(item) for item in self.videoPath)
        self.ui.VideoPath.setText(list_string)
        return


        # fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
        #                                           "All Files (*)")
        # if fileName:
        #     self.videoPath = fileName
        # self.ui.VideoPath.setText(self.videoPath)
        # return

    def S_button_start(self):
        print(self.videoPath)
        print(self.animatePath)
        print(self.imgPath)
        starttime = int(self.ui.VideoStartMinute.text())*60 + int(self.ui.VideoStartSecond.text())
        endtime = int(self.ui.VideoEndMinute.text())*60 + int(self.ui.VideoEndSecond.text())
        if starttime > endtime:
            print("start time is greater than end time !!!")
            return
        

        video = VideoFileClip(self.videoPath[0])
        intro = VideoFileClip(self.animatePath[0]).resize(height=video.h)

        if starttime == endtime:
            endtime = video.duration

        video = video.subclip(starttime, endtime)
        video = video.fx(vfx.fadeout, 2)

        logo = (ImageClip(self.imgPath[0])
                .set_duration(video.duration)
                .resize(height=300)
                .set_pos(("left", "bottom")))
        
        logo = logo.fx(vfx.fadein, 2)
        
        intro = intro.fx(vfx.mask_color, color=[0, 0, 0], thr=10)
        intro_background = video.get_frame(0)
        intro_background = ImageClip(intro_background, duration=intro.duration)
        
        newvideo = CompositeVideoClip([video, logo])
        newintro = CompositeVideoClip([intro_background, intro])

        final_video = concatenate_videoclips([newintro, newvideo])
        final_video = final_video.set_fps(video.fps).resize(video.size)

        final_video.write_videofile("./output.mp4", codec='mpeg4', bitrate='50000k', audio_codec='aac')
        return
    
    def S_button_add(self):
        if self.animatePath == "":
            print("animate path is null\n")
            return
        if self.imgPath == "":
            print("img path is null\n")
            return
        if self.videoPath == "":
            print("video path is null\n")
            return

        tmpsave = {}
        tmpsave['videoPath'] = self.videoPath
        tmpsave['animatePath'] = self.animatePath
        tmpsave['imgPath'] = self.imgPath

        starttime = int(self.ui.VideoStartMinute.text())*60 + int(self.ui.VideoStartSecond.text())
        endtime = int(self.ui.VideoEndMinute.text())*60 + int(self.ui.VideoEndSecond.text())
        tmpsave['startTime'] = starttime
        tmpsave['endTime'] = endtime


        self.video.Path = ""
        self.ui.VideoPath.setText("尚未選擇檔案")
        

    def S_button_video_cut(self):
        starttime = str(int(self.ui.VideoStartMinute.text())*60 + int(self.ui.VideoStartSecond.text()))
        endtime = str(int(self.ui.VideoEndMinute.text())*60 + int(self.ui.VideoEndSecond.text()))
        ismp4 = os.path.splitext(self.videoPath)[1] == ".mp4"
        dir = os.path.dirname(self.videoPath)
        newfilename = os.path.splitext(self.videoPath)[0] + ".mp4"
        print(newfilename)
        
        convertcmd = f"ffmpeg -i {self.videoPath} -c:v h264 -c:a aac -strict experimental -f mp4 {dir+'/tmp.mp4'}"
        command = ['ffmpeg', '-i', dir+'/tmp.mp4', '-ss', starttime, '-to', endtime, '-f', 'mp4', '-c:v', 'h264', dir + '/output.mp4']
        print(starttime + " " + endtime)
        try:
            subprocess.check_call(convertcmd)
            subprocess.check_call(command)
            os.remove(dir+'/tmp.mp4')
        except subprocess.CalledProcessError as e:
            print("Error: ", e)

        return



if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())