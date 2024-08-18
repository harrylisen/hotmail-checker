# # -*-coding: utf-8 -*-
# from socks import create_connection, PROXY_TYPE_SOCKS4, PROXY_TYPE_SOCKS5, PROXY_TYPE_HTTP
# from imaplib import IMAP4_SSL
# import socket
#
#
# # 收邮件用这个
# # 为什么取名SocksIMAP4SSL 而 不叫 ProxyIMAP4SSL? 因为socks库的本质是对socket库的扩展，增加了通过Proxy进行网络通信的支持。 （python自带的socket库不支持proxy）
# class SocksIMAP4SSL(IMAP4_SSL):
#
#     #  __init__ 除了新增三个参数外，其他没有任何改变<------ 执行一次 IMAP4_SSL.__init__ () 把 IMAP4_SSL.__init__ () 的全部继承过来
#     def __init__(self, host='', port=IMAP4_SSL_PORT, keyfile=None,
#                  certfile=None, ssl_context=None, proxy_addr=None,
#                  proxy_port=None, rdns=True):
#         self.proxy_addr = proxy_addr
#         self.proxy_port = proxy_port
#         self.rdns = rdns
#
#         IMAP4_SSL.__init__(self, host=host, port=port, keyfile=keyfile, certfile=certfile, ssl_context=ssl_context)
#
#     # 用 socks.create_connection 替换 socket.create_connection。 一个是socket，一个是socks，一个字母的差别！
#     def _create_socket(self):
#         sock = create_connection((self.host, self.port), proxy_type=PROXY_TYPE_HTTP, proxy_addr=self.proxy_addr,
#                                  proxy_port=self.proxy_port)
#         return self.ssl_context.wrap_socket(sock, server_hostname=self.host)
#
