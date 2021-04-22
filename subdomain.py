subdomain_dict = {} 


def ics_subdomain(self, url):
    try:
        parse = urlparse(url)
        subdomain = parse.hostname.split(".ics.uci.edu")[0]
        
        if "www." in subdomain:
            subdomain = subdomain[4:]
        
        if subdomain:
            try:
                self.subdomain_dict[subdomain] += 1
            except KeyError:
                self.subdomain_dict[subdomain] = 1

    except Exception as e:
        pass
    
## sort dictionary
## Keep track of the subdomains that it visited, 
## and count how many different URLs it has processed 
## from each of those subdomains.\n")
for key, value in sorted(self.subdomain_dict.items(), key=lambda _: _[1], reverse=True):
    #write..
