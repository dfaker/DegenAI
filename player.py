
import requests
import os
import threading
import time
import os 

import json

import subprocess as sp
import random
import itertools
import numpy as np
from math import ceil
from pathlib import Path
import torch
import torch.nn as nn
import torch.nn.functional as F
import clip
from PIL import Image, ImageFont, ImageDraw
from collections import deque
from queue import PriorityQueue, Empty
import traceback

scriptPath = os.path.dirname(os.path.abspath(__file__))
basescriptPath = os.path.split(scriptPath)[0]
os.environ["PATH"] = scriptPath + os.pathsep + os.environ["PATH"]

basePath = 'Y:\\'

if not os.path.exists(basePath):
    print(basePath, 'path for video file search does not exist')
    exit()

import mpv

player = mpv.MPV()
player.loop_playlist ='inf'
player.vo = 'gpu-next'
player.geometry = '70%x70%'
player.autofit_larger = '100%x100%'



state_name = "linear_predictor_L14_MSE.pth"

class AestheticPredictor(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.input_size = input_size
        self.layers = nn.Sequential(
            nn.Linear(self.input_size, 1024),
            nn.Dropout(0.2),
            nn.Linear(1024, 128),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.Dropout(0.1),
            nn.Linear(64, 16),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.layers(x)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)
if device == 'cpu':
    exit()

pt_state = torch.load(state_name, map_location=torch.device('cpu')) 

predictor = AestheticPredictor(768)
predictor.load_state_dict(pt_state)
predictor.to(device)
predictor.eval()

clip_model, clip_preprocess = clip.load("ViT-L/14", device=device)


def get_image_features(image, device=device, model=clip_model, preprocess=clip_preprocess):
    image = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        image_features = model.encode_image(image)
        # l2 normalize
        image_features /= image_features.norm(dim=-1, keepdim=True)
    return [], [], image_features

def get_score(image):
    values, indices, image_features = get_image_features(image)
    with torch.no_grad():
        score = predictor(image_features.float())
    return values, indices, score.item()


cnt=0
videoList = []
i=0
for r,_,fl in os.walk(basePath):
    for f in fl:
        p = os.path.join(r,f)
        if os.path.isfile(p) and f.endswith('.mp4'):
            i+=1
            videoList.append((i,p))
            print(p)

random.shuffle(videoList)

queueLimit = 9000
videoHotQueue = PriorityQueue(queueLimit)

thresh=0.7
fps = 1

totalSecondsFound = 0.01
currentScanFile = 'None'

def scanThread():
    global totalSecondsFound, currentScanFile

    order = 0
    while len(videoList) > 0:
        try:
            _,videoFile = videoList.pop()
            order += 1

            currentScanFile = videoFile

            dim = sp.Popen(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=s=x:p=0',  videoFile], stdout=sp.PIPE).communicate()[0]
            w,h = dim.split(b'x')
            w,h = float(w),float(h)

            if w < 720 or h < 720 or w < h:
                continue
            
            w,h = int(w),int(h)

            length = sp.Popen(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', videoFile], stdout=sp.PIPE).communicate()[0]
            length = float(length)

            """
            wr = 512/w
            w  = 512
            h  = int(h*wr)
            """

            popen_params = {
              "bufsize": 10 ** 5,
              "stdout": sp.PIPE,
              "stderr": sp.DEVNULL,
            }

            cmd = ["ffmpeg", "-i", videoFile 
                  ,"-sws_flags", "area"
                  ,"-vf", "fps={},scale={}:{}".format(fps,w,h)
                  ,"-f","image2pipe"
                  ,"-an"
                  ,"-copyts"
                  ,"-pix_fmt","rgb24"
                  ,"-vcodec","rawvideo"
                  ,"-vsync", "vfr" 
                  ,"-"]

            nbytes = 3 * w * h
            proc = sp.Popen(cmd,**popen_params)

            fnum = -1

            lastStart = None
            scores = []
            print(videoFile)
            while 1:
                fnum+=1
                s = proc.stdout.read(nbytes)

                if len(s) != nbytes:
                    print('Section stream end')
                    break

                frame = np.frombuffer(s, dtype="uint8")
                frame.shape = (h,w,3)
                _,_,score = get_score(Image.fromarray(frame))

                if score >= thresh and lastStart is None:
                    lastStart = fnum
                    scores.append(score)
                elif score < thresh and lastStart is not None:

                    meanscore = sum(scores)/len(scores)
                    hotVid = videoFile,meanscore,lastStart*fps,(fnum-1)*fps
                    if ((fnum-1) - lastStart) > 0.01:
                        totalSecondsFound += ((fnum-1) - lastStart)
                        print(hotVid)
                        videoHotQueue.put((order,lastStart,hotVid))
                    lastStart = None
                    scores = []
        except Exception as e:
            print(traceback.format_exc())
            print(e)

scanThreadWorkers = [threading.Thread(target=scanThread,daemon=True) for _ in range(1)]
for scanThreadWorker in scanThreadWorkers:
    scanThreadWorker.start()
scanstart = time.time()

active = True

@player.on_key_press('q')
def my_q_binding():
    global active
    active = False
    player.stop()


skip = False

@player.on_key_press('s')
def my_s_binding():
    global skip
    skip = True

overlayerr = mpv.ImageOverlay(player,0)

noiseImages = [ Image.open(os.path.join('noise',x)) for x in os.listdir('noise') ]
nonoise = Image.new('RGBA',(100,100),(255,255,255,0))

overlayMeter = mpv.ImageOverlay(player,2)

valqueue = deque([],200)

graph = Image.new('RGBA',(900,900),(0,0,0,0))
draw = ImageDraw.Draw(graph)

fnt = ImageFont.truetype("vcr.TTF", 20)
totalPlayed=0

lastFilename = None
from datetime import timedelta
totalSecondsPlayed=0.01

def updateStats():
    cacheFillSpeed = (totalSecondsFound/(time.time()-scanstart))
    cacheFillSpeedWarn = ''
    if cacheFillSpeed < 1.0:
        cacheFillSpeedWarn = '-*WARNING*'

    td = timedelta(seconds=time.time()-scanstart)

    pos = player.time_pos
    if pos is None:
        pos = end

    lines = [
        'Degen A.I. v1.4.0 - Artificial Video Cuts Editor',
        'Playing: {}'.format(os.path.splitext(os.path.basename(videoFile))[0]),
        'Scanning: {}'.format(os.path.splitext(os.path.basename(currentScanFile))[0]),
        'Seg: {:.2f}-{:.2f}s ({:.4f}s/{:.4f}s)'.format(start,end,end-pos,end-start),
        'Rating: {} (Min Threshold: {})'.format(('*'*int(10*meanscore)).ljust(10,'-'),thresh),
        'Uptime: {}'.format(str(td)),
        'Stream Cache: {:.1f}s [{:.4f}s/s{}]'.format( totalSecondsFound-(totalSecondsPlayed-(end-pos)) ,cacheFillSpeed,cacheFillSpeedWarn),
        'Queues: {} -> {} -> {}'.format(len(videoList),videoHotQueue.qsize(),totalPlayed),
    ]

    draw.rectangle([(0,0),(900,900)], fill=(0,0,0,0), outline=(0,0,0,0))

    borderSize=2
    for linei,line in enumerate(lines):
        draw.text((5-borderSize, 5+(linei*20)), line, font=fnt, fill=(0, 0, 0, 255))
        draw.text((5+borderSize, 5+(linei*20)), line, font=fnt, fill=(0, 0, 0, 255))
        draw.text((5, 5+(linei*20)-borderSize), line, font=fnt, fill=(0, 0, 0, 255))
        draw.text((5, 5+(linei*20)+borderSize), line, font=fnt, fill=(0, 0, 0, 255))

        if '*WARNING*' in line:
            draw.text((5, 5+(linei*20)), line, font=fnt, fill=(255, 0, 0, 255))
        elif 'Degen A.I.' in line:
            draw.text((5, 5+(linei*20)), line, font=fnt, fill=(255, 16, 240, 255))
        else:
            draw.text((5, 5+(linei*20)), line, font=fnt, fill=(255, 255, 255, 255))
    
    overlayMeter.update(graph,pos=(5,0))


while active:
    try:
        
        try:
            _,_,(videoFile,meanscore,start,end) = videoHotQueue.get(timeout=0.1)
            videoHotQueue.task_done()
            totalPlayed+=1

            totalSecondsPlayed += end-start
            player.pause = False
            try:
                overlayerr.update(nonoise.resize((player.osd_width,player.osd_height)))
            except Exception as e:
                pass
        except Empty as e:
            try:
                player.pause = True

                totalSecondsPlayed=0.01
                totalSecondsFound = 0.01

                updateStats()

                overlayerr.update(random.choice(noiseImages).resize((player.osd_width,player.osd_height)))
            except Exception as e:
                continue
            continue

        if lastFilename != videoFile:
            lastFilename = videoFile
            player.play(videoFile)
            player.wait_until_playing()

        if start > player.time_pos:
            player.command('seek',str(start),'absolute','exact')
        
        while player.time_pos < end:
            if skip:
                skip=False
                break
            updateStats()
            pass

    except Exception as e:
        print(e)
    

player.quit(0)
player.wait_for_shutdown()