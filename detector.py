import urllib.request
import socket # for urllib timeout
import os
import yaml
import time
from time import sleep
import requests
import json
import json.decoder
import math
import timestamp
from PIL import Image, ImageDraw, ImageFont
import sqlite3
import create_db
import logging
con = sqlite3.connect('data.db', isolation_level=None)
cur = con.cursor()
#socket.setdefaulttimeout(15)

class Photo:
  def __init__(self, api_key, directory, user_id, group_key, camera_id, camera_friendly, shinobi_ip, thing, filename, now, actual_detection):
    self.api_key = api_key
    self.directory = directory
    self.user_id = user_id
    self.group_key = group_key
    self.camera_id =  camera_id
    self.camera_friendly = camera_friendly
    self.shinobi_ip = shinobi_ip
    self.thing = thing
    self.actual_detection = actual_detection
    now = timestamp.now()
    self.now = now
    filename = (directory + camera_friendly + now + '.jpeg')
    self.filename = filename
    imgURL = ('http://' + shinobi_ip + '/' + api_key + '/jpeg/' + group_key + '/' + camera_id + '/s.jpg')
    logging.info(imgURL)
    try:
      urllib.request.urlretrieve(imgURL, filename)
    except:
        logging.info("no response from shinobi, waiting 10 seconds. If the app is just starting up, this is fine to ignore")
        sleep(10)
        self.now = timestamp.now()
        filename = (directory + camera_friendly + now + '.jpeg')
        urllib.request.urlretrieve(imgURL, filename)
class Detection(Photo):
  def __init__(self, api_key, directory, user_id, group_key, camera_id, camera_friendly, shinobi_ip, thing, filename, now, actual_detection):
    super().__init__(api_key, directory, user_id, group_key, camera_id, camera_friendly, shinobi_ip, thing, filename, now, actual_detection)
    filename = self.filename

    now = self.now
    image_data = open(filename,"rb").read()
    response = requests.post("http://deepstack:5000/v1/vision/detection",files={"image":image_data}).json() 
    label_index = -1
    try: 
      pred = iter(response['predictions'])
    except KeyError:
      print("deepstack error, waiting 10 seconds and trying again")
      sleep(10)
      response = requests.post("http://deepstack:5000/v1/vision/detection",files={"image":image_data}).json()
      pred = iter(response['predictions'])
    while True:
      try:
          element = next(pred)
          if thing not in element['label']:
            label_index += 1
          elif thing  in element['label']:
            label_index += 1
            confidence = element['confidence']
            # create variables for square boundaries
            xmin = response['predictions'][label_index]['x_min']
            xmax = response['predictions'][label_index]['x_max']
            ymin = response['predictions'][label_index]['y_min']
            ymax = response['predictions'][label_index]['y_max']
            # define shape of square with values from deepstack
            top = [(xmin, ymin), (xmax, ymin)]
            left = [(xmin, ymin), (xmin, ymax)]
            right = [(xmax, ymin), (xmax, ymax)]
            bottom = [(xmin, ymax), (xmax, ymax)]
            # open image for processing
            img = Image.open(filename)
            # draw square shape on image
            img1 = ImageDraw.Draw(img)
            img1.line(top, fill ="yellow", width = 5)
            img1.line(left, fill ="yellow", width = 5)
            img1.line(right, fill ="yellow", width = 5)
            img1.line(bottom, fill ="yellow", width = 5)
            font = ImageFont.truetype("qaz.ttf", 35)
            img1.text((xmax - 100, ymax - 200), response['predictions'][label_index]['label'], (155, 250, 0), font)
            img.save(filename)
            cur.execute("INSERT INTO DETECTIONS(LABEL, CONFIDENCE, Y_MIN, Y_MAX, X_MIN, X_MAX, CAMERA_ID, TIMESTAMP, FILENAME) VALUES (?,?,?,?,?,?,?,?,?)", (thing, confidence, ymin, ymax, xmin, xmax, camera_friendly, now, filename))
            con.commit()
            self.actual_detection = response['predictions'][label_index]['label']
            print("hello from line 87, the value of actual_detection is : " + self.actual_detection)
            break
      except StopIteration:
          break
       

with open('vars.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
    api_key = data["api_key"]
    directory = data["directory"]
    user_id = data["user_id"]
    group_key = data["group_key"]
    camera_id = data["camera_id"]
    camera_friendly = data["camera_friendly"]
    shinobi_ip = data["shinobi_ip"]
    thing = data["object"]
    log_level = data["log"]
    interval = data["interval"]

if log_level == "info":
  logging.basicConfig()
  logging.getLogger().setLevel(logging.INFO)


x = []
while True:
  x.append(Detection( api_key, directory, user_id, group_key, camera_id, camera_friendly, shinobi_ip, thing, "", "", ""))
  #print(x[0])

  print(x)
  if len(x[0].actual_detection) == 0:
      print("nothing detected, deleting file")
      logging.info("nothing detected")
      os.remove(x[0].filename)
      x.pop()
      sleep(interval)
  else:
    logging.info(x[0].actual_detection + " detected, file saved as "  + x[0].filename)
    x.pop()
    sleep(interval)


