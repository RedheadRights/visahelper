# Visa Tracker Software Requirements Specification

## Purpose

Facilitate the process of Chilean visa application for missionaries in Chile

- Automate the slow process of checking account information from the visa website
- Remove the need for missionaries to forward visa-related documents from their emails (A slow and unreliable method of notification)
- Provide a list of all missionaries with pending visa actions or documents requiring attention

## Design

All software will be developed using python 3

### cli.py

- Entry point of the program outside of the ‘src’ folder
- Necessary due in order to use PyInstaller to package and bundle the system into an application to be distributed
- Imports __main__.py and calls main() function

### __main__.py

- Controls flow of program
- Defines constants such as file paths
- Imports and uses scraper.py module to scrape information from the visa website for each set of data from database.csv
- Implements multi-threading to allow the application to execute much faster, due to waiting times necessary for making http requests
- Writes output from the application to changelog.txt
- Saves previously retrieved data to logs folder in json format

### scraper.py

- Uses Requests python module to make http requests to the visa tracking website.
- Handles login process and navigates to the inbox page
- Uses BeautifulSoup package to scrape retrieved html for csrf token and the desired information from the inbox page

### database.csv

- Snippet of a Microsoft Excel spreadsheet saved in comma-delimited format
- Contains names, emails, and passwords for each account taken from a master spreadsheet kept by each mission

## Deployment

- Application is packaged using PyInstaller to compress into one executable file
- Executable file is distributed in a folder where the user will place their own database.csv file before launching
- PyInstaller arguments are:
    cli.py --name visascraper --onefile

## Manual

- User instructions can be found in the "Visa Helper Instructions.docx" file in this repository
*User instructions written in word file format for ease of use for the average user*
