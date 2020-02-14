# _*_coding:utf-8 _*_
# @Time    : 2020/2/12 18:42
# @Author  : Shek 
# @FileName: windows.py
# @Software: PyCharm
"""
This is the classes libraries for curses windows that I usually use.
The parent class is CreateWindow, which functions only:
    1.provide 3 text-align functions
    2.create a curses window object by giving coordinate(x,y), area(width,length) and other optional arguments, instead
    of the old-fashion that put y before x in coordinate, which curses has kept for a very long time and now my class
    makes me fell much more better :)
    3.fill first row with header-text in REVERSE MODE(optional)
    4.provide a shadow function:refresh(), which simply point to self.win.refresh(). But here I do not figure out the
    difference between self.win.refresh() and self.win.erase() and currently I did not meet any bugs using refresh(), If
    anyone know this please inform me, thank you :)
    5.and a never-been-used function: press_to_continue() :( that's actually a get_ch()
    6.of course I make self.win go public so that you can directly call function of curses.Window object as usual

The child classes are StatusWindow, ChatWindow and bla bla bla~The child classes are established for some specified
function in its window area, for example, chat window need chat-logs-sync so it need a threading to engage the thread;
send window need to support chinese characters and commas so it need a thread to perform spell check on every key that
user just pressed down;and ...

so refer to class-level or class-based-function-level documentation if needed

:)

"""
import curses
import threading
from modules.common import *


class CreateWindow:
    """
    Parent class "CreateWindow" to be inherited which will automatically create window object by default
    """

    def __init__(self, xy: tuple, wh: tuple, h_enabled: bool = True, h_text: str = '', h_style=curses.A_NORMAL,
                 refresh_now: bool = True, zh_count: int = 0):

        # 1.create a new window
        self.win = self.__window_create(xy, wh, h_enabled, h_text, h_style, zh_count)
        self.win.move(1, 0)
        if refresh_now:  # refresh window once it was created
            self.refresh()

        # 2.get height and width
        self.height, self.width = self.win.getmaxyx()

        # 3.align format string template:
        self.ft_align_right = '{:>' + str(self.width - 1) + '}'  # align right
        self.ft_align_left = '{:<' + str(self.width - 1) + '}'  # align left
        self.ft_align_center = '{:^' + str(self.width - 1) + '}'  # align center raw

    def align_center(self, text: str):
        """
        pre generate a format string to dynamically both align right/left/center and fit the screen width properly
        :param text: text string you want to fill
        :return:
        """
        if len(text) > self.width - 1:  # reach out the screen, cut header to the screen width
            result = text[:self.width - 1]
        else:  # requirements satisfied, do the align job
            ft_str = '{:^' + str(self.width - 1 - cn_count(text)) + '}'
            result = ft_str.format(text)
        return result

    def align_right(self, text: str):
        """
        same as above
        :param text:
        :return:
        """
        if len(text) > self.width - 1:  # reach out the screen, cut header to the screen width
            result = text[-(self.width - 1):]
        else:  # requirements satisfied, do the align job
            ft_str = '{:>' + str(self.width - 1 - cn_count(text)) + '}'
            result = ft_str.format(text)
        return result

    def align_left(self, text: str):
        """
        same as above
        :param text:
        :return:
        """
        if len(text) > self.width - 1:  # reach out the screen, cut footer to the screen width
            result = text[:self.width - 1]
        else:  # requirements satisfied, do the align job
            ft_str = '{:<' + str(self.width - 1 - cn_count(text)) + '}'
            result = ft_str.format(text)
        return result

    @staticmethod
    def __text_fill(win_obj, xy: tuple, text: str, w_win: int = 0, style=None, zh_count: int = 0):
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
            text = '{}{}'.format(text, ' ' * (w_win - len(text) - zh_count))
        win_obj.addstr(p_y, p_x, text) if style is None else win_obj.addstr(p_y, p_x, text, style)  # custom style

    def __window_create(self, xy: tuple, wh: tuple, h_enabled: bool = True, h_text: str = '', h_style=0, zh_count=0):
        """
        create a curses window object
        :param xy: pos of upper-left corner
        :param wh: width and height
        :param h_enabled: add header to the first row of the window
        :param h_text: header text
        :param h_style: header text's style
        :return: curses window object
        """
        p_show = config.C_SHOW_POSITION_SIZE  # add position and size to header bar
        p_x, p_y = xy
        width, height = wh
        n_win = curses.newwin(height, width, p_y, p_x)  # create window object of curses
        p_size = '({},{}), {} x {}'.format(p_x, p_y, width, height)  # info text of position and area
        h_text = h_text if h_text == '' else '<%s> ' % h_text  # header text
        if h_enabled:  # fill the text with the same width of its window
            self.__text_fill(n_win, (0, 0), '{}{}'.format(h_text, p_size if p_show else ''), width, h_style, zh_count)
        return n_win

    def refresh(self):
        # refresh window data
        self.win.refresh()

    def press_key_continue(self):
        # waiting for confirmation
        self.win.getkey()


