import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
import shelve


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    url_list = []

    # Check and ensure the url response was valid (no errors nor non-OK status)
    if (resp.error is None) and (resp.status == 200):
        # BeautifulSoup setup adapted from their Quick Start https://www.crummy.com/software/BeautifulSoup/bs4/doc/

        # Initiate the HTML parser for the downloaded webpage
        soup = BeautifulSoup(resp.raw_response.content, "lxml") # Requires lxml parser library

        # Scrape all human-readable text from the webpage
        webpage_text = soup.get_text()

        # If the webpage contains a significant amount of content (at least 200 words),
        # store the text in the text storage shelve, and associate it with the current URL
        if has_substantial_information(webpage_text, 200):
            with shelve.open("Webpage_Text.shelve") as text_storage:
                text_storage[url] = webpage_text
                text_storage.sync()

        # Loop through <a> tags in the HTML
        for next_attribute in soup.find_all('a'):
            # Get the link from the <a> tag
            next_link = next_attribute.get('href')

            # If the link is valid, add it to the list
            if next_link is not None:
                url_list.append(urldefrag(next_link)[0]) # Defrag the link before adding to the list

    # Return the filtered list of links
    return url_list


def is_valid(url):
    try:
        parsed = urlparse(url)

        if parsed.scheme not in ["http", "https"]:
            return False

        # Ensure the url is within one of the valid domains and paths
        elif not ((re.match(r"^(.+\.)(ics\.uci\.edu)$", parsed.netloc)) or
                  (re.match(r"^(.+\.)(cs\.uci\.edu)$", parsed.netloc)) or
                  (re.match(r"^(.+\.)(informatics\.uci\.edu)$", parsed.netloc)) or
                  (re.match(r"^(.+\.)(stat\.uci\.edu)$", parsed.netloc)) or
                  ((parsed.netloc == "today.uci.edu") and
                   (re.match(r"^(/department/information_computer_sciences/)(.+)$", parsed.path)))):
            return False

        # Ensure potential traps are not included in the url
        potential_traps = ["/event/", "/events/", "calendar", "date", "gallery", "image",
                           "wp-content", "index.php", "upload", "/pdf", "attachment/",
                           "?replytocom=", "?version=", "?share=", "?redirect=", "?redirect_to=", "?action="]
        for trap in potential_traps:
            if trap in url:
                return False

        return not re.match(
            r".*\.(css|js|java|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|odc|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|ppsx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|z|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise


def has_substantial_information(text_to_tokenize: str, word_minimum: int) -> bool:
    # Keep a count of the number of alphanumeric words found
    word_count = 0

    # Separate the text by all non-alphanumeric characters, and loop through it
    for next_word in re.split(r"[^a-zA-Z0-9]", text_to_tokenize):

        # If the next word is alphanumeric, increase the count of alphanumeric words
        if re.match(r"^[a-zA-Z0-9]+$", next_word) is not None:
            word_count += 1

        # If the amount of alphanumeric words has surpassed the minimum, return that the text is substantial
        if word_count >= word_minimum:
            return True

    # Otherwise, the text did not have enough alphanumeric words to be considered substantial
    return False
