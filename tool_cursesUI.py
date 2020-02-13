# _*_coding:utf-8 _*_
# @Time    : 2020/2/11 12:00
# @Author  : Shek 
# @FileName: cursesUI.py
# @Software: PyCharm

from curses import wrapper
from module.windows import *
from module.pair import PairObject


def main(std_scr, pair_object: PairObject):
    # get 4 win object and max terminal size
    pre_conf_status, elements = preconfigure(scr_obj=std_scr)
    if not pre_conf_status:  # screen is too small to run, quit
        return
    std_scr.nodelay(True)  # for getch()
    # main begin here:
    w_status, w_chat, w_send, w_debug, max_yx = elements

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
        nn = []
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
            elif ch in SEND_KEYS:  # Enter: send
                if len(w_send.message):
                    send_result = pair_object.send(text=w_send.message)
                    w_send.show_send(chat_var=chat_logs, send_succeed=send_result)
                w_chat.page_bottom()
            elif ch == curses.KEY_PPAGE:  # PageUp key
                w_chat.page_up()
            elif ch == curses.KEY_NPAGE:  # PageDown key
                w_chat.page_down()
            elif ch == curses.KEY_HOME:  # Home key
                w_chat.page_top()
            elif ch == curses.KEY_END:  # End key
                w_chat.page_bottom()
            else:

                # real-time decode chinese characters
                unknown = ['%02x' % ch]
                while True:
                    ch2 = std_scr.getch()
                    if ch2 == -1:
                        break
                    else:
                        unknown.append('%02x' % ch2)
                if len(unknown) >= 3:
                    b = bytes.fromhex(''.join(unknown))
                    w_send.append_message(b.decode('utf-8'))
    # end

    # stop all data thread
    w_status.upd_datetime_thread_stop()


chat_logs, debug_logs = [], []
pair = PairObject()
pair_conf_status, err_inf = pair.configure('tcp', '*:4000', is_server=True)
if pair_conf_status:
    pair.enable_recv_loop()
    pair.start_recv_loop(chat_var=chat_logs)
    wrapper(main, pair)
else:
    print('init failed because:\n'.format(err_inf))
