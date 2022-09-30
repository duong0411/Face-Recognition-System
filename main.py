import tkinter as tk
from tkinter import *
from tkinter import messagebox
import cv2
import tkinter
import sqlite3
import os
import socket
from PIL import Image
import PIL.ImageTk
import numpy as np
import datetime
import csv
from tkinter import filedialog
window = tk.Tk()
window.title("NHẬN DIỆN KHUÔN MẶT")
#Tạo các label
l1 = tk.Label(window,text="Name",font =("Arial",20))
l1.grid(column=0 ,row= 0)
username= tk.Entry(window,text ="",width=50,bd=5)
username.grid(column=1, row=0)

l2 = tk.Label(window,text="MSSV",font=("Arial",20))
l2.grid(column=0 ,row= 1)
mssv= tk.Entry(window,width=50,bd=5)
mssv.grid(column=1, row=1)

def generate_dataset():
    if (username.get() == "" or mssv.get() == ""):
        messagebox.showinfo('result', 'nhập tên và mã số sinh viên')
    else:
        #Mở camera và nhận diện mặt
        #url = 'http://192.168.1.4:4747/video'
        cam = cv2.VideoCapture(0)
        canvas_w = cam.get(cv2.CAP_PROP_FRAME_WIDTH) // 2
        canvas_h = cam.get(cv2.CAP_PROP_FRAME_HEIGHT) // 2

        canvas = Canvas(window, width=canvas_w, height=canvas_h, bg="red")
        detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        # Hàm cập nhật tên và ID vào CSDL
        def insertOrUpdate(id,name,date):
            conn = sqlite3.connect("C:/Users/TT/nhandienkhuonmat/FaceBaseNew2.db")
            cursor = conn.execute('SELECT * FROM people WHERE ID=' + str(id))
            isRecordExist = 0
            for row in cursor:
                isRecordExist = 1
                break

            if isRecordExist == 1:
                cmd = "UPDATE people SET Name=' " + str(name) + " ',Date='"+str(date)+"' WHERE ID=" + str(id)
            else:
                cmd = "INSERT INTO people(ID,Name,date) Values(" + str(id) + ",' " + str(name) + " ','"+str(date)+"' )"
            conn.execute(cmd)
            conn.commit()
            conn.close()
        id = mssv.get()
        name = username.get()
        now = datetime.datetime.now()
        date = now.strftime("%D,%H:%M:%S")
        print(date)
        print("Bắt đầu chụp ảnh sinh viên, nhấn q để thoát!")
        insertOrUpdate(id, name,date)
        sampleNum = 0
        while (True):
            ret,img = cam.read()
            # Chuyen he mau

            # Convert hanh image TK
            photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img))
            # Show
            canvas.create_image(0, 0, image=photo, anchor=tkinter.NW)
            img = cv2.resize(img, dsize=None, fx=1, fy=1)
            # Lật ảnh cho đỡ bị ngược
            img = cv2.flip(img,1)
            # Kẻ khung giữa màn hình để người dùng đưa mặt vào khu vực này
            centerH = img.shape[0] // 2;
            centerW = img.shape[1] // 2;
            sizeboxW = 300;
            sizeboxH = 400;
            cv2.rectangle(img, (centerW - sizeboxW // 2, centerH - sizeboxH // 2),
                          (centerW + sizeboxW // 2, centerH + sizeboxH // 2), (255, 255, 255), 5)
            # Đưa ảnh về ảnh xám
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Nhận diện khuôn mặt
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                # Vẽ hình chữ nhật quanh mặt nhận được
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                sampleNum = sampleNum + 1
                # Ghi dữ liệu khuôn mặt vào thư mục dataSet
                cv2.imwrite("C:/Users/TT/nhandienkhuonmat/User." + id + '.' + str(sampleNum) + ".jpg",
                            gray[y:y + h, x:x + w])
            cv2.imshow('frame', img)
            # Check xem có bấm q hoặc trên 100 ảnh sample thì thoát
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            elif sampleNum > 100:
                break
        cam.release()
        cv2.destroyAllWindows()
        messagebox.showinfo('result','successful detection')
b1= tk.Button(window,text="Dectection",font=("Arial",20),bg ='pink',fg='red',command= generate_dataset)
b1.grid(column=0,row=4)

def training_face():
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        path = "C:/Users/TT/nhandienkhuonmat"

        def getImagesAndLabels(path):
            # Lấy tất cả các file trong thư mục
            imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
            # create empth face list
            faceSamples = []
            # create empty ID list
            Ids = []
            for imagePath in imagePaths:
                if (imagePath[-3:] == "jpg"):
                    print(imagePath[-3:])
                    # loading the image and converting it to gray scale
                    pilImage = Image.open(imagePath).convert('L')
                    # Now we are converting the PIL image into numpy array
                    imageNp = np.array(pilImage, 'uint8')
                    print(imageNp)
                    # getting the Id from the image
                    Id = int(os.path.split(imagePath)[-1].split(".")[1])
                    # extract the face from the training image sample
                    faces = detector.detectMultiScale(imageNp)
                    # If a face is there then append that in the list as well as Id of it
                    for (x, y, w, h) in faces:
                        faceSamples.append(imageNp[y:y + h, x:x + w])
                        Ids.append(Id)
                        cv2.imshow("training", imageNp)
                        cv2.waitKey(10)
            return faceSamples, Ids
        # Lấy các khuôn mặt và ID từ thư mục dataSet
        faceSamples, Ids = getImagesAndLabels("C:/Users/TT/nhandienkhuonmat")

        # Train model để trích xuất đặc trưng các khuôn mặt và gán với từng nahan viên
        recognizer.train(faceSamples, np.array(Ids))

        # Lưu model
        recognizer.save("C:/Users/TT/nhandienkhuonmat/recognizer/recognizer.yml")
        print("Trained!")
        messagebox.showinfo('result', 'training models')
b2 = tk.Button(window,text="Training",font=("Arial",20),bg ='orange',fg='red',command=training_face)
b2.grid(column=1,row=4)

def recognition_face():

        SERVER_ADDRESS = "192.168.1.6"
        global PORT
        PORT = 8888
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        soc.connect((SERVER_ADDRESS, PORT))
        # Khởi tạo bộ phát hiện khuôn mặt
        faceDetect = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml");
        # Khởi tạo bộ nhận diện khuôn mặt
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("C:/Users/TT/nhandienkhuonmat/recognizer/recognizer.yml")
        id = 0
        # set text style
        fontface = cv2.FONT_HERSHEY_SIMPLEX
        fontscale = 1
        fontcolor = (0, 255, 0)
        fontcolor1 = (0, 0, 255)
        # Hàm lấy thông tin người dùng qua ID
        def getProfile(id):
            conn = sqlite3.connect("C:/Users/TT/nhandienkhuonmat/FaceBaseNew2.db")
            cursor = conn.execute("SELECT * FROM people WHERE ID=" + str(id))
            profile = None
            for row in cursor:
                profile = row
            conn.close()
            return profile
        # Khởi tạo camera
        #url = 'http://192.168.1.4:4747/video'
        cam = cv2.VideoCapture(0)
        # Hàm lấy tên:
        def attendance(name,id):
            with open('attendance.csv', 'r+') as f:
                mydatalist = f.readline()
                print(mydatalist)
                nameList = []
                for line in mydatalist:
                    entry = line.split(',')
                    nameList.append(entry[0])
                if name not in nameList:
                    now = datetime.datetime.now()
                    dtString = now.strftime('%D,%H:%M:%S')
                    f.writelines(f'\n{name},{id},{dtString}')
        while (True):
            # Đọc ảnh từ camera
            ret, img = cam.read();
            # Chuyển ảnh về xám
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Phát hiện các khuôn mặt trong ảnh camera
            faces = faceDetect.detectMultiScale(gray, 1.3, 5)
            # Lặp qua các khuôn mặt nhận được để hiện thông tin
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                id, dist = recognizer.predict(gray[y:y + h, x:x + w])
                profile = None
                # Nếu độ sai khác < 70% thì lấy profile
                if (dist <= 70):
                    profile = getProfile(id)
                    # Hiển thị thông tin tên người hoặc Unknown nếu không tìm thấy
                    if (profile != None):
                        cv2.putText(img, "" + str(profile[1]), (x, y + h + 30), fontface, fontscale, fontcolor, 2)
                        print(x, y)
                        if (x >0):
                          soc.send('1'.encode())
                else:
                    cv2.putText(img, "Uknow", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 5)
                    if (x > 0):
                        soc.send('0'.encode())

            cv2.imshow('Face', img)
            # Nếu nhấn q thì thoát
            if cv2.waitKey(1) == ord('q'):
                break;
        #lấy ra tên với id:
        attendance(profile[1],profile[0])
        cam.release()
        cv2.destroyAllWindows()
        messagebox.showinfo('result','successful identification')

b3 = tk.Button(window,text="Recognition",font=("Arial",20),bg ='blue',fg='red',command=recognition_face)
b3.grid(column=2,row=4)
def open_file():
    filepath = filedialog.askopenfilename(initialdir ="C:/Users/TT/PycharmProjects/pythonProject13/attendance.csv")
    file = open(filepath,'r')
    print(file.read())
    file.close()
b4 = tk.Button(window,text="Attendance",font=("Arial",20),bg ='pink',fg='red',command=open_file)
b4.grid(column=1,row=5)
window.geometry("800x400")
window.mainloop()