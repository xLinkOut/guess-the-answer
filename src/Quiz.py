# -*- coding: utf-8 -*-

from os import makedirs
from os.path import isfile
from datetime import datetime
from operator import attrgetter
from Coords import answers_shift
from csv import writer as csv_writer

CSV_HEADERS = [
    "Question", "First answer", "Second answer", "Third answer",
    "Cleaned question", "Cleaned first answer", "Cleaned second answer", "Cleaned third answer",
    "Guessed answer", "Correct answer", "Usual question", "One match",
    "Score first answer", "Score second answer", "Score third answer",
    "Did I guess?"
]

class Quiz:
    
    def __init__(self,path=None):
        self.folder_name = self.create_folder() if not path else path
        self.report_path = f"{self.folder_name}/Report.csv"
        self.report_exists = isfile(self.report_path)
        self.questions = list()
        print("Created new quiz!")

    def set_folder_name(self):
        now = datetime.now()
        hour = now.hour
        if 13 <= hour <= 14:
            return "Quizzes/{0}".format(now.strftime("%Y-%m-%d-AM"))
        elif 20 <= hour <= 21:
            return "Quizzes/{0}".format(now.strftime("%Y-%m-%d-PM"))
        else:
            return "Quizzes/Debug"

    def create_folder(self):
        folder_name = self.set_folder_name()
        try:
            makedirs(folder_name)
            print(f"{folder_name} created")
        except FileExistsError:
            print(f"{folder_name} already exists")
        finally:
            return folder_name

    def new_question(self, text):
        question = Question(text)
        self.questions.append(question)
        return question
    
    def get_current_question(self):
        return self.questions[-1] if self.questions else None

    def save_report(self):
        """
        CSV Structure:
        
        Question: question text as read by the OCR,
        First answer: text of the first answer as read by the OCR,
        Second answer: text of the second answer as read by the OCR,
        Third answer: text of the third answer as read by the OCR,
        
        Cleaned question: question text after the 'cleaning' process,
        Cleaned first answer: text of the first answer after the 'cleaning' process,
        Cleaned second answer: text of the second answer after the 'cleaning' process,
        Cleaned third answer: text of the third answer after the 'cleaning' process,

        Guessed answer: the answer guessed by the algorithm (1,2,3)
        Correct answer: the real correct answer (1,2,3)
        
        Usual question: True if the question is an usual question, False if is a "negated" question
        One match: number of matches if the algorithm guessed the answer without concatenating, 0 otherwise
        Score first answer: a triple with <score, results, total_result> of the first answer
        Score second answer: a triple with <score, results, total_result> of the second answer
        Score third answer: a triple with <score, results, total_result> of the third answer

        Did I guess?: True if the algorithm has guessed the right answer, False otherwise
        """
        
        # Open a new report file
        with open(self.report_path,'w') as report_file:
            writer = csv_writer(report_file, delimiter=',', quotechar='"')
            # Write the headers
            writer.writerow(CSV_HEADERS)

            # For each question evaluated
            for question in self.questions:
                writer.writerow([
                    question.get_text(), # Question
                    question.get_answer(0).get_text(), # First answer
                    question.get_answer(1).get_text(), # Second answer
                    question.get_answer(2).get_text(), # Third answer
                    
                    question.get_cleaned_text(), # Cleaned question
                    question.get_answer(0).get_cleaned_text(), # Cleaned first answer
                    question.get_answer(1).get_cleaned_text(), # Cleaned second answer
                    question.get_answer(2).get_cleaned_text(), # Cleaned third answer

                    question.get_guessed_answer(), # Guessed answer
                    question.get_correct_answer(), # Correct answer
                    question.usual_question, # Usual question?
                    question.one_match, # One match
                    
                    question.get_answer(0).score, # Score first answer
                    question.get_answer(1).score, # Score second answer
                    question.get_answer(2).score, # Score third answer

                    question.guessed_answer == question.correct_answer # Did I guess?
                ])
            

class Question:

    def __init__(self, text):
        # Remove blank lines and new line
        self.text = text.strip().replace("\n",' ') 
        self.cleaned_text = str()
        self.answers = [None] * 3
        self.guessed_answer = int()
        self.correct_answer = int()
        self.usual_question = True
        self.one_match = False # Assume that no answer was found
        try:
            rows = len(text.strip().split("\n"))
            self.shift = answers_shift[rows-1]
        except IndexError:
            self.shift = 0
    
    def get_text(self):
        return self.text
    
    def get_shift(self):
        return self.shift

    def add_answer(self,text,cleaned_text,position):
        if 0 <= position <= 2:
            self.answers[position] = Answer(text,cleaned_text)

    def get_answer(self,position):
        try:
            return self.answers[position]
        except:
            return None

    def get_cleaned_text(self):
        return self.cleaned_text
    
    def set_cleaned_text(self, cleaned_text):
        self.cleaned_text = cleaned_text

    def get_answer_max_matches(self):
        return max(self.answers, key=attrgetter("matches"))
    
    def get_answer_max_score(self):
        return max(self.answers, key=attrgetter("score"))

    def get_answer_min_score(self):
        return min(self.answers, key=attrgetter("score"))

    def set_correct_answer(self, correct_answer):
        self.correct_answer = correct_answer

    def get_correct_answer(self):
        return self.correct_answer

    def set_guessed_answer(self,guessed_answer):
        self.guessed_answer = guessed_answer
    
    def get_guessed_answer(self):
        return self.guessed_answer

class Answer:

    def __init__(self, text, cleaned_text):
        self.text = text
        self.cleaned_text = cleaned_text
        self.score = 0
        self.matches = 0
        self.results = 0
        self.total_results = 0
        
    def get_text(self):
        return self.text
    
    def get_cleaned_text(self):
        return self.cleaned_text

    def get_matches(self):
        return self.matches