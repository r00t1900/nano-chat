# _*_coding:utf-8 _*_
# @Time    : 2020/2/11 12:00
# @Author  : Shek 
# @FileName: feb11_curses.py
# @Software: PyCharm
import curses
from curses import wrapper


class CreateWindow:
    def __init__(self, xy: tuple, wh: tuple, h_enabled: bool = True, h_text: str = '',
                 h_style=curses.A_NORMAL, refresh_now: bool = True):
        """
        Parent class "CreateWindow" to be inherited which will automatically create window object by default
        """
        self.win = self.__window_create(xy, wh, h_enabled, h_text, h_style)  # create a window
        if refresh_now:  # refresh window once it was created
            self.refresh()

    @staticmethod
    def __text_fill(win_obj, xy: tuple, text: str, w_win: int = 0, style=None):
        """
        fill text to full width of window object
        :param win_obj: window object
        :param xy: pos to start
        :param text: text content
        :param w_win: width need to be specified, default is 0 meaning do not execute filling operation
        :param style: text style
        :return:
        """
        p_x, p_y = xy
        w_win -= 1  # to diff from neighbor window
        if len(text) > w_win:  # text length out of row_width and need to be limited
            text = text[:w_win - 2] + '..'
        elif w_win != 0:  # fill text to row_width
            text = '{}{}'.format(text, ' ' * (w_win - len(text)))
        win_obj.addstr(p_y, p_x, text) if style is None else win_obj.addstr(p_y, p_x, text, style)  # custom style

    def __window_create(self, xy: tuple, wh: tuple, h_enabled: bool = True, h_text: str = '', h_style=curses.A_NORMAL):
        """
        create a curses window object
        :param xy: pos of upper-left corner
        :param wh: width and height
        :param h_enabled: add header to the first row of the window
        :param h_text: header text
        :param h_style: header text's style
        :return: curses window object
        """
        p_x, p_y = xy
        width, height = wh
        n_win = curses.newwin(height, width, p_y, p_x)  # create window object of curses
        pos_size = '({},{}), {} x {}'.format(p_x, p_y, width, height)  # info text of position and area
        h_text = h_text if h_text == '' else '<%s> ' % h_text  # header text
        if h_enabled:  # fill the text with the same width of its window
            self.__text_fill(n_win, (0, 0), '{}{}'.format(h_text, pos_size), width, h_style)
        return n_win

    def refresh(self):  # refresh window
        self.win.refresh()

    def press_key_continue(self):  # used for waiting
        self.win.getkey()


class StatusWindow(CreateWindow):
    # status elements are:
    # datetime, addr and online-status of friend to chat, log cache count, etc
    pass


class ChatWindow(CreateWindow):
    # chat logs pipe need to be added
    # logic of refreshing chat logs need to be declared
    pass


class SendWindow(CreateWindow):
    # [send] button need to be added
    pass


class DebugWindow(CreateWindow):
    # debug information pipe need to be added
    # logic of refreshing debug logs need to be declared
    pass


def preconfigure(scr_obj):
    scr_obj.clear() or scr_obj.refresh()  # init the std_scr and clear window
    max_y, max_x = scr_obj.getmaxyx()  # get max window size
    welcome_str = '(%d x %d)' % (max_x, max_y)
    welcome_str += ' terminal size is too small to run :(' if max_y < 20 or max_x < 60 else ' press any key to GO :)'
    scr_obj.addstr(welcome_str)
    scr_obj.refresh() or scr_obj.getkey()  # inform the max window size
    if max_y < 20 or max_x < 60:  # quit program if terminal size is too small
        return
    # argument sets for each window object here:
    a_st = {'xy': (0, 0), 'wh': (max_x - 30, 3), 'h_text': 'Status', 'h_style': curses.A_REVERSE}  # status
    a_sd = {'xy': (0, max_y - 6), 'wh': (max_x - 30, 6), 'h_text': 'Send', 'h_style': curses.A_REVERSE}  # send
    a_ct = {'xy': (0, 3), 'wh': (max_x - 30, max_y - a_st['wh'][1] - a_sd['wh'][1]),
            'h_text': 'Chat', 'h_style': curses.A_REVERSE}  # chat
    a_dg = {'xy': (max_x - 30, 0), 'wh': (30, max_y), 'h_text': 'Debug', 'h_style': curses.A_REVERSE}  # debug

    w_st, w_ct, w_sd, w_dg = StatusWindow(**a_st), ChatWindow(**a_ct), ChatWindow(**a_sd), DebugWindow(**a_dg)
    return w_st, w_ct, w_sd, w_dg, (max_y, max_x)


def main(std_scr):
    w_status, w_chat, w_send, w_debug, max_yx = preconfigure(scr_obj=std_scr)  # get 4 win object and max terminal size

    std_scr.move(max_yx[0] - 1, max_yx[1] - 1) or std_scr.getkey()  # hide cursor to lower-right corner and pause


wrapper(main)
