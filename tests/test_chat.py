import unittest
import app as chat

class ChatTests(unittest.TestCase):
    def setUp(self):
        self.client = chat.socketio.test_client(chat.app)

    def tearDown(self):
        self.client.disconnect()

    def test_join_and_message_broadcast(self):
        self.client.emit("join", {"name": "Ada", "room": "general"})
        self.client.get_received()
        self.client.emit("message", {"text": "Hello"})
        events = self.client.get_received()
        messages = [event for event in events if event["name"] == "message"]
        self.assertEqual(messages[0]["args"][0]["text"], "Hello")
        self.assertEqual(messages[0]["args"][0]["name"], "Ada")

    def test_rejects_invalid_room_name(self):
        self.client.emit("join", {"name": "Ada", "room": "../admin"})
        events = self.client.get_received()
        self.assertTrue(any(event["name"] == "error_message" for event in events))

if __name__ == "__main__":
    unittest.main()
