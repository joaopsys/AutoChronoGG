# AutoChronoGG
A Python script to automatically get the daily coins on Chrono.gg

**Format:**

The format is pretty straightforward, the program only needs your cookie in order to have access to your Chrono.gg session.

    Usage: ./chronogg.py <Cookie (first execution only)>
    
In order to obtain your cookie, you can press CTRL+SHIFT+J while on Chrono.gg (CTRL+SHIFT+K on Firefox) and type **document.cookie**. Then use the whole string (quotes included) as the argument.
**You only need need to do this once because AutoChronoGG will remember your cookie (if valid).**

**Optional: Crontab**
This script is meant to be run once per day, so here goes a crontab example for the lazy:

    0 17 * * * root cd /usr/local/bin/ && ./chronogg.py
