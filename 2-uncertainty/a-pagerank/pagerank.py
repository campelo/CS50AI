import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")

def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages

def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    result = {k: 0.0 for k in corpus}
    if page is None or len(corpus[page]) == 0:
        dist = 1 / len(corpus)
        for k in corpus:
            result[k] += dist
    else:
        dist = damping_factor / len(corpus[page])
        for p in corpus[page]:
            result[p] += dist
        remaining_dist = (1 - damping_factor) / len(corpus)
        for k in corpus:
            result[k] += remaining_dist
    return result

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    count = {k: 0 for k in corpus}
    page = random.choice(list(corpus.keys()))

    for _ in range(0, n):
        count[page] += 1
        t_model = transition_model(corpus, page, damping_factor)
        page = random.choices(list(t_model.keys()), list(t_model.values()))[0]

    result = {k: count[k]/n for k in count}
    # print(f"sum = {sum(result.values())}")
    return result

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    result = {p: 1/len(corpus) for p in corpus}
    can_stop = {p: False for p in corpus}
    
    while any(v is False for v in can_stop.values()):
        for p in result:
            second = 0
            for page, link in corpus.items():
                if page == p:
                    continue
                if not link:
                    second += result[page]/len(corpus)
                elif p in link:
                    second += result[page]/len(link)               
            new_pr = ((1-damping_factor)/len(corpus))+(damping_factor*second)
            if new_pr - result[p] < 0.001:
                can_stop[p] = True
            result[p] = new_pr
        
        temp_sum = sum(result.values())
        result = {p: (r / temp_sum) for p, r in result.items()}

    # print(f"sum = {round(sum(result.values()),4)}")
    return result

if __name__ == "__main__":
    main()
