import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    url_list = []

    # Check and ensure the url response was valid (no errors nor non-OK status)
    if (resp.error is not None) and (resp.status == 200):
        # BeautifulSoup setup adapted from their Quick Start https://www.crummy.com/software/BeautifulSoup/bs4/doc/

        # Initiate the HTML parser for the downloaded webpage
        html_parser = BeautifulSoup(resp.raw_response.content, "lxml") # Requires lxml parser library

        # TODO scrape text later

        # Loop through <a> tags in the HTML
        for next_attribute in html_parser.find_all('a'):
            # Get the link from the <a> tag
            next_link = next_attribute.get('href')

            # If the link is valid, add it to the list
            if (next_link is not None) and is_valid(next_link):
                url_list.append(urldefrag(next_link)) # Defrag the link before adding to the list

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
                           "wp-content", "index.php", "upload"]
        for trap in potential_traps:
            if trap in url:
                return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise