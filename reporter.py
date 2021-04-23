import shelve
import re
from collections import defaultdict
import enchant
from urllib.parse import urlparse
import os


def get_number_of_downloaded_urls(worker_log: os.path) -> int:
    # To hold the amount of unique URLs downloaded
    url_count = 0

    # Open the Worker log to get the downloaded URLs
    with open(worker_log, "r") as log_text:

        # Loop through the lines in the Worker log
        for next_line in log_text:
            # Split the line accord to its whitespace
            line_parts = next_line.split()

            # If the 7th part of the line is "Downloaded", that marks a unique URL as being downloaded,
            # so increment the amount by 1
            if line_parts[7] == "Downloaded":
                url_count += 1

    # Return the number of unique URLs crawled
    return url_count


def get_common_words(text_storage: shelve.DbfilenameShelf, amount_of_common_words: int) -> [(str, int)]:
    stop_words = set() # To hold the set of stop words
    word_frequencies = defaultdict(int) # To hold the amount of occurrences for non-stop words

    # Enchant setup adapted from their tutorial: https://pyenchant.github.io/pyenchant/tutorial.html
    dictionary = enchant.Dict("en_US") # To validate words

    # Open up the stop_words file and read in the set of stop words
    with open("stop_words.txt", "r") as file_input_stream:
        for next_word in file_input_stream:
            stop_words.add(next_word.rstrip())

    # Loop through the text for each webpage
    for next_webpage_text in text_storage.values():

        # Split the webpage according to all whitespace, dashes, and hyphens
        for next_word in re.split(r"[\s\-–]", next_webpage_text):

            # Remove special characters from the words (if any)
            next_word = re.sub(r"[.,?:!;()\[\]{}\"]", "", next_word)

            # If the next word contains only alphabetical characters (and some special characters),
            # is a recognizable English word, and is not a stop word, increment its frequency
            if (re.match(r"^[a-zA-Z']+$", next_word) is not None) and \
               dictionary.check(next_word) and \
               (next_word.lower() not in stop_words):
                word_frequencies[next_word.lower()] += 1

    # Sort the words according to their frequency in descending order and return them
    words_in_descending_frequency = \
        [(next_word, frequency) for next_word, frequency in sorted(word_frequencies.items(), key=lambda x: (-x[1]))]

    return words_in_descending_frequency[:amount_of_common_words]


def get_longest_page(shelf: shelve.DbfilenameShelf) -> (str, int):
    # To hold the longest page and its number of words
    longest_page = ""
    longest_page_count = 0

    # Get all urls from the shelve and loop through them
    keys = shelf.keys()
    for key in keys:

        # Get the words for the current url and count its words
        words = shelf[key]
        word_count = len(words)

        # If the amount of words for this url is more than the previous longest page, update the longest page and
        # word amount
        if word_count > longest_page_count:
            longest_page_count = word_count
            longest_page = key

    # Return the longest page and its word amount as a 2-tuple
    return longest_page, longest_page_count


def get_ics_subdomains(worker_log: os.path) -> [(str, int)]:
    # To hold the subdomains of ics and how many pages for each were found
    subdomain_dict = defaultdict(int)

    # For determining the subdomain of a url and increasing its frequency by 1
    def ics_subdomain(url):
        nonlocal subdomain_dict # So that the outside declaration of subdomain_dict can be accessed in this function

        # Parse the subdomain from the url
        parse = urlparse(url)
        subdomain = parse.hostname.split(".ics.uci.edu")[0]

        # If the subdomain has an additional www. attached to it, remove it
        if "www." in subdomain:
            subdomain = subdomain[4:]

        # If the subdomain is not empty, and isn' exactly www, increment its frequency in the dictionary
        if subdomain and (subdomain != "www"):
            subdomain_dict[subdomain] += 1

    # Open the Worker log file
    with open(worker_log, "r") as log_text:

        # Loop through each line of the Worker log
        for next_line in log_text:

            # Split the line according to its whitespace
            line_parts = next_line.split()

            # If the part at index 7 is Downloaded, then the part at index 8 is the URL
            # If the URL is a subdomain of ics.uci.edu, increment that subdomain's frequency
            if (line_parts[7] == "Downloaded") and ("ics.uci.edu" in line_parts[8]):
                ics_subdomain(line_parts[8])

    # Sort the list of subdomains and their frequencies into alphabetical order
    return sorted(subdomain_dict.items())


if __name__ == "__main__":
    # Construct the local path for the Worker log file
    worker_log = os.path.join("Logs", "Worker.log")

    # Open the shelve that houses the URLs and their human-readable text
    with shelve.open("Webpage_Text.shelve") as text_storage:
        # Calculate the number of unique urls found by the crawler (the number of urls downloaded by the Worker)
        unique_urls_found = get_number_of_downloaded_urls(worker_log)

        # Calculate the 50 most common words among all downloaded webpages
        most_common_words = get_common_words(text_storage, 50)

        # Calculate the longest downloaded webpages (by word amount)
        longest_page, longest_page_count = get_longest_page(text_storage)

        # Calculate all subdomains found under ics.uci.edu
        ics_subdomains = get_ics_subdomains(worker_log)

        # Print the results
        print(f"The number of unique pages found was: {unique_urls_found}")
        print(f'\nThe longest page was "{longest_page}" with a length of {longest_page_count}')

        print("\nThe 50 most common words (and their frequencies) are:")
        for next_common_word, next_frequency in most_common_words:
            print(f"{next_common_word}, {next_frequency:}")

        print("\nThe subdomains found under ics.uci.edu and the number of unique pages detected for each is:")
        for next_subdomain, next_page_amount in ics_subdomains:
            print(f"http://{next_subdomain}.ics.uci.edu, {next_page_amount}")