class DebugWindow(CreateWindow):

    def __init__(self, xy: tuple, wh: tuple, h_enabled: bool = True, h_text: str = '',
                 h_style=curses.A_REVERSE, refresh_now: bool = True, zh_count: int = 0):
        super().__init__(xy, wh, h_enabled, h_text, h_style, refresh_now, zh_count)  # inherit from parent
        self.last_debug_msgs = []
        self.debug_msgs = []

    def add_debug_message(self, message: str):
        """
        modified message by appending datetime to its head and then save it to debug messages list
        :param message:
        :return:
        """
        self.debug_msgs.append('{} {}'.format(current_datetime('%H:%M:%S'), message))

    def wipe_debug_messages_all(self):
        """
        wipe all previously added debug messages
        :return:
        """
        self.debug_msgs = []
        self.last_debug_msgs = []

    def upd_scr_debug_msgs(self):
        """
        update window's data of the debug messages properly to the window's area
        :return:
        """
        # chat logs changed or pageup/pagedown keys pressed wil do screen update(won't do any if remains the same)
        if self.last_debug_msgs != self.debug_msgs:
            self.win.move(1, 0)  # move cursor to (1,0)
            self.win.clrtoeol()  # clear from (1,0) to end-of-line(EOL)
            for i, line in enumerate(self.debug_msgs[-(self.height - 1):]):
                # ATTENTION:
                # Here we need to strip with [:self.width-1] first and then count the zh characters or commas for this
                # stripped text instead of the raw self.debug_msgs[i][:self.width-1-zh_count]
                text_here = self.debug_msgs[i][:self.width - 1]
                zh_count = cn_count(text_here)
                self.win.addstr(i + 1, 0, text_here[:self.width - 1 - zh_count])
            self.win.move(1, 0)  # move cursor to (1,0)
            self.last_debug_msgs = self.debug_msgs.copy()  # copy to last_chat_logs for compare the next time


class StatusWindow(CreateWindow):

    def __init__(self, xy: tuple, wh: tuple, h_enabled: bool = True, h_text: str = '',
                 h_style=curses.A_REVERSE, refresh_now: bool = True, zh_count: int = 0):
        super().__init__(xy, wh, h_enabled, h_text, h_style, refresh_now, zh_count)  # inherit from parent
        self.flag_upd_datetime = False

    def init_debug_object(self, debug_object: DebugWindow):
        """
        for calling functions of DebugWindow
        after this initialization, use self.debugger.<func()> to call funcs of DebugWindow
        :param debug_object: DebugWindow Object
        :return:
        """
        self.debugger = debug_object

    def upd_scr_datetime(self):
        """
        update screen data in status window
        (currently there is only datetime shown here, more elements will be added soon)
        :return:
        """
        self.win.move(1, 0)  # move cursor to (1,0)
        self.win.clrtoeol()  # clear from (1,0) to end-of-line(EOL)
        self.win.addstr(1, 0, self.datetime)
        self.win.move(1, 0)

    def __upd_datetime(self):
        """
        get current_datetime in default format:'%Y-%m-%d %H:%M:%S'
        :return: formatted datetime string
        """
        self.datetime = current_datetime()

    def __upd_datetime_loop(self):
        """
        update variable `self.datetime` in a loop if flag_upd_datetime is True
        :return:
        """
        while self.flag_upd_datetime:
            self.__upd_datetime()

    def upd_datetime_thread_start(self):
        """
        set flag to True and toggle on a threading on `__upd_datetime_loop()` to keep datetime synced
        :return:
        """
        self.flag_upd_datetime = True
        threading.Thread(target=self.__upd_datetime_loop).start()

    def upd_datetime_thread_stop(self):
        """
        set flag to False to break WhileLoop and therefore quit the thread
        :return:
        """
        self.flag_upd_datetime = False


