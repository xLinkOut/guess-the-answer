# -*- coding: utf-8 -*-

import Sanitize
import Scraping
import Screenshot

from Quiz import Quiz
from argparse import ArgumentParser
from colorama import Fore, Back, Style
from concurrent.futures import ThreadPoolExecutor, as_completed

def play(num_questions,path_directory,path_screenshot):
    # Create a new Quiz
    quiz = Quiz(path_directory)
    # Create a ThreadPool to parallelize the work from here on
    pool = ThreadPoolExecutor(max_workers=4)

    # For each question
    for i in range(1,num_questions+1):
        # Waiting for user input...
        try:
            c = input("Press enter to evaluate a new question, e to exit: ")
        except KeyboardInterrupt:
            # If CTRL+C, break
            print("") # Go to a new line  
            break
        # If the user decided to exit, break
        if c == 'e': break

        # If we are here to evaluate only one question
        if path_screenshot:
            # Load the screenshot from disk as cv2 grey object
            screenshot = Screenshot.load_image(path_screenshot)
        # Or we have to process an entire directory of questions
        elif path_directory:
            # Go through all screenshots in the specified directory 
            filename = f"{path_directory}/Question-{i}.png"
            screenshot = Screenshot.load_image(filename)
        # If there isn't neither a screenshots nor a directory
        else:
            # Define the path for a new screenshot file
            filename = f"{quiz.folder_name}/Question-{i}.png"
            # Take a black-n-white screenshot
            screenshot = Screenshot.take_screenshot(filename)

        # Create a new Question object and extract the question from the screenshot
        question = quiz.new_question(Screenshot.extract_question(screenshot))

        # Extract all three answers from the screenshot, in three different threads
        future_answers = {
            pool.submit(
                Screenshot.extract_answer,
                screenshot,
                question,
                position
            ): position for position in range(3)}
        future_question = pool.submit(Sanitize.clean_question(question))
        # Wait until all threads are done
        for future in as_completed(future_answers): pass

        print(f"\nQuestion n.{i}: {question.get_text()}")
        print(f"Answers: [{question.get_answer(0).get_text()}, {question.get_answer(1).get_text()}, {question.get_answer(2).get_text()}]")

        # Briefly ... later

        # Define the query URL
        query_url = Scraping.define_url(question.get_text())
        # Get search results from Google 
        google_results = Scraping.search(query_url)

        # Parallelize the pattern matching process with all the results
        future_guess = {
            pool.submit(
                Scraping.guess_answer,
                google_results,
                question.get_answer(position)
            ): position for position in range(3)
        }
        
        # If at least one result was found
        for future in as_completed(future_guess):
            if future.result():
                question.one_match = True

        # If at least one answer has a match
        if question.one_match:
            # Get and print the answer with the highest matches number
            guessed = question.get_answer_max_matches()
            print(f"\n{Style.BRIGHT}{Fore.GREEN}{guessed.get_text():>40} {Fore.CYAN}{guessed.get_matches():<40}{Fore.RESET}{Style.RESET_ALL}")
            # Save a reference to the guessed answer (non-zero indexed)
            question.set_guessed_answer(question.answers.index(guessed)+1)
        else:
            print(f"{Style.DIM}{Fore.YELLOW}No match found, trying a more in depth analysis...{Fore.RESET}{Style.RESET_ALL}\n")
            # Perform a query built concatenating the question and each answer
            
            # Print sort-of table header (17+Answer+17, Score+5, 1+Results+2, Total)
            # I know it's ugly, maybe I'll use Rich lib 
            print(f"{Style.BRIGHT}                 Answer                 Score      Results  Total{Style.RESET_ALL}")

            # Check if this is an usual question or a "negated" question (explaination below)
            question.usual_question = "NON" not in question.get_text()

            # Parallelize the pattern matching process with all the results
            future_calculation = {
                pool.submit(
                    Scraping.calculate_concat,
                    question.get_text() if question.usual_question else question.get_text().replace("NON",''),
                    question.get_answer(position)
                ): position for position in range(3)
            }
            
            for future in as_completed(future_calculation):
                print(future.result())

            # If the answers scored the same, then something went wrong
            if question.get_answer(0).score == question.get_answer(1).score == question.get_answer(2).score:
                print(f"\n{Style.BRIGHT}{Fore.RED}Choose a random answer, the search was not successful!{Fore.RESET}{Style.RESET_ALL}") # why not suggest a random answer?
            # Otherwise, let's assume the answer with the highest score is fair
            else:
                guessed = question.get_answer_max_score() if question.usual_question else question.get_answer_min_score()
                print(f"\n{Style.BRIGHT}{Fore.GREEN}{guessed.get_text():>40} {Fore.CYAN}{guessed.score:<40}{Fore.RESET}{Style.RESET_ALL}")
                # Save a reference to the guessed answer (non-zero indexed)
                question.set_guessed_answer(question.answers.index(guessed)+1)
            
            # About the algorithm for "negated" questions ("which of these... not..."):
            # if in the question is required to indicate the answer that does NOT belong
            # to a certain category, then a Google search concatenating the question without
            # the "not" ("NON", in italian) word and the answer is executed and then 
            # the answer that obtains the minimum score instead of the maximum, is taken.

        # Save the (real) correct answer for debug and analysis purpose,
        # but only if the report file doesn't already exist
        if not quiz.report_exists:
            question.set_correct_answer(int(input("\nWhat was the correct answer? (1,2,3): ")))
        
        # Print a bunch (80) of underscore to separate different question
        print("________________________________________________________________________________\n")
    
    # Shutdown the ThreadPool
    pool.shutdown()

    # Save the report if it doesn't already exist
    if not quiz.report_exists: 
        quiz.save_report()

if __name__ == "__main__":

    description = """
Guess the answer! is a general purporse Python algorithm that 
reads a series of questions and their answers, and tries to guess 
the correct answer based on the results of a Google search.
"""

    # Create a new ArgumentParser
    parser = ArgumentParser(prog="Guess the answer!", description=description)
    # Absolute path to a directory full of screenshots of quiz questions
    parser.add_argument("-d","--directory",default=None,type=str,help="path to a quiz folder")
    # Number of questions to evaluate, use in combo with --directory if there are fewer (or more) than the usual number of questions
    parser.add_argument("-n","--questions",default=12,type=int,help="number of questions to answer")
    # Absolute path to a single screenshot of a quiz question (if this is not None, --questions=1)
    parser.add_argument("-s","--screenshot",default=None,type=str,help="path to a single image of a quiz question")
    #parser.add_argument("-v","--verbose",default=1,type=int,help="set verbosity level")
    args = parser.parse_args()

    # Could not process a directory and single question at the same time
    if args.screenshot and args.directory:
        exit("Specify only one parameter between --directory and --screenshot!")
    #print(f"Using these parameters:\n\tQuestions:\t{args.questions}\n\tDirectory:\t{args.directory}\n\tScreenshot:\t{args.screenshot}")
    
    # Let's play!
    play(args.questions if not args.screenshot else 1,args.directory,args.screenshot)