
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
#from ui_dldialog import Ui_DLDialog
from PyQt5.uic import loadUi
import sys
import subprocess
from waitingspinnerwidget import QtWaitingSpinner
from time import sleep
import threading
import os 


class MainWindow(QDialog):
    
    # Debug Filepath. TODO: Remove later
    filepath = ["C:/Users/David/Desktop/hackathon-2023/OSR_us_000_0010_8k.wav"]
    
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Lecture Transcription")
        loadUi("browsefile.ui", self)
        self.browseButton.clicked.connect(self.browsefiles)
        #self.label_finished.hide()
        
        # Create Busy Indicator. TODO Fix scuffed positioning
        self.spinner = QtWaitingSpinner(self, False, True, Qt.ApplicationModal)  
        self.spinner.move(165,150)   
        
        self.pushButton.clicked.connect(self.spinIt)
        self.startButton.clicked.connect(self.startTranscipt)

        self.textButton.clicked.connect(self.setTranscriptBox)
        
        #Experimental QProcess stuff
        self.process = QProcess(self)
        self.process.readyRead.connect(self.updateTranscriptBox)
        self.process.finished.connect(self.transcriptFinished)
        
        
        
        
    
    # Browse File Dialog
    def browsefiles(self):
 
        self.filename = QFileDialog.getOpenFileName(self, "Select Lecture" )
        self.filepath = self.filename
        self.selectedFile.setText(self.filepath[0])
        filename = self.filepath[0].split("/")
        self.file = filename[-1]  

        
        
    
    #Main Transcription Process
    def startTranscipt(self):
        self.spinner.start()
        language = self.comboBox.currentText()
        print("Language selected: " + language)
        self.transcriptBox.append(str("Starting Whisper.."))
        self.transcriptBox.setEnabled(False)
        self.process.start('whisper', [self.filepath[0], '--model',  'base', '--language' ,language, '--output_format',  'vtt', '--task', 'transcribe'])
        self.transcriptBox.append(str("---Transcript Start---\n"))
        print('whisper ' + self.filepath[0] + " --model base --language '" + language +  "' --output_format vtt --task transcribe")
        
    
    def transcriptFinished(self):
        self.transcriptBox.append(str("---Transcript End---"))
        subprocess.run("ffmpeg -i " + self.file +" -i " + self.file[:-4] + ".vtt -c copy -c:s mov_text -metadata:s:s:0 language=eng " + self.file[:-4] + "_subtitled.mp4")
        print("ffmpeg -i " + self.file +" -i " + self.file[:-4] + ".vtt -c copy -c:s mov_text -metadata:s:s:0 language=eng " + self.file[:-4] + "_subtitled.mp4")
        self.spinner.stop()
    
    # TODO Remove Later
    def spinIt(self):
        print(self.verticalLayout.geometry())
        if self.spinner._isSpinning:
            self.spinner.stop()
        else:
            self.spinner.start()

    # TODO Remove Later
    def setTranscriptBox(self):
        if self.transcriptBox.isHidden():
            print("Disable!")
            self.transcriptBox.setHidden(False)
        else:
            print("Enable!")
            self.transcriptBox.setHidden(True)
          
    # Refresh Log Window  
    def updateTranscriptBox(self):
        cursor = self.transcriptBox.textCursor()
        cursor.movePosition(cursor.End)
        
        self.consoleOutput = str(self.process.readAll())
        print("Appending: " + self.consoleOutput)
        self.consoleOutput = self.consoleOutput.replace("]", "] <br>")
        self.consoleOutput = self.consoleOutput.replace("[", "<br><br>[")
        self.consoleOutput = self.consoleOutput.replace("\r\n", "REEE")
        self.transcriptBox.append(self.consoleOutput)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwin = MainWindow()
    #ui = Ui_DLDialog
    #ui.setupUi(ui, mainwin)
    mainwin.show()
    
    sys.exit(app.exec_())
    