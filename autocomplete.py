import curses
from curses import wrapper
import os
from Trie import Trie

def isWordChar(char):
    ascii = ord(char)
    return 65 <= ascii <= 90 or 97 <= ascii <= 122 or 48 <= ascii <= 57 or char in "_'"

def main(stdscr : curses.window):

    curses.init_pair(1, 226, 0)
    curses.init_pair(2, 241, 0)
    curses.init_pair(3, 10, 0)
    YELLOW_ON_BLACK = curses.color_pair(1)
    GREY_ON_BLACK = curses.color_pair(2)
    GREEN_ON_BLACK = curses.color_pair(3)

    def setup_windows():
        stdscr.erase()
        ht, wd = stdscr.getmaxyx()
        box_win = stdscr.subwin(ht // 3, wd, 0, 0)
        box_win.box()
        box_win.refresh()
        status_win = stdscr.subwin(ht // 3 - 2, wd - 2, 1, 1)
        status_win.refresh()
        status_win.scrollok(True)
        box_win = stdscr.subwin(ht // 3, wd, ht // 3, 0)
        box_win.box()
        box_win.refresh()
        dict_win = stdscr.subwin(ht // 3 - 2, wd - 2, ht // 3 + 1, 1) 
        dict_win.refresh()
        box_win = stdscr.subwin(ht // 3, wd, ht // 3 * 2, 0)
        box_win.box()
        box_win.refresh()
        input_win = stdscr.subwin(ht // 3 - 2, wd - 2, ht // 3 * 2 + 1, 1) 
        input_win.refresh()
        return [status_win, dict_win, input_win]

    def get_input(windows, trie:Trie=None):
        status_win, dict_win, input_win = windows
        ht, wd = input_win.getmaxyx()
        text = []
        prevWord = None
        pos = 0
        tabbed = False
        input_win.cursyncup()
        stdscr.refresh()

        while True:
            key = stdscr.getch()
            if key == curses.KEY_RESIZE:
                windows = setup_windows()  # resize window
                status_win.addstr(f"{stdscr.getmaxyx()} Key: {key} Str: {''.join(text)}\n")
                status_win.refresh()
                continue

            if tabbed is not False and key not in (9, 351):
                text[wordL:wordR] = [*currWord + casefunc(nearestWords[tabbed][len(currWord):])]
                pos = wordL + len(nearestWords[tabbed])
                tabbed = False

            if key in (curses.KEY_BACKSPACE, 8, 127) and pos > 0:
                pos -= 1
                text[pos:pos+1] = []
            elif key == curses.KEY_DC and pos < len(text):
                text[pos:pos+1] = []
            elif key in (curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN):
                pos += {curses.KEY_LEFT: -1, curses.KEY_RIGHT: 1, curses.KEY_UP: -wd, curses.KEY_DOWN: wd}[key]
                pos = min(len(text), max(pos, 0))
            elif key == 9 and nearestWords:  # TAB
                if tabbed is False: tabbed = 0
                else: tabbed = (tabbed + 1) % len(nearestWords)
            elif key == 351 and nearestWords:  # Shift-TAB
                if tabbed is False: tabbed = -1 % len(nearestWords)
                else: tabbed = (tabbed - 1) % len(nearestWords)
            elif 32 <= key <= 126:
                text[pos:pos] = chr(key)
                pos += 1
            elif key == 27: break
            else:
                status_win.addstr(f"{stdscr.getmaxyx()} Key: {key} Str: {''.join(text)}\n")
                status_win.refresh()
                continue

            # detect word on cursor position
            if not (pos > 0 and isWordChar(text[pos-1])) and not (pos < len(text) and isWordChar(text[pos])):
                currWord = None
            else:
                wordL = wordR = pos
                while wordL > 0 and isWordChar(text[wordL-1]): wordL -= 1
                while wordR < len(text) and isWordChar(text[wordR]): wordR += 1
                currWord = ''.join(text[wordL:wordR])

            dict_win.erase()
            input_win.erase()

            # autocomplete
            if currWord:
                if prevWord != currWord:
                    nearestWords = trie.nearestAutocomplete(currWord.lower())
                    prevWord = currWord
                    tabbed = False
                dict_win.addstr(f"Current word: ")
                dict_win.addstr(currWord, GREEN_ON_BLACK)
                dict_win.addstr('\n')
                dict_win.addstr('  '.join(nearestWords), GREY_ON_BLACK)
                input_win.addstr(''.join(text[:wordL]))
                input_win.addstr(currWord, YELLOW_ON_BLACK)
                if nearestWords:
                    casefunc = str.upper if currWord.isupper() else lambda x: x
                    if tabbed is False: input_win.addstr(casefunc(nearestWords[0][len(currWord):]), GREY_ON_BLACK)
                    else: input_win.addstr(casefunc(nearestWords[tabbed][len(currWord):]), YELLOW_ON_BLACK)
                input_win.addstr(''.join(text[wordR:]))
            else:
                prevWord = currWord
                input_win.addstr(''.join(text))

            status_win.addstr(f"{stdscr.getmaxyx()} Key: {key} Str: {''.join(text)}\n")
            status_win.refresh()
            dict_win.refresh()
            input_win.move(*divmod(pos if tabbed is False else wordL + len(nearestWords[tabbed]), wd))
            input_win.cursyncup()
            input_win.refresh()


    os.system("cls" if os.name == "nt" else "clear")
    print("")
    trie = Trie.fromTextFile('large_dict.txt')
    get_input(setup_windows(), trie)


wrapper(main)