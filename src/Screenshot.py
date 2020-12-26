# -*- coding: utf-8 -*-

import cv2
import Coords
import Sanitize

from os import system as os_system
from pytesseract import image_to_string

# OCR on Answer config
OCR_CONFIG_ANSWER = "--oem 0 --psm 7 -l ita+eng"
# OCR on Question config
OCR_CONFIG_QUESTION = "--oem 0 -l ita+eng"

def load_image(path):
    # Load the screenshot file from disk
    screenshot = cv2.imread(path)
    
    # Debug, uncomment to:
    # show a window with the loaded screenshot, until a key is pressed
    #cv2.imshow(f"{path}",screenshot)
    #cv2.waitKey(0)
    
    # Commute image from colored to black and white
    grey_screenshot = cv2.cvtColor(screenshot,cv2.COLOR_BGR2GRAY)
    return grey_screenshot

def take_screenshot(filename):
    # A few words about the fastest way to take a screenshot with Python.
    
    # Initially the Pillow library was used, in particular PIL.ImageGrab(), 
    # which is compatible only with Windows and macOS (press f for Linux). 
    # However, after some tests (on my machine specifically), it takes on average
    # a second to capture and save a screenshot to disk, which is too much 
    # considering the ten seconds available to answer the question.
    #from PIL import ImageGrab
    #ImageGrab.grab().save("screen.png")
    #real    0m1.077s

    # So I tried the MSS library, which can halve the time required 
    # to take and save a screenshot to disk. Plus, it's cross-platform.
    #from mss import mss
    #with mss() as sct:
    #    sct.shot() # saved as "monitor-1.png" by default
    #real    0m0.465s

    # But the choice fell on the macOS system utility, screencapture (rip cross-platform),
    # which manages to do the same operation in less than a quarter of a second.
    #from os import system
    #system("screencapture screen.png") # use -R to specify a region
    #real    0m0.206s
    
    # Take a screenshot of the emulator window
    os_system(f"screencapture -R {Coords.emulator.to_string()} {filename}")
    # Returns the screenshot already converted to grayscale
    return load_image(filename)

    
def extract_question(screen):
    # Crop original screenshot to only question's box using coordinates
    question_image = screen[
        Coords.question.y1:Coords.question.y2,
        Coords.question.x1:Coords.question.x2
    ]
    
    # Debug, uncomment to:
    # show a window with the question image, cropped from the screenshot until a key is pressed
    #cv2.imshow("Question",question_image)
    #cv2.waitKey(0)

    # Extract question's text from cropped screenshot as string
    question_text = image_to_string(question_image, config=OCR_CONFIG_QUESTION)
    return question_text if question_text != "" else "OCR Failed"

def extract_answer(screen, question, position):
    # Crop original screenshot to only answer's box using coordinates
    answer_image = screen[
        Coords.answers[position].y1 + question.get_shift():Coords.answers[position].y2 + question.get_shift(),
        Coords.answers[position].x1:Coords.answers[position].x2
    ]

    # Debug, uncomment to:
    # show a window with the answer image, cropped from the screenshot until a key is pressed
    #cv2.imshow(f"Answer {position}",answer_image)
    #cv2.waitKey(0)

    # Extract answer's text from cropped screenshot as string
    answer_text = image_to_string(answer_image,config=OCR_CONFIG_ANSWER).lower().strip()
    # Sanitize the answer and add it to the current question into quiz object
    question.add_answer(answer_text,Sanitize.clean_answer(answer_text),position)
    