from twisted.internet import defer
from twisted.test import proto_helpers
from twisted.trial import unittest

import msgpack
from txmsgpack.protocol import MSGTYPE_REQUEST
from txmsgpack.protocol import MSGTYPE_RESPONSE
from txmsgpack.protocol import MSGTYPE_NOTIFICATION
from txmsgpack.server   import MsgpackRPCServer


class TestServer(MsgpackRPCServer):
    def __init__(self):
        self.storage = {}

    def remote_insert_key(self, value, msgid=None):
        value["new_key"]=1
        return self.remote_echo(value, msgid)

    def remote_echo(self, value, msgid=None):
        return value

    def remote_notify(self, value):
        return

    def remote_sum(self, args):
        lhs, rhs = args
        df = defer.Deferred()
        df.callback(lhs + rhs)
        return df

    def remote_store(self, key, value):
        self.storage[key] = value

    def remote_load(self, key):
        return self.storage[key]


class MsgpackRPCServerTestCase(unittest.TestCase):

    request_index=0

    def setUp(self):
        self.server = TestServer()
        factory = self.server._buildFactory()

        self.proto = factory.buildProtocol(("127.0.0.1", 0))
        self.transport = proto_helpers.StringTransport()
        self.proto.makeConnection(self.transport)
        self.packer = msgpack.Packer(encoding="utf-8")

    def test_request_string(self):
        arg = "SIMON SAYS"
        return self._test_request(method="echo", param=arg, expected_result=arg, expected_error=None)

    def test_request_dict(self):
        arg = {"A":1234}
        ret = {"A":1234, "new_key":1}
        return self._test_request(method="insert_key", param=arg, expected_result=ret, expected_error=None)

    def test_notify(self):
        arg = "NOTIFICATION"
        return self._test_notification(method="notify", value=arg)

    def test_sum(self):
        args = (2,5)
        ret  = 7
        return self._test_request(method="sum", param=args, expected_result=ret, expected_error=None)

    def test_store_load(self):
        key = 'foo'
        value = 'bar'
        args = (key, value)

        self._test_request(method="store", params=args)

        self.assertEqual(self.server.storage, {key: value})

        self.transport.clear()
        self._test_request(method="load", param=key, expected_result=value)

    def _test_notification(self, method="notify", value=""):
        message = (MSGTYPE_NOTIFICATION, method, (value,))
        packed_message = self.packer.pack(message)
        self.proto.dataReceived(packed_message)
        return_value = self.transport.value()
        self.assertEqual(return_value, "")

    def _test_request(self, method, param=None, params=None, expected_result=None, expected_error=None):
        index = MsgpackRPCServerTestCase.request_index
        MsgpackRPCServerTestCase.request_index += 1

        if params is not None:
            args = params
        else:
            args = (param,)

        message         = (MSGTYPE_REQUEST, index, method, args)
        packed_message  = self.packer.pack(message)

        response        = (MSGTYPE_RESPONSE, index, expected_error, expected_result)
        packed_response = self.packer.pack(response)

        self.proto.dataReceived(packed_message)
        return_value = self.transport.value()

        self.assertEqual(return_value, packed_response)

        unpacked_response = msgpack.loads(return_value)
        (msgType, msgid, methodName, args) = unpacked_response

        self.assertEqual(msgType, MSGTYPE_RESPONSE)
        self.assertEqual(msgid, index)
        self.assertEqual(methodName, None)
        self.assertEqual(args, expected_result)
