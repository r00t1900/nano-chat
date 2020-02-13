# _*_coding:utf-8 _*_
# @Time    : 2020/2/12 18:42
# @Author  : Shek 
# @FileName: windows.py
# @Software: PyCharm
import curses
import datetime
import threading
import config


def current_datetime(format_str: str = '%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.now().strftime(format_str)


CODE_CN = ('\u0391', '\uffe5')  # chinese characters and commas
CODE_CUSTOM = ()  # set the custom code range and add it to code_sets
SEND_KEYS = [10, 13]  # \r 13 and \n 10
QUIT_KEYS = [ord('D') - 0x40]  # Ctrl-D
CODE_SETS = [CODE_CN]


def cn_count(text: str, code_all=None):
    if code_all is None:
        code_all = CODE_SETS
    count = 0
    for code_range in code_all:
        for ch in text:
            if code_range[0] <= ch <= code_range[1]:
                count += 1
    return count


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


class CreateWindow:
    def __init__(self, xy: tuple, wh: tuple, h_enabled: bool = True, h_text: str = '',
                 h_style=curses.A_NORMAL, refresh_now: bool = True, cn_count: int = 0):
        """
        Parent class "CreateWindow" to be inherited which will automatically create window object by default
        """
        self.win = self.__window_create(xy, wh, h_enabled, h_text, h_style, cn_count)  # create a window
        if refresh_now:  # refresh window once it was created
            self.refresh()
        # height and width
        self.height, self.width = self.win.getmaxyx()
        # align format string template:
        self.ft_align_right = '{:>' + str(self.width - 1) + '}'  # align right
        self.ft_align_left = '{:<' + str(self.width - 1) + '}'  # align left
        self.ft_align_center = '{:^' + str(self.width - 1) + '}'  # align center raw

    def align_center(self, text: str):
        ft_str = '{:^' + str(self.width - 1 - cn_count(text)) + '}'
        return ft_str.format(text)

    def align_right(self, text: str):
        ft_str = '{:>' + str(self.width - 1 - cn_count(text)) + '}'
        return ft_str.format(text)

    def align_left(self, text: str):
        ft_str = '{:<' + str(self.width - 1 - cn_count(text)) + '}'
        return ft_str.format(text)

    @staticmethod
    def __text_fill(win_obj, xy: tuple, text: str, w_win: int = 0, style=None, cn_count: int = 0):
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
            text = '{}{}'.format(text, ' ' * (w_win - len(text) - cn_count))
        win_obj.addstr(p_y, p_x, text) if style is None else win_obj.addstr(p_y, p_x, text, style)  # custom style

    def __window_create(self, xy: tuple, wh: tuple, h_enabled: bool = True, h_text: str = '', h_style=0, cn_count=0):
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
            self.__text_fill(n_win, (0, 0), '{}{}'.format(h_text, pos_size), width, h_style, cn_count)
        return n_win

    def refresh(self):  # refresh window
        self.win.refresh()

    def press_key_continue(self):  # used for waiting
        self.win.getkey()


class StatusWindow(CreateWindow):
    # status elements are:
    # datetime, addr and online-status of friend to chat, log cache count, etc
    # def __init__(self):
    #     super(StatusWindow, self).__init__()
    #     self.flag_upd_datetime = False

    def __init__(self, xy: tuple, wh: tuple, h_enabled: bool = True, h_text: str = '',
                 h_style=curses.A_REVERSE, refresh_now: bool = True, cn_count: int = 0):
        super().__init__(xy, wh, h_enabled, h_text, h_style, refresh_now, cn_count)  # inherit from parent
        self.flag_upd_datetime = False

    def upd_scr_datetime(self):
        self.win.move(1, 0)  # move cursor to (1,0)
        self.win.clrtoeol()  # clear from (1,0) to end-of-line(EOL)
        self.win.addstr(1, 0, self.datetime)
        self.win.move(1, 0)

    def __upd_datetime(self):
        self.datetime = current_datetime()

    def __upd_datetime_loop(self):
        while self.flag_upd_datetime:
            self.__upd_datetime()

    def upd_datetime_thread_start(self):
        self.flag_upd_datetime = True
        threading.Thread(target=self.__upd_datetime_loop).start()

    def upd_datetime_thread_stop(self):
        self.flag_upd_datetime = False


class ChatWindow(CreateWindow):
    # chat logs pipe need to be added
    # logic of refreshing chat logs need to be declared
    def __init__(self, xy: tuple, wh: tuple, h_enabled: bool = True, h_text: str = '',
                 h_style=curses.A_REVERSE, refresh_now: bool = True, cn_count: int = 0):
        super().__init__(xy, wh, h_enabled, h_text, h_style, refresh_now, cn_count)  # inherit from parent
        self.last_chat_logs = []
        self.t_add_str_sets = []
        self.page_offset = 0
        self.flag_page_changed = False

    def __timestamp_manager(self, chat_var: list, index: int, interval: int):
        timestamp = None
        n_dt = datetime.datetime.strptime(chat_var[index]['time'], '%Y-%m-%d %H:%M:%S')  # present datetime
        if index:  # from line 1 to the end
            p_dt = datetime.datetime.strptime(chat_var[index - 1]['time'], '%Y-%m-%d %H:%M:%S')  # previous datetime
            delta = n_dt - p_dt
            if delta.total_seconds() >= interval:  # print datetime in the middle
                timestamp = '{} {}:{:02d}'.format('上午' if 0 <= n_dt.hour <= 12 else '下午', n_dt.hour, n_dt.minute)
        else:  # line 0
            timestamp = '{} {}:{:02d}'.format('上午' if 0 <= n_dt.hour <= 12 else '下午', n_dt.hour, n_dt.minute)

        if timestamp is not None:
            self.t_add_str_sets.append([self.align_center(timestamp), curses.color_pair(2)])

    def page_up(self):
        begin_index = -(self.height - 1) + self.page_offset
        if begin_index > -(len(self.t_add_str_sets)):
            self.page_offset -= 1
            self.flag_page_changed = True
            return True
        else:
            return False

    def page_down(self):
        if self.page_offset < 0:
            self.page_offset += 1
            self.flag_page_changed = True
            return True
        else:
            return False

    def page_bottom(self):
        while self.page_down():
            pass

    def page_top(self):
        while self.page_up():
            pass

    def upd_scr_chat_logs(self, chat_var: list, debug_var: list):
        # chat logs changed or pageup/pagedown keys pressed wil do screen update(won't do any if remains the same)
        if self.last_chat_logs != chat_var or self.flag_page_changed:
            self.t_add_str_sets = []
            self.win.move(1, 0)  # move cursor to (1,0)
            self.win.clrtoeol()  # clear from (1,0) to end-of-line(EOL)
            datetime_interval_seconds = 5
            msg_len_r = 30 if self.width < 90 else self.width // 3  # min of msg width is 30
            # draw each row with individual chat log
            for i in range(len(chat_var)):
                self.__timestamp_manager(chat_var, i, datetime_interval_seconds)  # add timestamp automatically

                msg_raw, msg_clips, r_len = chat_var[i]['message'], [], len(chat_var[i]['from'])  # r-len: role str len

                # bug fixed on 2020-2-13 11:28 chinese character message width limit issue
                while msg_raw:
                    idx = msg_len_r
                    clip = msg_raw[:idx]
                    while len(clip) + cn_count(clip) > msg_len_r:
                        idx -= 1
                        clip = msg_raw[:idx]
                    msg_clips.append(clip)
                    msg_raw = msg_raw[idx:]
                # core operation here
                for j in range(len(msg_clips)):
                    # delta between standard len and current len
                    m_len = msg_len_r - len(msg_clips[j]) - cn_count(msg_clips[j])  # calc the count of blank space
                    if chat_var[i]['from'] == config.C_SEND_ROLE_NAME:  # align right for self
                        msg = msg_clips[j] + ('%s' % (' ' * (1 + r_len + m_len)) if j else '<%s' % chat_var[i]['from'])
                        self.t_add_str_sets.append([self.align_right(msg), 0])  # update
                    else:  # align left for friend
                        msg = ('%s' % (' ' * (1 + r_len + m_len)) if j else '%s>' % chat_var[i]['from']) + msg_clips[j]
                        self.t_add_str_sets.append([self.align_left(msg), 0])  # update

            bgn_i = -(self.height - 1) + self.page_offset  # begin_index
            dest_i = len(self.t_add_str_sets) + self.page_offset  # dest_index
            for i, a in enumerate(self.t_add_str_sets[bgn_i:dest_i]):
                self.win.addstr(i + 1, 0, a[0], a[1])  # add to Chat-Screen data
            self.win.move(1, 0)  # move cursor to (1,0)
            self.last_chat_logs = chat_var.copy()  # copy to last_chat_logs for compare the next time
            self.flag_page_changed = False  # resume page-changed status to False


class SendWindow(CreateWindow):
    # [send] button need to be added
    def __init__(self, xy: tuple, wh: tuple, h_enabled: bool = True, h_text: str = '',
                 h_style=curses.A_REVERSE, refresh_now: bool = True, cn_count: int = 0):
        super().__init__(xy, wh, h_enabled, h_text, h_style, refresh_now, cn_count)  # inherit from parent
        self.message = ''
        self.role_name = config.C_SEND_ROLE_NAME
        self.unknown_characters = []

    def set_role_name(self, role_name: str):
        self.role_name = role_name

    def upd_scr_message(self):
        self.win.move(1, 0)  # move cursor to (1,0): the begin of the window's second row
        self.win.clrtobot()  # clear from (1,0) to end-of-window)
        self.win.addstr(1, 0, self.message + '_')
        self.win.move(1, 0)

    def input(self, ch_code: int):
        if ch_code == curses.KEY_BACKSPACE:
            if len(self.message):  # delete last character when length is more than 1
                self.message = self.message[:-1]
        else:  # add ASCII character to EOL
            self.message += chr(ch_code)

    def overwrite_message(self, msg_text: str):
        self.message = msg_text

    def append_message(self, append_text: str):
        self.message += append_text

    def show_send(self, chat_var: list, send_succeed: bool):
        if len(self.message):
            apx = '' if send_succeed else ' [sent failed]'
            chat_var.append({'time': current_datetime(), 'message': self.message + apx, 'from': self.role_name})
            self.message = ''


class DebugWindow(CreateWindow):
    # debug information pipe need to be added
    # logic of refreshing debug logs need to be declared
    def __init__(self, xy: tuple, wh: tuple, h_enabled: bool = True, h_text: str = '',
                 h_style=curses.A_REVERSE, refresh_now: bool = True, cn_count: int = 0):
        super().__init__(xy, wh, h_enabled, h_text, h_style, refresh_now, cn_count)  # inherit from parent
