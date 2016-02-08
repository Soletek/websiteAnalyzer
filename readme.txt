Website status analysis tool

Copyright(c) Tuukka Kurtti 2016


1. Running

Start core.py with Python version 2.7
(The program is tested with Python 2.7.11)


2. Implemented Features

- Ability to specify periodical checks on URL addresses. Checks the site online
    status, determines if the page content fulfills the set requirements and
    measures the latency.
- Logging for all the conducted checks.
- Page cache for latest downloaded page from every URL address
- A single page HTTP server interface. All data about is collected on the web page.
   (default port: 8080)
- Very simple command prompt with very limited number of available commands.


3. Configuration

Config file containing the basic setup is located at config/config.ini

The check scheduler can be configured with a json file. The monitored URLs, 
check intervals and content check conditionals can be configured. 
Per site logging and page caching can also be disabled for monitored web pages.
There's an example json file in the config folder.

