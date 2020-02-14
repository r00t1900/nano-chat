# _*_coding:utf-8 _*_
# @Time    : 2020/2/13 19:53
# @Author  : Shek 
# @FileName: curses.py
# @Software: PyCharm
"""
functions or loader related to curses UI
(classes related please referer to module/ui/windows.py)

The main function is main4curses_wrapper(), many other function calls are served for it.
Referer to it's function reference for more details.
"""
import curses
from conf import config
from curses import wrapper
from module.ui.windows import StatusWindow, ChatWindow, SendWindow, DebugWindow, HelpWindow
from module.communication.nanomsg_pair import PairObject

STAT_LINES = 3
SEND_LINES = 6
HELP_LINES = 6
DEBUG_COLS = 30


def process_chinese_characters(ch_current_got, ch_windows, send_windows_obj):
    """
    sub function for main() of curses.wrapper(), repeat reading get_ch() and combine them to chinese characters
    or commas if requirement matched. The requirement is simple: if continue to uninterruptedly read for more than 2(
    more than 3 in total because there is already a `ch_current_got` been sent here) then we consider it as a chinese
    characters or commas, considering chinese characters or commas take hex length of 3 or 4
    It returns nothing but directly action on `send_windows_obj`
    :param ch_current_got:previously got value of get_ch()
    :param ch_windows:the host windows of get_ch() which send `ch_current_got` here
    :param send_windows_obj:sendWindow object
    :return:
    """
    unknown = ['%02x' % ch_current_got]  # real-time decode chinese characters
    while True:
        ch2 = ch_windows.getch()
        if ch2 == -1:  # means no user input
            break
        else:  # got user input and then collect it
            unknown.append('%02x' % ch2)  # of course: in hex string format
    if len(unknown) >= 3:
        b = bytes.fromhex(''.join(unknown))  # join to a hex-string and convert to bytes
        send_windows_obj.append_message(b.decode(config.DATA_ENCODING))  # sync content of current message


def color_pair_configure():
    """
    do your color pair initialize here
    :return:
    """
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)  # FG BLACK BG GREEN
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # FG GREEN BG BLACK


def pre_configure(scr_obj):
    """
    do some requirement test and lazy job such as windows arrangement for curses, divided into 4 windows:
    Status,Chat,Send and Debug
    :param scr_obj: if the terminal size does not meet the minimum, use it to send a warning and quit, just for this
    :return:
    """
    # 1. test terminal size
    scr_obj.clear() or scr_obj.refresh()  # init the std_scr and clear window
    max_y, max_x = scr_obj.getmaxyx()  # get max window size
    welcome_str = '(%d x %d)' % (max_x, max_y)
    if max_y < 20 or max_x < 60:  # quit program if terminal size is too small
        welcome_str += ' terminal size is too small to run :('
        scr_obj.addstr(welcome_str)
        scr_obj.refresh()
        scr_obj.getkey()  # inform the max window size
        return False, ()

    # 2. init color pair when necessary
    color_pair_configure()  # for colorful display in terminal

    # 3. create 4 window for different usages
    # status
    a_st = {'xy': (0, 0), 'wh': (max_x - DEBUG_COLS, STAT_LINES), 'h_text': 'Status'}
    # send
    a_sd = {'xy': (0, max_y - SEND_LINES), 'wh': (max_x - DEBUG_COLS, SEND_LINES), 'h_text': 'Send'}
    # chat
    a_ct = {'xy': (0, STAT_LINES), 'wh': (max_x - DEBUG_COLS, max_y - a_st['wh'][1] - a_sd['wh'][1]), 'h_text': 'Chat'}
    # debug
    a_dg = {'xy': (max_x - DEBUG_COLS, 0), 'wh': (DEBUG_COLS, max_y - HELP_LINES), 'h_text': 'Debug'}
    # help
    a_hp = {'xy': (max_x - DEBUG_COLS, max_y - HELP_LINES), 'wh': (DEBUG_COLS, HELP_LINES), 'h_text': 'Help'}

    #  use arguments above to create each window object
    w_st, w_ct, w_sd, w_dg = StatusWindow(**a_st), ChatWindow(**a_ct), SendWindow(**a_sd), DebugWindow(**a_dg)
    w_hp = HelpWindow(**a_hp)

    return True, (w_st, w_ct, w_sd, w_dg, w_hp, (max_y, max_x))


