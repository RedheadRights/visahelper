from os import path as p, mkdir
from .scraper import Scraper
import csv
import json
from datetime import datetime
import threading

def main() -> None:
    dirpath = './logs'
    csvpath = './database.csv'
    changes = {}
    num_lines = 0

    # Get length of file to calculate progress
    with open(csvpath, "r+") as f:
        num_lines = sum(1 for _ in f) + 1

    # Open CSV database
    database = open(csvpath, 'r')
    reader = csv.reader(database)

    # Skip header
    next(reader)

    # make sure logs folder exists
    if not p.exists(dirpath):
        mkdir(dirpath)    
        
    def scrapingprocess(row):
        if len(row) == 0:
            return
        # Create file name in format: last_first.json
        try:
            last = row[0].split(',')[0].split()[0]
            first = row[0].split(',')[1].split()[0]
        except Exception as e:
           return    
        filename = last + '_' + first + '.json'

        # Create object
        try:
            so = Scraper(dirpath + '/' + filename, row[1], row[2])
        except Exception as e:
            print(e)
            return
        
        # get csrf from login page
        csrf, session = so.get_login()

        # Return early if CSRF isn't found
        if csrf == '':
            return

        # login with csrf
        session = so.login_and_request(csrf, session)

        # get inbox page and return content
        response = so.get_request(session)

        # scrape response
        data = so.scrape(response)

        # Parse data
        parsed = so.parse(data)

        # Get rid of wierd spanish characters that don't do ASCII
        so.normalize(parsed)

        # Add new data to JSON and return false if there is none
        if so.append(parsed):
            changes.update({row[1]:row[2]})


    # Allow for multithreading and progress tracking
    threadlist = []

    # Iterate through each missionary in the object and create and use a scraper object to scrape the website for their data
    for row in reader:
        # Print out progress

        # Instantiate Thread
        t = threading.Thread(target=scrapingprocess, args=(row,))
        threadlist.append(t)
    
    # Start the threads and have them run in parallel
    for thread in threadlist:
        thread.start()

    # Wait to continue the program until all threads have finished running.
    for thread in threadlist:
        thread.join()
        print(str(round((threadlist.index(thread) / num_lines * 100), 2)) + " Percent Complete.")

    # Compile a list of the missionaries that have had changes in their accounts and save it to a text file called changelog.txt
    # Save file content to append at the beginning; If file doesn't exist, except error
    try:
        changelog = open('changelog.txt', 'r')
        temp = changelog.read()
        changelog.close()
    except:
        temp = ''
    # Prepend content and write old data back to file
    changelog = open('changelog.txt', 'w')
    changelog.write(str(datetime.now()))
    changelog.write('\n')
    changelog.write('The people with the following login data have had changes to their accounts:')
    changelog.write('\n')
    changelog.write(json.dumps(changes, indent=4))
    changelog.write('\n')
    changelog.write(temp)
    changelog.close()

    print("Scan Complete.")
    input("Go check the file, 'changelog.txt' for the results of this scan (in the same folder as this program).\nPress enter to close this window.")


if __name__ == "__main__":
    main()
