# _*_coding:utf-8 _*_
# @Time    : 2020/2/11 12:00
# @Author  : Shek 
# @FileName: cursesUI.py
# @Software: PyCharm

from curses import wrapper
from module.windows import *
import pprint
import time

SEND_KEYS = [10, 13]  # \r 13 and \n 10
QUIT_KEYS = [ord('D') - 0x40]  # Ctrl-D


def color_pair_configure():
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)  # FG BLACK BG GREEN
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # FG GREEN BG BLACK


def preconfigure(scr_obj):
    color_pair_configure()  # for colorful display in terminal
    scr_obj.clear() or scr_obj.refresh()  # init the std_scr and clear window

    max_y, max_x = scr_obj.getmaxyx()  # get max window size
    welcome_str = '(%d x %d)' % (max_x, max_y)
    welcome_str += ' terminal size is too small to run :(' if max_y < 20 or max_x < 60 else ' press any key to GO :)'
    scr_obj.addstr(welcome_str)
    scr_obj.refresh()
    scr_obj.getkey()  # inform the max window size
    if max_y < 20 or max_x < 60:  # quit program if terminal size is too small
        return False, ()
    # argument sets for each window object here:
    a_st = {'xy': (0, 0), 'wh': (max_x - 30, 3), 'h_text': 'Status'}  # status
    a_sd = {'xy': (0, max_y - 6), 'wh': (max_x - 30, 6), 'h_text': 'Send'}  # send
    a_ct = {'xy': (0, 3), 'wh': (max_x - 30, max_y - a_st['wh'][1] - a_sd['wh'][1]), 'h_text': 'Chat'}  # chat
    a_dg = {'xy': (max_x - 30, 0), 'wh': (30, max_y), 'h_text': 'Debug'}  # debug

    w_st, w_ct, w_sd, w_dg = StatusWindow(**a_st), ChatWindow(**a_ct), SendWindow(**a_sd), DebugWindow(**a_dg)
    return True, (w_st, w_ct, w_sd, w_dg, (max_y, max_x))


def main(std_scr):
    status, elements = preconfigure(scr_obj=std_scr)  # get 4 win object and max terminal size
    if not status:  # screen is too small to run, quit
        return
    std_scr.nodelay(True)  # for getch()
    # main begin here:
    w_status, w_chat, w_send, w_debug, max_yx = elements
    chat_logs, debug_logs = [], []
    curses.curs_set(0)  # disable cursor blinking
    assert isinstance(w_status, StatusWindow)
    assert isinstance(w_chat, ChatWindow)
    assert isinstance(w_send, SendWindow)
    assert isinstance(w_debug, DebugWindow)
    # data-updating-thread begin:
    w_status.upd_datetime_thread_start()
    # end
    # screen updating in time-loop begin:
    while True:
        # update window data below:
        w_status.upd_scr_datetime()
        w_send.upd_scr_message()
        w_chat.upd_scr_chat_logs(chat_var=chat_logs, debug_var=debug_logs)

        # none-output-refresh window objects below:
        w_status.win.noutrefresh()
        w_send.win.noutrefresh()
        w_chat.win.noutrefresh()

        # physical screen refresh
        curses.doupdate()

        # CATCH KEY HERE
        ch = std_scr.getch()  # hide cursor to lower-right corner and pause
        if ch == -1:  # return -1 when no input
            continue
        elif 0x20 <= ch <= 0x7e or ch in [curses.KEY_BACKSPACE]:  # input visible character solution: input to message
            w_send.input(ch)
        else:  # invisible character solution
            if ch in QUIT_KEYS:  # ctrl + D: Quit
                break
            elif ch in SEND_KEYS:  # ctrl + G: send
                w_send.send(chat_var=chat_logs)
                w_chat.page_bottom()
            elif ch == curses.KEY_PPAGE:  # PageUp
                w_chat.page_up()
            elif ch == curses.KEY_NPAGE:  # PageDown
                w_chat.page_down()
    # end

    # stop all data thread
    w_status.upd_datetime_thread_stop()


wrapper(main)
