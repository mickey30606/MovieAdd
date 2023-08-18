from PyQt5.QtWidgets import (QMainWindow, QApplication, QFileDialog, QMessageBox, QHeaderView)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtCore import (QModelIndex)
from UI import Ui_MainWindow
from PyQt5.QtCore import (pyqtSignal)
import sys
import os
import subprocess
import re
from moviepy.editor import *
import random
import threading
import time


class MainWindow(QMainWindow):
    videoPath = ""
    videoStartMinute = 0
    videoStartSecond = 0
    videoEndMinute = 0
    videoEndSecond = 0
    animatePath = ""
    imgPath = ""
    saveConfig = {}
    head = ['id', 'videoPath', 'starttime', 'endtime', 'animatePath', 'imgPath', 'imgHeight']
    cnt = 0

    now_lock = threading.Lock()
    now = 0
    work = []

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # init ui
        self.ui.VideoPath.setText("尚未選擇檔案")
        self.ui.ImgPath.setText("尚未選擇檔案")
        self.ui.AnimatePath.setText("尚未選擇檔案")

        model = QStandardItemModel()
        for i in range(6):
            model.setHorizontalHeaderItem(i, QStandardItem(self.head[i]))
        self.ui.WorkTable.setModel(model)

        # button to slot
        self.ui.VideoLoadButton.clicked.connect(self.S_button_video_choosepath)
        self.ui.VideoCut.clicked.connect(self.S_button_video_cut)
        self.ui.ImgLoadButton.clicked.connect(self.S_button_img_choosepath)
        self.ui.AnimateLoadButton.clicked.connect(self.S_button_animate_choosepath)
        self.ui.StartButton.clicked.connect(self.S_button_start)
        self.ui.NewWork.clicked.connect(self.S_button_addWork)
        self.ui.DeleteWork.clicked.connect(self.S_button_delWork)
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
        if len(self.imgPath):
            self.imgPath = self.imgPath[0]
        self.ui.ImgPath.setText(list_string)
        return

    def S_button_animate_choosepath(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Video files (*.mp4)")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        if file_dialog.exec_():
            self.animatePath = file_dialog.selectedFiles()
        list_string = "\n".join(str(item) for item in self.animatePath)
        if len(self.animatePath):
            self.animatePath = self.animatePath[0]
        self.ui.AnimatePath.setText(list_string)
        return

    def S_button_video_choosepath(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Video files (*.mp4)")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        if file_dialog.exec_():
            self.videoPath = file_dialog.selectedFiles()
        list_string = "\n".join(str(item) for item in self.videoPath)
        if len(self.videoPath):
            self.videoPath = self.videoPath[0]
        self.ui.VideoPath.setText(list_string)
        return


        # fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
        #                                           "All Files (*)")
        # if fileName:
        #     self.videoPath = fileName
        # self.ui.VideoPath.setText(self.videoPath)
        # return
    def Dealing_thread(self):
        while True:
            self.now_lock.acquire()
            
            if self.now >= len(self.work):
                break
            deal = self.now
            self.now += 1
            self.now_lock.release()

            self.work[deal].start()
            self.work[deal].join()
        return

    def Work_thread(self, videoPath=None, starttime=None, endtime=None, animatePath=None, imgPath=None, imgHeight=None, outputPath=None):
        video = VideoFileClip(videoPath)
        intro = VideoFileClip(animatePath).resize(height=video.h)

        if starttime == endtime:
            endtime = video.duration

        video = video.subclip(starttime, endtime)
        video = video.fx(vfx.fadeout, 2)

        logo = (ImageClip(imgPath)
                .set_duration(video.duration)
                .resize(height=imgHeight)
                .set_pos(("left", "bottom")))
    
        logo = logo.fx(vfx.fadein, 2)
    
        intro = intro.fx(vfx.mask_color, color=[0, 0, 0], thr=10)
        intro_background = video.get_frame(0)
        intro_background = ImageClip(intro_background, duration=intro.duration)
    
        newvideo = CompositeVideoClip([video, logo])
        newintro = CompositeVideoClip([intro_background, intro])

        final_video = concatenate_videoclips([newintro, newvideo])
        final_video = final_video.set_fps(video.fps).resize(video.size)

        final_video.write_videofile(outputPath, codec='mpeg4', bitrate='50000k', audio_codec='aac')
        return

    def S_button_start(self):
        for k in self.saveConfig.keys():
            starttime = self.saveConfig[k]['starttime']
            endtime = self.saveConfig[k]['endtime']
            videoPath = self.saveConfig[k]['videoPath']
            animatePath = self.saveConfig[k]['animatePath']
            imgPath = self.saveConfig[k]['imgPath']
            imgHeight = self.saveConfig[k]['imgHeight']
            outputPath = videoPath.replace(videoPath.split('/')[-1], videoPath.split('/')[-1].split('.')[0] + "_" + str(int(random.random()*1000)) + "_modified.mp4")

            self.work.append(threading.Thread(target=self.Work_thread, kwargs=dict(videoPath=videoPath, starttime=starttime,endtime=endtime,animatePath=animatePath,imgPath=imgPath,imgHeight=imgHeight,outputPath=outputPath)))

            # video = VideoFileClip(videoPath)
            # intro = VideoFileClip(animatePath).resize(height=video.h)

            # if starttime == endtime:
            #     endtime = video.duration

            # video = video.subclip(starttime, endtime)
            # video = video.fx(vfx.fadeout, 2)

            # logo = (ImageClip(imgPath)
            #         .set_duration(video.duration)
            #         .resize(height=imgHeight)
            #         .set_pos(("left", "bottom")))
        
            # logo = logo.fx(vfx.fadein, 2)
        
            # intro = intro.fx(vfx.mask_color, color=[0, 0, 0], thr=10)
            # intro_background = video.get_frame(0)
            # intro_background = ImageClip(intro_background, duration=intro.duration)
        
            # newvideo = CompositeVideoClip([video, logo])
            # newintro = CompositeVideoClip([intro_background, intro])

            # final_video = concatenate_videoclips([newintro, newvideo])
            # final_video = final_video.set_fps(video.fps).resize(video.size)

            # final_video.write_videofile(outputPath, codec='mpeg4', bitrate='50000k', audio_codec='aac', threads=4)
        t = []
        tttt = int(self.ui.ThreadNum.text())
        if tttt <= 0:
            tttt  = 1
        if tttt >= 8:
            tttt = 8
        print("Threads Number: " + str(tttt))
        for i in range(tttt):
            t.append(threading.Thread(target=self.Dealing_thread))
            t[i].start()
        print("Thread start")
        for i in range(tttt):
            t[i].join()
        print("Thread end all")

        self.work.clear()
        self.now = 0
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
        if self.videoPath == "":
            print("Please choose video file!!")
            return
        starttime = str(int(self.ui.VideoStartMinute.text())*60 + int(self.ui.VideoStartSecond.text()))
        endtime = str(int(self.ui.VideoEndMinute.text())*60 + int(self.ui.VideoEndSecond.text()))

        if starttime > endtime:
            print("please enter correct time!!")
            return

        video = VideoFileClip(self.videoPath)
        video = video.subclip(starttime, endtime)

        outputPath = self.videoPath.replace(self.videoPath.split('/')[-1], self.videoPath.split('/')[-1].split('.')[0] + "_cut.mp4")
        video.write_videofile(outputPath, codec='mpeg4', bitrate='50000k', audio_codec='aac')
        return
    
    def S_button_addWork(self):
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
        starttime = int(self.ui.VideoStartMinute.text())*60 + int(self.ui.VideoStartSecond.text())
        endtime = int(self.ui.VideoEndMinute.text())*60 + int(self.ui.VideoEndSecond.text())
        imgHeight = int(self.ui.ImgHeight.text())
        if imgHeight == 0:
            imgHeight = 600
        tmpsave['starttime'] = starttime
        tmpsave['endtime'] = endtime
        tmpsave['animatePath'] = self.animatePath
        tmpsave['imgPath'] = self.imgPath
        tmpsave['videoPath'] = self.videoPath
        tmpsave['imgHeight'] = imgHeight
        tmpsave['id'] = self.cnt
        self.cnt += 1

        model = self.ui.WorkTable.model()
        rowCnt = model.rowCount()
        for i in range(len(self.head)):
            model.setItem(rowCnt, i, QStandardItem(str(tmpsave[self.head[i]])))
        self.saveConfig[tmpsave['id']] = tmpsave
        return
    
    def S_button_delWork(self):
        model = self.ui.WorkTable.model()
        selection = self.ui.WorkTable.selectionModel().selectedRows()
        qi = model.index(selection[0].row(), 0, QModelIndex())
        id = int(model.data(qi))
        self.saveConfig.pop(id)
        model.removeRow(selection[0].row())
        return



if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())