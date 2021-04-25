import shelve
import re

def longestPage():
    shelf = shelve.open("Webpage_Text.shelve")
    longest_page = ""
    longest_page_count = 0
    keys = shelf.keys()
    for key in keys:
        words = re.split(r"[\s\-–]", shelf[key])
        word_count = len(words)
        if word_count > longest_page_count:
            longest_page_count = word_count
            longest_page = key
    shelf.close()
    return longest_page

if __name__ == '__main__':
    print(longestPage())