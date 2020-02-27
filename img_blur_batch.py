import cv2 as cv
import os
import tkinter.filedialog
import tkinter.messagebox
import subprocess
import glob
import numpy as np
import threading
import time

global img

def nothing(x):
    pass

def eachProcess(img):
    '''
    img = cv.imread('E:\Personal\AntiAliasing\data\Chinese_HarmonyCapture.bmp', 0)

    cv.namedWindow('res', cv.WINDOW_AUTOSIZE)
    cv.namedWindow('edge', cv.WINDOW_AUTOSIZE)
    cv.namedWindow('blur', cv.WINDOW_AUTOSIZE)
    cv.namedWindow('rst', cv.WINDOW_AUTOSIZE)
    cv.createTrackbar('min', 'edge', 0, 25, nothing)
    cv.createTrackbar('max', 'edge', 0, 25, nothing)
    maxVal = cv.getTrackbarPos('max', 'edge')
    minVal = cv.getTrackbarPos('min', 'edge')
    while (1):
        if cv.waitKey(1) == 27:
            break

        maxValTemp = cv.getTrackbarPos('max', 'edge')
        minValTemp = cv.getTrackbarPos('min', 'edge')

        if maxVal == maxValTemp and minVal == minValTemp:
            continue
        maxVal = maxValTemp
        minVal = minValTemp

        edge = cv.Canny(img, 10 * minVal, 10 * maxVal)
        blur = cv.blur(img, (2, 2))
        rst = blur_f(img, blur, edge)
        #hmerge = np.hstack((img,edge, blur,rst))
        cv.imshow('res', img)
        cv.imshow('edge', edge)
        cv.imshow('blur', blur)
        cv.imshow('rst', rst)
    cv.destroyAllWindows()
    '''
    file_name = file_survey()
    img = cv.imread(img)
    edge = cv.Canny(img, 100, 600)
    cv.imwrite("./data/{}.bmp".format('edge'), edge)
    blur = cv.blur(img, (2, 2))
    cv.imwrite("./data/{}.bmp".format('blur'), blur)
    img = blur_f(img, blur, edge)
    cv.imwrite("./data/{}.bmp".format(file_name), img)
    dir_name = os.path.dirname(os.path.abspath(__file__)).replace("/", "\\")
    subprocess.run("explorer {}\\data".format(dir_name))


def blur_f(img, blur, edge):
    w, h = img.shape[:2]
    mask = make_mask(edge.copy(), w, h)
    for i in range(w):
        for j in range(h):
            if mask[i][j] == 255:
                img[i][j] = blur[i][j]
    return img


def make_mask(edge, w, h):
    blank_img = edge.copy()
    for i in range(w):
        for j in range(h):
            blank_img[i][j] = 0
    for i in range(w):
        for j in range(h):
            try:
                if edge[i][j] == 255:
                    for k in range(-1, 2):
                        for l in range(-1, 2):
                            blank_img[i + k][j + l] = 255
            except IndexError:
                pass
    return blank_img


def file_survey():
    flag = 0
    while True:
        print("保存ファイル名を指定してください : ", end="")
        file_name = input()
        dir_files = glob.glob("./data/*")
        for name in dir_files:
            name = os.path.basename(name)
            name = name.strip(".jpg")
            if name == file_name:
                flag += 1
        if flag == 1:
            print("指定したファイル名は既に存在します。上書きしますか?(y/other) : ", end="")
            yn = input()
            if yn == "y":
                return file_name
            else:
                flag -= 1
        else:
            return file_name

def selectPathSrc():
    pathSrc.set(tkinter.filedialog.askdirectory())


def selectPathBaseFile():
    file_type = [("image", "*.bmp")]
    initial_dir = os.path.abspath(os.path.dirname(__file__))
    pathBaseFile.set(tkinter.filedialog.askopenfilename(filetypes=file_type, initialdir=initial_dir))


def selectPathDst():
    pathDst.set(tkinter.filedialog.askdirectory())

