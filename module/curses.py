# _*_coding:utf-8 _*_
# @Time    : 2020/2/13 19:53
# @Author  : Shek 
# @FileName: curses.py
# @Software: PyCharm
import curses
from module.windows import StatusWindow, ChatWindow, SendWindow, DebugWindow
import config


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


def curses_main_for_wrapper(std_scr, pair_obj, chat_var: list):
    pre_conf_status, elements = preconfigure(scr_obj=std_scr)  # get 4 win object and max terminal size
    if not pre_conf_status:  # screen is too small to run, quit
        pair_obj.stop_recv_loop()
        return
    std_scr.nodelay(True)  # for getch()
    # main begin here:
    w_status, w_chat, w_send, w_debug, max_yx = elements

    curses.curs_set(0)  # disable cursor blinking
    assert isinstance(w_status, StatusWindow)
    assert isinstance(w_chat, ChatWindow)
    assert isinstance(w_send, SendWindow)
    assert isinstance(w_debug, DebugWindow)
    # debugger initialize here

    w_chat.init_debug_object(w_debug)

    # data-updating-thread begin:
    w_status.upd_datetime_thread_start()

    # screen updating in time-loop begin:
    while True:
        # update window data below:
        w_status.upd_scr_datetime()
        w_send.upd_scr_message()
        # w_chat.upd_scr_chat_logs(chat_var=chat_logs, debug_var=debug_logs)
        w_chat.upd_scr_chat_logs(chat_var=chat_var)
        w_debug.upd_scr_debug_logs()

        # none-output-refresh window objects below:
        w_status.win.noutrefresh()
        w_send.win.noutrefresh()
        w_chat.win.noutrefresh()
        w_debug.win.noutrefresh()

        # physical screen refresh
        curses.doupdate()

        # CATCH KEY HERE
        ch = std_scr.getch()  # hide cursor to lower-right corner and pause
        if ch == -1:  # return -1 when no input
            continue
        elif 0x20 <= ch <= 0x7e or ch in [curses.KEY_BACKSPACE]:  # input visible character solution: input to message
            w_send.input(ch)
        else:  # invisible character solution
            if ch in config.QUIT_KEYS:  # ctrl + D: Quit
                break
            elif ch in config.SEND_KEYS:  # Enter: send
                if len(w_send.message):
                    send_result, send_inf = pair_obj.send(text=w_send.message)
                    w_send.publish_send_status(chat_var=chat_var, send_succeed=send_result)
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
                unknown = ['%02x' % ch]  # real-time decode chinese characters
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
    pair_obj.stop_recv_loop()
