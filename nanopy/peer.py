import socket

address = "peering.nano.org"
port = 7075

enum_network = {}
for i, network_id in enumerate(
    ["network_test", "network_beta", "network_live"], start=ord("A")
):
    enum_network[network_id] = i.to_bytes(1, byteorder="big")

enum_msgtype = {}
for i, msgtype in enumerate(
    [
        "invalid",
        "not_a_type",
        "keepalive",
        "publish",
        "confirm_req",
        "confirm_ack",
        "bulk_pull",
        "bulk_push",
        "frontier_req",
        "bulk_pull_blocks",
        "node_id_handshake",
        "bulk_pull_account",
    ]
):
    enum_msgtype[msgtype] = i.to_bytes(1, byteorder="big")

enum_blocktype = {}
for i, blocktype in enumerate(
    ["invalid", "not_a_block", "send", "receive", "open", "change", "state"]
):
    enum_blocktype[blocktype] = i.to_bytes(1, byteorder="big")

magic = b"R"
network_id = enum_network["network_live"]
version_max = (16).to_bytes(1, byteorder="big")
version_using = (16).to_bytes(1, byteorder="big")
version_min = (13).to_bytes(1, byteorder="big")
message_type = enum_msgtype["keepalive"]
extensions = (0x0000).to_bytes(2, byteorder="big")
# ~ extensions = (0xffff & 0x0001).to_bytes(2, byteorder='big')
# ~ extensions = (0xffff & 0x0002).to_bytes(2, byteorder='big')
# ~ extensions = ((0xffff & 0x0f00)>>8).to_bytes(2, byteorder='big')
# ~ print(account_key('nano_3ooycog5ejbce9x7nmm5aueui18d1kpnd74gc4s67nid114c5bp4g9nowusy'))
# ~ start = bytes.fromhex(
# ~ 'd6be555c36452a61fa5a4e6346d9b800cb04ad45944e50b242d20b0004a1a6c2')
# ~ age = bytes.fromhex('ffffffff')
# ~ count = bytes.fromhex('ffffffff')
# ~ body = start + age + count
peer = bytes.fromhex("000000000000000000000000000000000000")
body = peer
for i in range(7):
    body += peer

sock = socket.socket(
    socket.AF_INET, socket.SOCK_DGRAM
)  # SOCK_DGRAM - UDP # SOCK_STREAM - TCP
# ~ sock.bind(('', 7075))
# ~ sock.connect((address, port))
msg = (
    magic
    + enum_network["network_live"]
    + version_max
    + version_using
    + version_min
    + message_type
    + extensions
    + body
)
# ~ sock.send(msg)
sock.sendto(msg, (address, port))
print(msg.hex())
response = sock.recv(1024)
print(response.hex())