def on_mouseSrc(event, x, y, flags, param):
    global pixelBase, img, point1, point2

    if event == cv.EVENT_LBUTTONDOWN:         #左键点击
        point1 = (x,y)

    elif event == cv.EVENT_MOUSEMOVE and (flags & cv.EVENT_FLAG_LBUTTON):               #按住左键拖曳
        pass

    elif event == cv.EVENT_LBUTTONUP:         #左键释放
        point2 = (x, y)
        pixelFore=img[x,y].copy()

        fillbgr = (int(pixelBase[0]), int(pixelBase[1]), int(pixelBase[2]))

        min_x = min(point1[0],point2[0])
        min_y = min(point1[1],point2[1])
        rectWidth = abs(point1[0] - point2[0])
        rectHeight = abs(point1[1] -point2[1])
        imgWidth = img.shape[1]
        imgHeight = img.shape[0]

        cv.rectangle(img, (0,0), (imgWidth-1,min_y), fillbgr, thickness=-1)
        cv.rectangle(img, (0,min_y+rectHeight), (imgWidth, imgHeight), fillbgr, thickness=-1)
        cv.rectangle(img, (0, min_y), (min_x, min_y+rectHeight), fillbgr, thickness=-1)
        cv.rectangle(img, (min_x+rectWidth, min_y), (imgWidth, min_y+rectHeight), fillbgr, thickness=-1)

        for px in range(min_x,min_x+rectWidth):
            for py in range(min_y,min_y+rectHeight):
                if (img[py,px] == pixelFore).all():
                    img[py,px] = pixelBase.copy()

        blur = cv.blur(img, (2, 2))

        global src
        dst = src.copy()
        for px in range(min_x,min_x+rectWidth):
            for py in range(min_y,min_y+rectHeight):
                if (blur[py,px] != pixelBase).all():
                    dst[py,px] = blur[py,px].copy()

        cv.imwrite("{}/{}".format(pathDst.get(),name), dst)

        cv.imshow('SRC IMAGE', dst)
        tkinter.messagebox.showinfo('提示', 'Done!')
        cv.destroyAllWindows()


        #
        #
        # global src
        # dst = mergeBlur2Src(blur,src)
        #
        # time.sleep(2)
        #
        # cv.imwrite("{}/{}".format(pathSrc.get(),i), dst)


def mergeSrc2Base(src,base):
    global pixelBase, pixelFore, img, point1, point2
    pixelBase = base[0, 0].copy()

    # cv.namedWindow('选取Base颜色')
    # cv.imshow('选取Base颜色', base)
    # cv.setMouseCallback('选取Base颜色', on_mouseBase)
    #

    img = src.copy()
    cv.namedWindow('SRC IMAGE')
    cv.imshow('SRC IMAGE', img)

    cv.setMouseCallback('SRC IMAGE', on_mouseSrc)


def mergeBlur2Src(src, dst):
    pass


def runProcess():

    if pathSrc.get()=='':
        tkinter.messagebox.showwarning('提示','【源图片路径】 未选择')
        return
    if pathBaseFile.get()=='':
        tkinter.messagebox.showwarning('提示','【Base图片】 未选择')
        return
    if pathDst.get() == '':
        tkinter.messagebox.showwarning('提示','【目标图片路径】 未选择')
        return

    for i in os.listdir(pathSrc.get()):
        if i.endswith('.bmp'):
            global src, name
            name = i
            src=cv.imread(pathSrc.get()+'\\'+i)
            base=cv.imread(pathBaseFile.get())
            mergeSrc2Base(src, base)

            # 等待Callback函数结束
            # global flgImgDone
            # flgImgDone = False
            # while not flgImgDone:
            #     continue
            #
            # blur = cv.blur(img, (2, 2))
            #
            # dst = mergeBlur2Src(blur,src)

            # cv.imwrite("{}/{}".format(pathSrc.get(),i), dst)


if __name__ == "__main__":
    root = tkinter.Tk()

    pathSrc = tkinter.StringVar()
    pathBaseFile = tkinter.StringVar()
    pathDst = tkinter.StringVar()

    '''
    Debug
    '''
    pathSrc.set(r'E:\Personal\AntiAliasing\data\src')
    pathBaseFile.set(r'E:\Personal\AntiAliasing\data\base\BTN_Master_1_OFF.bmp')
    pathDst.set(r'E:\Personal\AntiAliasing\data\dst')


    tkinter.Label(root, text='源图片路径').grid(row=0,column=0)
    tkinter.Entry(root, textvariable=pathSrc,width=80).grid(row=0,column=1)
    tkinter.Button(root,text='选择',command=selectPathSrc).grid(row=0,column=2)

    tkinter.Label(root, text='Base图片').grid(row=1,column=0)
    tkinter.Entry(root, textvariable=pathBaseFile,width=80).grid(row=1,column=1)
    tkinter.Button(root,text='选择',command=selectPathBaseFile).grid(row=1,column=2)

    tkinter.Label(root, text='目标图片路径').grid(row=2,column=0)
    tkinter.Entry(root, textvariable=pathDst,width=80).grid(row=2,column=1)
    tkinter.Button(root,text='选择',command=selectPathDst).grid(row=2,column=2)

    tkinter.Button(root,text='执行',command=runProcess).grid(row=3,column=1)

    root.mainloop()

'''
    root.withdraw()
    file_type = [("image", "*.bmp")]
    initial_dir = os.path.abspath(os.path.dirname(__file__))
    main(img=tkinter.filedialog.askopenfilename(filetypes=file_type, initialdir=initial_dir))
'''