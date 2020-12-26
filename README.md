# Guess the answer!
*Guess the answer!* is a general purporse Python algorithm that reads a series of questions and their answers, and tries to guess  the correct answer based on the results of a Google search. It's a porting, in fact it's not so "general purporse" but it's easily adaptable to any quiz.

## How to
The idea is: on the screen, there is a window with the quiz, always placed in the same position. The algorithm reads the questions and their answers by taking a screenshot and reading the text via OCR. It will try to find the correct answer thanks to (multiple) Google searches. In the best of cases, a match is found immediately, otherwise, each answer will be assigned a score indicating the "confidence" regarding its correctness. Ideally, the algorithm can be used even if the quiz is hosted on a web browser, a desktop application, or a mobile application (with the help of emulators such as BlueStack or by screen-mirroring with tools such as ScrCpy). Just set the coordinates correctly.

## Installation
### macOS
1. Install [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki): `brew install tesseract`;
2. Move Tesseract train's data from _tessdata_: `mv tessdata/* /usr/local/share/tessdata/`;
3. (Optional) use a virtual env: `python3 -m venv venv; source venv/bin/activate`;
3. Install dependencies: `pip install -r requirements.txt`;
4. Set coordinates in _src/Coords.py_ based on your screen (use `shift + cmd + 4`).

### Linux 
Same as macOS instructions but you know how to install Tesseract.

### Windows
Windows support requires some changes but installation follows the same steps. The software is easily portable and I gladly accept pull requests!

## Disclaimer
Developed only for educational purpose (and fun!).