class ChatWindow(CreateWindow):

    def __init__(self, xy: tuple, wh: tuple, h_enabled: bool = True, h_text: str = '',
                 h_style=curses.A_REVERSE, refresh_now: bool = True, zh_count: int = 0):
        super().__init__(xy, wh, h_enabled, h_text, h_style, refresh_now, zh_count)  # inherit from parent
        self.last_chat_logs = []
        self.logs_loop_sets = []
        self.page_offset = 0  # offset for pageup and pagedown
        self.flag_page_changed = False  # indicated that if key pageup or key pagedown functions properly

    def __timestamp_manager(self, chat_var: list, index: int, interval: int):
        """
        judge every messages sent/recv interval and insert timestamp between them if send/recv interval > std interval
        :param chat_var: index: messages box
        :param index: current message index in chat_var
        :param interval: std interval
        :return: None. Directly insert Timestamp string into messages box if above std interval
        """
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
            self.logs_loop_sets.append([self.align_center(timestamp), curses.color_pair(2)])

    def init_debug_object(self, debug_object: DebugWindow):
        self.debugger = debug_object

    def page_up(self):
        """
        key PageUp function, change offset if requirements satisfied
        :return:
        """
        begin_index = -(self.height - 1) + self.page_offset  # get previous begin_index of messages_box
        if begin_index > -(len(self.logs_loop_sets)):
            self.page_offset -= 1
            self.flag_page_changed = True
            return True
        else:
            return False

    def page_down(self):
        """
        key PageDown function, change offset if requirements satisfied
        :return:
        """
        if self.page_offset < 0:  # means that it has not reached bottom yet, operation page_down granted
            self.page_offset += 1
            self.flag_page_changed = True
            return True
        else:
            return False

    def page_bottom(self):
        """
        go to the bottom of chat window
        :return:
        """
        while self.page_down():
            pass

    def page_top(self):
        """
        go to the top of chat window
        :return:
        """
        while self.page_up():
            pass

    def upd_scr_chat_logs(self, chat_var: list):
        """
        update window data of chat logs.
        (Do the update only if chat logs changed or pageup/pagedown/home/end key is pressed, won't do anything if it
        remains the same)
        :param chat_var: messages_box variable
        :return:
        """
        if self.last_chat_logs != chat_var or self.flag_page_changed:
            # 1.clean window data first
            self.logs_loop_sets = []  # to temporarily save window-height-shown-only message clips
            self.win.move(1, 0)  # move cursor to (1,0)
            self.win.clrtoeol()  # clear from (1,0) to end-of-line(EOL)

            # standard for timestamp
            dt_interval_sec = config.C_DATETIME_REFRESH_INTERVAL
            # define the standard of "message is too long" below
            msg_len_r = config.C_SEND_MESSAGE_MAX_WIDTH if self.width < 3 * config.C_SEND_MESSAGE_MAX_WIDTH else \
                self.width // 3  # default is 30

            # 2.split a single message into several pieces if it's too long
            for i in range(len(chat_var)):
                # do the timestamp adding job
                self.__timestamp_manager(chat_var, i, dt_interval_sec)
                # r-len: role str len
                msg_raw, msg_clips, r_len = chat_var[i]['message'], [], len(chat_var[i]['from'])
                # bug fixed on 2020-2-13 11:28 chinese character message width limit issue
                # since chinese characters or commas occupy 2 ASCII position, so need to detect the number of these
                # characters in text and modified the length of the text

                # 2.1.split into pieces here with dynamic standard:
                while msg_raw:
                    idx = msg_len_r  # dynamic standard:idx
                    clip = msg_raw[:idx]  # try with 'official' standard first, may be all are ASCII characters
                    while len(clip) + cn_count(clip) > msg_len_r:  # actual position occupied more than standard
                        idx -= 1  # need to change standard by decrease value of min_value
                        clip = msg_raw[:idx]  # clip again with new standard
                    msg_clips.append(clip)  # satisfied with new standard, append it
                    msg_raw = msg_raw[idx:]  # dropped the checked part and start a new check for the rest of msg_raw

                # 2.2.do the text-align job
                for j in range(len(msg_clips)):
                    # delta between standard len and current len
                    m_len = msg_len_r - len(msg_clips[j]) - cn_count(msg_clips[j])  # calc the count of blank space
                    if chat_var[i]['role'] == config.C_SELF_ID:  # align right for self
                        msg = msg_clips[j] + ('%s' % (' ' * (1 + r_len + m_len)) if j else '<%s' % chat_var[i]['from'])
                        self.logs_loop_sets.append([self.align_right(msg), 0])  # update
                    else:  # align left for friend
                        msg = ('%s' % (' ' * (1 + r_len + m_len)) if j else '%s>' % chat_var[i]['from']) + msg_clips[j]
                        self.logs_loop_sets.append([self.align_left(msg), 0])  # update

            # 3.draw it
            bgn_i = -(self.height - 1) + self.page_offset  # begin_index
            dest_i = len(self.logs_loop_sets) + self.page_offset  # dest_index
            for i, a in enumerate(self.logs_loop_sets[bgn_i:dest_i]):
                self.win.addstr(i + 1, 0, a[0], a[1])  # add to Chat-Screen data
            self.win.move(1, 0)  # move cursor to (1,0)
            self.last_chat_logs = chat_var.copy()  # copy to last_chat_logs for compare the next time
            self.flag_page_changed = False  # resume page-changed status to False