def key_pressed_solution(std_scr, stw: StatusWindow, ctw: ChatWindow, sdw: SendWindow, dgw: DebugWindow,
                         hpw: HelpWindow, comm: PairObject, ct_storage: list):
    """
    A branch to resolve the key pressed situation
    :param std_scr: window object that get_ch() function at
    :param stw: for function calls of Status Windows Object
    :param ctw: for function calls of Chat Windows Object
    :param sdw: for function calls of Send Windows Object
    :param dgw: for function calls of Debug Windows Object
    :param hpw: for function calls of Help Windows Object
    :param comm: for function calls to communication object
    :param ct_storage: for chat logs variable sharing among the program
    :return:
    0:break loop
    1: pass loop
    2: continue loop and ignore code below(mostly 1 is equal to 2)
    """
    ch = std_scr.getch()  # hide cursor to lower-right corner and pause
    if ch == -1:  # return -1 when no input
        # continue
        return 2
    elif 0x20 <= ch <= 0x7e or ch in [curses.KEY_BACKSPACE]:  # input visible character solution: input to message
        sdw.input(ch)
    else:  # invisible character solution
        if ch in config.QUIT_KEYS:  # ctrl + D: Quit
            # break
            return 0
        elif ch in config.SEND_KEYS:  # Enter: send
            if len(sdw.message):
                send_result, send_inf = comm.send(text=sdw.message)
                sdw.publish_send_status(chat_var=ct_storage, send_succeed=send_result)
            ctw.page_bottom()
        elif ch == curses.KEY_PPAGE:  # PageUp key
            ctw.page_up()
        elif ch == curses.KEY_NPAGE:  # PageDown key
            ctw.page_down()
        elif ch == curses.KEY_HOME:  # Home key
            ctw.page_top()
        elif ch == curses.KEY_END:  # End key
            ctw.page_bottom()
        else:
            process_chinese_characters(ch_current_got=ch, ch_windows=std_scr, send_windows_obj=sdw)
    return 1


def main4curses_wrapper(std_scr, comm_obj, chat_logs_storage: list):
    """
    function-based argument for curses.wrapper
    :param std_scr: the raw window object that was first created
    :param comm_obj: communication mode object, by default is a nanomsg-pair mode object
    :param chat_logs_storage: a list variable for chatWindow to display chat logs
    :return:
    """
    # I.PRECONFIGURE HERE:

    pre_conf_status, elements = pre_configure(scr_obj=std_scr)  # get 4 win object and max terminal size
    if not pre_conf_status:  # screen is too small to run, quit
        # FUNCTIONS THAT NEED TO BE CALLED WHEN PROGRAMS EXIT:
        comm_obj.stop_recv_loop()
        return
    w_status, w_chat, w_send, w_debug, w_help, max_yx = elements
    std_scr.nodelay(True)  # for getch()
    curses.curs_set(0)  # disable cursor blinking
    # assert isinstance(w_status, StatusWindow)
    # assert isinstance(w_chat, ChatWindow)
    # assert isinstance(w_send, SendWindow)
    # assert isinstance(w_debug, DebugWindow)
    # assert isinstance(w_help, HelpWindow)

    # II.CALL FUNCTIONS THAT RUN FOR ONE TIMES BELOW:

    # 1.debugger initialize here
    w_chat.init_debug_object(w_debug)  # init debugger for ChatWindow
    w_send.init_debug_object(w_debug)  # init debugger for SendWindow

    # 2.pull trigger of threads here
    w_status.upd_datetime_thread_start()  # start datetime sync thread here

    # 3.add help messages in once
    w_help.set_help_messages(config.C_HELP_LIST)
    w_help.upd_scr_help_message()  # update for 1 time is enough

    # III.CALL FUNCTIONS THAT RUN EVERY LOOP BELOW:

    while True:
        # FOR STATUS
        w_status.upd_scr_datetime()
        w_status.win.noutrefresh()
        # FOR CHAT
        w_chat.upd_scr_chat_logs(chat_var=chat_logs_storage)
        w_chat.win.noutrefresh()
        # FOR SEND
        w_send.upd_scr_message()
        w_send.win.noutrefresh()
        # FOR DEBUG
        w_debug.upd_scr_debug_msgs()
        w_debug.win.noutrefresh()
        # FOR HELP
        # w_help.upd_scr_help_message() # just run once so I put it to 'I' area above
        w_help.win.noutrefresh()

        # FOR PHYSICAL SCREEN
        # physical screen refresh
        curses.doupdate()

        # KEY PRESSED SOLUTION:

        # 1.Single key: shortcuts or a single ASCII character input
        # 2.Multiple keys(Uninterruptedly input): mostly chinese characters and need to do real-time decoding

        n_step = key_pressed_solution(std_scr, w_status, w_chat, w_send, w_debug, w_help, comm_obj, chat_logs_storage)

        # 0 means break loop, 1 means pass loop and 2 means continue loop and ignore code below(mostly 1 is equal to 2)
        if n_step == 0:
            break
        elif n_step == 1:
            pass
        elif n_step == 2:
            continue

    # IV.Functions that need to be called when break the loop:

    # 1.stop threading
    w_status.upd_datetime_thread_stop()  # stop threading of datetime sync
    comm_obj.stop_recv_loop()  # stop threading of chat_logs sync


def curses_boot_loader(protocol: str, addr: str, is_server: bool):
    """
    a standard binder for nanomsg and curses and I think I can call it a loader either
    :param protocol: arguments for nanomsg
    :param addr: arguments for nanomsg
    :param is_server: use nnpy.Socket.bind if `is_server`==1 else nnpy.Socket.connect
    :return:
    """
    chat_logs = []
    comm_module = PairObject()
    comm_conf_status, comm_err_inf = comm_module.start(protocol, addr, is_server=is_server)
    if comm_conf_status:
        comm_module.enable_recv_loop()
        comm_module.start_recv_loop(chat_var=chat_logs)
        wrapper(main4curses_wrapper, comm_module, chat_logs)
        comm_module.stop()  # always remember to call this after wrapper
    else:
        print('{}\n{}'.format(config.C_WRAPPER_STOPPED_WITH_FAILURE_TEXT_SUFFIX, comm_err_inf))
