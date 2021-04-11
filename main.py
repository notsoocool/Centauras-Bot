import cv2 #OpenCV
import pyautogui
import numpy as np
from pydub import AudioSegment

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.alert import Alert
import pdfkit 


from functions.login import turnOffMicCam,AskToJoin,Glogin,joinNow
from functions.attendance import attendance
from functions.createpdf import createpdf
from functions.screenshots import screenshot
from functions.similarity import similarity
from functions.audio_recording import record2
from functions.orb_sim import print_save_final_images
from functions.orb_sim import orb_sim
from harassment_checker.LogisticRegression.Predict import predict
# from harassment_checker.LSTM.Predict import predict

from Summary.summary import create_summary_file
from Summary.voiceToText import generateText

from time import time, sleep
from datetime import datetime
from functions.audio import record
import speech_recognition as sr
import io, time, sys, os
import threading
import js2py
from win10toast import ToastNotifier
import sys

#ADD CREDENTIALS OF BOT HERE
CREDS = {'email' : sys.argv[1], 'passwd': sys.argv[2]}
name = sys.argv[3]
meeting_id = sys.argv[4]
meeting_end = False


opt = Options()
opt.add_argument("--disable-infobars")
opt.add_argument("--mute-audio")
opt.add_argument("start-maximized")
opt.add_argument("enable-usermedia-screen-capturing")
opt.add_experimental_option('excludeSwitches', ['test-type'])
opt.add_experimental_option("prefs", {
    "profile.default_content_setting_values.media_stream_mic": 1,
    "profile.default_content_setting_values.media_stream_camera": 1,
    "profile.default_content_setting_values.geolocation": 1,
    "profile.default_content_setting_values.notifications": 1
})

driver= webdriver.Chrome()

def check():
    
    AUDIO_FILE = ("recording1.wav")   # use the audio file as the audio source 
    
    r = sr.Recognizer() 
    print()
    with sr.AudioFile(AUDIO_FILE) as source: 
        r.adjust_for_ambient_noise(source=source)
        audio = r.record(source)  
                
        try: 
            text = r.recognize_google(audio)#houndify(audio, client_id="M06R66L3BmYqpaohS8jxVA==", client_key="Pb6vejVFbEhXCs7PU4-VZDjTKGW2F_VzS3cc1FgSvIPdaDLN1NFNJj4KbW26zVGzDRSvR4tcIm7NskyVd-APbQ=="))        
            print(text)
            if (text.find(name) == -1):
                print("NO")
            else:
                print("YES")
                toaster = ToastNotifier()
                toaster.show_toast("Google Meet Notification","Your name has been called in the meeting!!!")
        except sr.UnknownValueError: 
            pass# print("Audio is not Clear") 
            
        except sr.RequestError as e: 
            pass# print("Try Again; {0}".format(e))


def name_notifier():
    while True:
        record()
        th = threading.Thread(target=check, args=())
        th.start()


def attendance_list(): # attendance is taken at a interval of 60 minutes
    from time import time, sleep
    file = open("Attendance.txt","w+") 
    file.write("Attendance List\n")

    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        people = attendance(driver)
        file = open("Attendance.txt","a") 
        file.readline()
        file.write('Taken at time : ',current_time)
        file.write('\n')
        for i in people:
            file.write(i+'\n')
        file.close()
        sleep(300*6)


def record_audio():
    record2()