class SendWindow(CreateWindow):
    # [send] button need to be added
    def __init__(self, xy: tuple, wh: tuple, h_enabled: bool = True, h_text: str = '',
                 h_style=curses.A_REVERSE, refresh_now: bool = True, zh_count: int = 0):
        super().__init__(xy, wh, h_enabled, h_text, h_style, refresh_now, zh_count)  # inherit from parent
        self.message = ''
        self.role_name = config.C_SEND_ROLE_NAME
        self.unknown_characters = []

    def init_debug_object(self, debug_object: DebugWindow):
        """
        same as ChatWindow's
        :param debug_object:
        :return:
        """
        self.debugger = debug_object

    def set_role_name(self, role_name: str):
        """
        change the role name indicated for us
        (never been used before)
        :param role_name: the name string
        :return:
        """
        self.role_name = role_name

    def upd_scr_message(self, with_indicator: bool = True):
        """
        update window data for real-time decoded to-send message content. If with_indicator is True, a '_' will be added
        to stimulate a cursor indicating your typing
        :param with_indicator: show a '_' right on where you are tying at
        :return:
        """
        self.win.move(1, 0)  # move cursor to (1,0): the begin of the window's second row
        self.win.clrtobot()  # clear from (1,0) to end-of-window)
        self.win.addstr(1, 0, self.message + '_' if with_indicator else '')
        self.win.move(1, 0)

    def input(self, ch_code: int):
        """
        ASCII input job and [backspace] pressed solution
        :param ch_code: the ASCII code just got
        :return:
        """
        if ch_code == curses.KEY_BACKSPACE:
            if len(self.message):  # delete last character when length is more than 1
                self.message = self.message[:-1]
        else:  # add ASCII character to EOL
            self.message += chr(ch_code)

    def overwrite_message(self, msg_text: str):
        """
        overwrite variable `self.message`
        :param msg_text:
        :return:
        """
        self.message = msg_text

    def append_message(self, append_text: str):
        """
        appending string to the end of self.messages which was created to served with the chinese characters or commas
        real-time decoding at the beginning.
        :param append_text: text string
        :return:
        """
        self.message += append_text

    def publish_send_status(self, chat_var: list, send_succeed: bool, debug: bool = True):
        """
        you know the sending function did not exist in SendWindow, it just performs a visualization of sending.
        so the send_succeed is sent_result that returned by the real-man who sent the message(comm module), and now
        we need to judge the status and tell our users. If failed we can send a debug info to debugger(optional) and
        add [!] to the end of the message and then display them on chat window.
        :param debug: enable debugger module to receive error output
        :param chat_var: message box variable
        :param send_succeed: sent status, True for succeed and False for failed
        :return:
        """
        if len(self.message):
            apx = config.C_SEND_SUCCEED_SUFFIX if send_succeed else config.C_SEND_FAILED_SUFFIX
            if not send_succeed and debug:
                self.debugger.add_debug_message('failed:{}'.format(self.message))
            chat_var.append({'time': current_datetime(), 'message': self.message + apx, 'from': self.role_name,
                             'role': config.C_SELF_ID})
            self.message = ''


class HelpWindow(CreateWindow):
    # help text shown below debug window
    def __init__(self, xy: tuple, wh: tuple, h_enabled: bool = True, h_text: str = '',
                 h_style=curses.A_REVERSE, refresh_now: bool = True, zh_count: int = 0):
        super().__init__(xy, wh, h_enabled, h_text, h_style, refresh_now, zh_count)  # inherit from parent
        self.help_messages = []

    def add_help_message(self, message: str):
        """
        add a single help message to current list, maximum is height-1 records in total
        :param message: msg itself
        :return:
        """
        if len(self.help_messages) < self.height - 1:
            self.help_messages.append(message)

    def set_help_messages(self, messages_list: list):
        """
        multiple-mode adding help messages. Maximum height-1 records in total
        :param messages_list: a list-set of messages you want to show
        :return:
        """
        self.help_messages = messages_list[:self.height - 1]

    def wipe_debug_messages_all(self):
        """
        wipe previously added debug info
        :return:
        """
        self.help_messages = []

    def upd_scr_help_message(self):
        self.win.move(1, 0)  # move cursor to (1,0)
        self.win.clrtoeol()  # clear from (1,0) to end-of-line(EOL)
        for j, line in enumerate(self.help_messages):  # show all help_messages(has been cut to length=height-1 so all)
            # ZH_CN SUPPORT
            text_here = self.help_messages[j][:self.width - 1]
            zh_count = cn_count(text_here)
            self.win.addstr(j + 1, 0, text_here[:self.width - 1 - zh_count])
            # OLD ASCII ONLY SCRIPT:
            # self.win.addstr(j + 1, 0, self.help_messages[j][:self.width - 1])  # max width limit
        self.win.move(1, 0)  # move cursor to (1,0)
