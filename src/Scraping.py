# -*- coding: utf-8 -*-

from pyquery import PyQuery
from urllib.request import Request
from urllib.request import urlopen
from urllib.parse import quote_plus

# Reminder: quote_plus is used for properly quoting 
# when building up a query string that go into a URL
# https://docs.python.org/3/library/urllib.parse.html#urllib.parse.quote_plus

# Google URL
google_url = "https://www.google.it/search?q="
# User agent for http get
headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

def define_url(question_text, answer_text=None):
    if answer_text:
        return google_url + quote_plus(f"{question_text} {answer_text}")
    else:
        return google_url + quote_plus(question_text)

def search(url, full_page=False):
    # Create an HTTP Get request
    request = Request(url, headers=headers)
    # Make the HTTP Get request
    page = urlopen(request).read()
    # Load the HTML into a PyQuery instance
    pq = PyQuery(page)
    # Find and return all divs with 'rc' as class
    # <full_page> is required during "a more in depth analysis" fase,
    # where the algorithm need the number of total results
    return pq("div.rc") if not full_page else (pq("div.rc"), pq)

def guess_answer(results, answer):
    # Pattern matching: answer in google result body
    for result in results:
        # If the answer is in the body of the result
        if answer.get_text() in PyQuery(result).text().lower():
            answer.matches += 1
    # Return true if the answer got at least one match, false otherwise
    return answer.matches > 0

def calculate_concat(question_text, answer):
    query_url = define_url(question_text, answer.get_text())
    google_results, full_page = search(query_url, full_page=True)
    # Extract the number of total google results
    answer.total_results = get_google_total_results(full_page)

    for result in google_results:
        result_text = PyQuery(result).text()
        # If Google doesn't find enough results, it includes some that aren't really relevant,
        # adding "Missing words: <keywords>", where keywords are words 
        # included in the search query (answer, here).
        # In this context, the results described are not useful and are excluded

        # If the answer is in the result text
            # If "Mancanti:" is not in the result text (so, it's a relevant result)
                # If the answer is not in the "Must include" section
        if answer.get_text() in result_text.lower() and \
            not "Mancanti:" in result_text and \
                not answer.get_text() in result_text.split("\n")[-1].lower():
                    # Yay! This is a relevant result!
                    answer.results += 1

    # Calculate the score of the answer
    answer.score = answer.total_results * (answer.results if answer.results > 0 else 1)

    return f"{answer.get_text()[:40]:^40}{answer.score:<10}{answer.results:^10}{answer.total_results:<10}"

def get_google_total_results(google_results):
    # Extract div contain the number of total google results
    number_results = google_results("div#result-stats").text().split(' ')
    # If there is a result counter on the page
    if number_results:

        # Explanation: <number_results> is a list of strings containing the number
        # of results found, like: ['Circa', 'x', 'risultati ', '(x secondi)'].
        # Sometimes, if the query is too specific, Google return a different format 
        # and the same list becomes more like: ['x', 'risultati', '(x secondi)'].
        # In both scenarios, we need <x> which is located in position 0 in the first case,
        # and in position 1 in the second, respectively if the length of the list is 4 or 3.
        # Instead of checking the lenght of the list in two different if, we use modular algebra
        # to take the remainder of the division between the lenght and 3 (used as constant). So:
        #  1. if len(number_results) == 4 -> 4 % 3 = 1, and we get <x>
        #  2. if len(number_results) == 3 -> 3 % 3 = 0, and we also get <x>

        try:
            return int(number_results[len(number_results) % 3].replace('.',''))
        # Sometimes, due to network/google error, it fail! 
        except IndexError:
            return 1
    else:
        # If the query is too general, Google does not return the total number of results at all, 
        # so <1> is returned as the neutral element of the multiplication
        return 1
