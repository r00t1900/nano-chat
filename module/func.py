# _*_coding:utf-8 _*_
# @Time    : 2020/2/6 11:42
# @Author  : Shek 
# @FileName: func.py
# @Software: PyCharm
import nnpy
import time
import config
from module import logger
from module.pair import PairObject
from module.windows import *
from curses import wrapper
import curses

chat_logs, debug_logs = [], []


def current_datetime(format_str: str = '%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.now().strftime(format_str)


# abandon
def sub_cmd_bind_old(arguments):
    # 1 initialize a logger
    log = logger.Logger(config.ROLE_NAME_PAIR + 'SERVER')
    # 2 create a object
    pair_server = nnpy.Socket(nnpy.AF_SP, nnpy.PAIR)
    # set send and recv timeout to 1s
    pair_server.setsockopt(nnpy.SOL_SOCKET, nnpy.SNDTIMEO, 1000)
    pair_server.setsockopt(nnpy.SOL_SOCKET, nnpy.RCVTIMEO, 1000)

    # 3 establish a sever to push message
    log.info('binding to {}://{} ...'.format(arguments.protocol, arguments.addr))
    result = pair_server.bind('{}://{}'.format(arguments.protocol, arguments.addr))
    # bind status
    log.info('success') if result else log.info('failed') and exit(0)

    # 4 push loop
    time.sleep(0.5)
    while True:

        content = input('Send({})>'.format(config.COUNT_SEND_SUCCESS))
        # process input message/command
        if content == config.FLAG_SERVER_EXIT:
            # exit command caught, break loop
            log.info(config.L_SERVER_EXIT)
            break
        else:
            try:  # success
                # send message/data/command
                send_result = pair_server.send(bytes(content, encoding=config.DATA_ENCODING))
                print(send_result)
                config.COUNT_SEND_SUCCESS += 1
            except nnpy.errors.NNError as e:  # failed
                config.COUNT_SEND_FAILED += 1
                log.warning('{}:{}'.format(e, content))

    # 5 close server
    pair_server.close()
    log.info(config.L_SERVER_CLOSED)


# abandon
def sub_cmd_connect_old(arguments):
    # 1 initialize a logger
    log = logger.Logger(config.ROLE_NAME_PAIR + 'CLIENT')
    # 2 create a object
    pair_client = nnpy.Socket(nnpy.AF_SP, nnpy.PAIR)
    # set send and recv timeout to 1s
    pair_client.setsockopt(nnpy.SOL_SOCKET, nnpy.SNDTIMEO, 1000)
    # pair_client.setsockopt(nnpy.SOL_SOCKET, nnpy.RCVTIMEO, 1000)
    # keep-alive: not completed yet
    if arguments.keep_alive:
        log.info(config.I_KEEP_ALIVE_ENABLED)
    # 3 connect to a server for receiving message
    log.info('connecting to {}://{}'.format(arguments.protocol, arguments.addr))
    result = pair_client.connect('{}://{}'.format(arguments.protocol, arguments.addr))
    # connect status
    log.info(config.I_OP_SUCCESS) if result else log.info(config.I_OP_FAILED) and exit(0)

    # 4 receive in loop
    time.sleep(0.5)
    while True:
        try:
            recv_data = pair_client.recv()
            if recv_data:
                decoded_data = recv_data.decode(config.DATA_ENCODING)
                # 3 process received data
                # remove the subscribe prefix
                decoded_data = decoded_data[len(arguments.subscribe):]
                # receive a go-offline flag from server, break loop
                if decoded_data == config.FLAG_CLIENT_OFFLINE:
                    log.info(config.L_CLIENT_FLAG_OFFLINE_DETECTED)
                    break
                # display message push by server
                print('{}|{}'.format(current_datetime(), decoded_data))
                # logging to text file
                log.debug(decoded_data)
        except KeyboardInterrupt:
            # ctrl + c detected
            log.info(config.L_CLIENT_CTRL_C)
            break

    # 5 close client
    pair_client.close()
    log.info(config.L_CLIENT_CLOSED)


def main(std_scr, pair_obj: PairObject):
    pre_conf_status, elements = preconfigure(scr_obj=std_scr)  # get 4 win object and max terminal size
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
                    send_result, send_inf = pair_obj.send(text=w_send.message)
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
    pair_obj.stop_recv_loop()


def sub_cmd_bind(arguments):
    pair = PairObject()
    pair_conf_status, err_inf = pair.configure(arguments.protocol, arguments.addr, is_server=True)
    if pair_conf_status:
        pair.enable_recv_loop()
        pair.start_recv_loop(chat_var=chat_logs)
        wrapper(main, pair)
    else:
        print('init failed because:\n'.format(err_inf))


def sub_cmd_connect(arguments):
    pair = PairObject()
    pair_conf_status, err_inf = pair.configure(arguments.protocol, arguments.addr, is_server=False)  # is_server:0
    if pair_conf_status:
        pair.enable_recv_loop()
        pair.start_recv_loop(chat_var=chat_logs)
        wrapper(main, pair)
    else:
        print('init failed because:\n'.format(err_inf))
