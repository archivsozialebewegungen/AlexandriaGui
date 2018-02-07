'''
Created on 03.05.2015

@author: michael
'''
import unittest
from alexpresenters.MessageBroker import MessageBroker, Message, ERROR_MESSAGE

class MessageTest(unittest.TestCase):
    
    def test_equals_1(self):
        
        self.assertEqual(Message("MY_KEY", option='bla'),
                         Message('MY_KEY', option='blub'))

    def test_equals_2(self):
        
        self.assertEqual("MY_KEY",
                         Message('MY_KEY', option='blub'))
        
    def test_stringify(self):
        self.assertEqual("MY_KEY",
                         "%s" % Message('MY_KEY', option='blub'))

class MessageBrokerTest(unittest.TestCase):


    def testMessageBroker(self):
        broker = MessageBroker()
        class TestClass:
            
            def receive_message(self, message):
                self.key = message.key
                self.param1 = message.param1
                self.param2 = message.param2
                
        test_class = TestClass()
        broker.subscribe(test_class)
        broker.send_message(Message("KEY", param1="P1", param2="P2"))
        
        self.assertEqual("KEY", test_class.key)
        self.assertEqual("P1", test_class.param1)
        self.assertEqual("P2", test_class.param2)

    def testMessageInMessage(self):
        broker = MessageBroker()
        class TestClass:
            
            def __init__(self, message_broker):
                self.message_broker = message_broker
                self.received_key2 = False
            
            def receive_message(self, message):
                if message == 'KEY1':
                    self.message_broker.send_message(Message('KEY2'))
                if message == 'KEY2':
                    self.received_key2 = True
                
        test_class = TestClass(broker)
        broker.subscribe(test_class)
        broker.send_message(Message("KEY1"))
        
        self.assertTrue(test_class.received_key2)

class DisplayMessageTest(unittest.TestCase):


    def setUp(self):
        
        self.broker = MessageBroker()
        class TestClass:
            
            def __init__(self):
                self.message_type = None
                self.message_text = None
            
            def receive_message(self, message):
                if message.key == ERROR_MESSAGE:
                    self.message_type = message.messagetype
                    self.message_text = message.message
                
        self.test_class = TestClass()
        self.broker.subscribe(self.test_class)

    def test_show_error(self):
        
        self.broker.show_error("error text")
        self.assertEqual("error", self.test_class.message_type)
        self.assertEqual("error text", self.test_class.message_text)

    def test_show_info(self):
        
        self.broker.show_info("info text")
        self.assertEqual("info", self.test_class.message_type)
        self.assertEqual("info text", self.test_class.message_text)

    def test_show_warning(self):
        
        self.broker.show_warning("warning text")
        self.assertEqual("warning", self.test_class.message_type)
        self.assertEqual("warning text", self.test_class.message_text)

    def test_show_debug(self):
        
        self.broker.show_debug("debug text")
        self.assertEqual("debug", self.test_class.message_type)
        self.assertEqual("debug text", self.test_class.message_text)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()