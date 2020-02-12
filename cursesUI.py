# _*_coding:utf-8 _*_
# @Time    : 2020/2/11 12:00
# @Author  : Shek 
# @FileName: cursesUI.py
# @Software: PyCharm

from curses import wrapper
from module.windows import *

SEND_KEYS = [10, 13]  # \r 13 and \n 10
QUIT_KEYS = [ord('D') - 0x40]  # Ctrl-D


def main(std_scr):
    status, elements = preconfigure(scr_obj=std_scr)  # get 4 win object and max terminal size
    if not status:  # screen is too small to run, quit
        return

    # main begin here:
    w_status, w_chat, w_send, w_debug, max_yx = elements
    curses.curs_set(0)  # disable cursor blinking
    assert isinstance(w_status, StatusWindow)
    assert isinstance(w_chat, ChatWindow)
    assert isinstance(w_send, SendWindow)
    assert isinstance(w_debug, DebugWindow)
    # data updating in thread begin:
    # chat_logs = ['hi!']
    chat_logs = []
    debug_logs = []
    w_status.upd_datetime_thread_start()
    # end
    std_scr.nodelay(True)
    # screen updating in time-loop begin:
    while True:
        # update window data below:
        w_status.upd_scr_datetime()
        w_send.upd_scr_message()
        w_chat.upd_scr_chat_logs(chat_var=chat_logs)

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
    # end

    # stop all data thread
    w_status.upd_datetime_thread_stop()


# wrapper(main2)
wrapper(main)