def record_video():
    codec = cv2.VideoWriter_fourcc(*"XVID")

    out = cv2.VideoWriter("Recorded.avi", codec , 19, (1920, 1080)) #Here screen resolution is 1366 x 768, you can change it depending upon your need

    cv2.namedWindow("Recording", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Recording", 480, 270) #Here we are resizing the window to 480x270 so that the program doesn't run in full screen in the beginning

    global meeting_end
    while meeting_end == False:
        img = pyautogui.screenshot() #capturing screenshot
        frame = np.array(img) #converting the image into numpy array representation 
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #converting the BGR image into RGB image
        out.write(frame) #writing the RBG image to file
        cv2.imshow('Recording', frame) #display screen/frame being recorded
        if cv2.waitKey(1) == ord('q'): #Wait for the user to press 'q' key to stop the recording
            break

    out.release() #closing the video file
    cv2.destroyAllWindows() #destroying the recording window


def take_screenshot():
    global meeting_end
    while meeting_end == False:
        screenshot()
        
        img1 = cv2.imread('./images/screenshot.png')
        img2 = cv2.imread('./images/to_compare.png')
        value = orb_sim(img1, img2)
        if value>=0.8:
            meeting_end = True
            return

        sleep(30) 



def functions():
    
    notifier_thread = threading.Thread(target=name_notifier, args=())
    notifier_thread.start()
    
    attendance_thread = threading.Thread(target=attendance_list, args=())
    attendance_thread.start()

    video_thread = threading.Thread(target=record_video, args=())
    video_thread.start()

    audio_thread = threading.Thread(target=record_audio, args=())
    audio_thread.start()

    screenshot_thread = threading.Thread(target=take_screenshot, args=())
    screenshot_thread.start()
        
    
    global meeting_end
    while meeting_end == False:
        sleep(30)

    print('MeetingEnded')
    driver.close()

    end_time = print_save_final_images()

    sleep(300)
    end_time = [0,12,24,36,114]
    t1 = 0
    t2 = 0
    k = 0
    for t in end_time:
        t2 = t
        newAudio = AudioSegment.from_wav("./recording002.wav")
        newAudio = newAudio[t1*1000:t2*1000]
        newAudio.export('./audio/recording'+str(k)+'.wav', format="wav") #Exports to a wav file in the current path.
        k = k+1
        t1 = t2

    k = 0
    for filename in os.listdir('E:/WEB_DEVELOPMENT/selenium/centauras_bot/audio'):
        generateText('E:/WEB_DEVELOPMENT/selenium/centauras_bot/audio/'+filename, k)
        create_summary_file(k)
        k = k+1

    doc = '''<!DOCTYPE html>
    <html lang="en">

    <head>
    <title>Notes</title>
    </head>

    <body>'''
    
    file = open('doc.html','a')
    file.write(doc+'\n')
    file.close()

    doc = ' <h1>Notes</h1>'

    file = open('doc.html','a')
    file.write(doc+'\n')
    file.close()

    k = 0
    summary_text = ''
    for filename in os.listdir('E:/WEB_DEVELOPMENT/selenium/centauras_bot/images/data'):
        try:
            f = open("E:/WEB_DEVELOPMENT/selenium/centauras_bot/Text/Textsummary"+str(k)+".txt")
            fileContent = f.read()  
            doc = ' <h1>'+fileContent+'</h1>'

            file = open('doc.html','a')
            file.write(doc+'\n')
            file.close()
            f.close()
            summary_text = summary_text + " " + fileContent
        except IOError:
            print("File not accessible")
        
        loc = 'E:/WEB_DEVELOPMENT/selenium/centauras_bot/images/data/'+filename
        k = k+1
        doc = ' <img src=\''+loc+'\' alt="Description for image" width="1000" height="800">'

        file = open('doc.html','a')
        file.write(doc+'\n')
        file.close()

        doc = ' <h1>'+str(end_time[k-1]/60)+' minutes: </h1>'

        file = open('doc.html','a')
        file.write(doc+'\n')
        file.close()


    doc = '''
    </body>
    </html>
    '''

    file = open('doc.html','a')
    file.write(doc+'\n')
    file.close()

    path_wkhtmltopdf ='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe' #'C:/Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdfkit.from_file("./doc.html", "E:/WEB_DEVELOPMENT/selenium/centauras_bot/Text/output.pdf", configuration=config) 

    if len(summary_text) > 0:    
        hm = predict([summary_text])
        ans = ''
        if hm[0] == '1':
            ans = 'Harassment detected'
        else:
            ans = 'No Harassment detected'
        
        doc = '''<!DOCTYPE html>
        <html lang="en">

        <head>
        <title>Notes</title>
        </head>

        <body>'''
        
        file = open('doc2.html','a')
        file.write(doc+'\n')
        file.close()
        doc2 = ' <h1>'+ans+' minutes: </h1>'

        file = open('doc2.html','a')
        file.write(doc+'\n')
        file.close()
        doc = '''
        </body>
        </html>
        '''

        file = open('doc2.html','a')
        file.write(doc+'\n')
        file.close()       

        path_wkhtmltopdf ='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe' #'C:/Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
        pdfkit.from_file("./doc2.html", "E:/WEB_DEVELOPMENT/selenium/centauras_bot/Text/output.pdf", configuration=config) 
    

    
Glogin(CREDS['email'], CREDS['passwd'],driver)
driver.get('https://meet.google.com/'+meeting_id)

time.sleep(2)
# turnOffMicCam(driver)
# driver.implicitly_wait(15)
# joinNow(driver)
# driver.implicitly_wait(10)
# time.sleep(5)

driver.find_element_by_xpath('//*[@id="yDmH0d"]/div[3]/div/div[2]/div[3]/div').click()

try:
    WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                   'Timed out waiting for PA creation ' +
                                   'confirmation popup to appear.')

    alert = driver.switch_to.alert
    alert.accept()
    print("alert accepted")
except:
    print("no alert")

time.sleep(8)
functions()

