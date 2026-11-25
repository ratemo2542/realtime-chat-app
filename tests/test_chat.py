import unittest

import app as chat


def event_payload(event):
    """Normalize Flask-SocketIO test-client payloads across supported versions."""
    payload = event["args"]
    return payload[0] if isinstance(payload, list) else payload


class ChatTests(unittest.TestCase):
    def setUp(self):
        self.sender = chat.socketio.test_client(chat.app)
        self.receiver = chat.socketio.test_client(chat.app)

    def tearDown(self):
        self.sender.disconnect()
        self.receiver.disconnect()

    def join(self, client, name, room="general"):
        client.emit("join", {"name": name, "room": room})
        client.get_received()

    def test_message_is_broadcast_to_room_members(self):
        self.join(self.sender, "Ada")
        self.join(self.receiver, "Grace")

        self.sender.emit("message", {"text": "Hello"})
        sender_events = self.sender.get_received()
        receiver_events = self.receiver.get_received()

        sender_messages = [event for event in sender_events if event["name"] == "message"]
        receiver_messages = [event for event in receiver_events if event["name"] == "message"]

        self.assertEqual(len(sender_messages), 1)
        self.assertEqual(len(receiver_messages), 1)
        self.assertEqual(event_payload(sender_messages[0])["text"], "Hello")
        self.assertEqual(event_payload(sender_messages[0])["name"], "Ada")
        self.assertEqual(event_payload(receiver_messages[0])["text"], "Hello")
        self.assertEqual(event_payload(receiver_messages[0])["name"], "Ada")

    def test_rejects_invalid_room_name(self):
        self.sender.emit("join", {"name": "Ada", "room": "../admin"})
        events = self.sender.get_received()
        self.assertTrue(any(event["name"] == "error_message" for event in events))

    def test_message_is_ignored_until_client_joins_a_room(self):
        self.sender.emit("message", {"text": "Not in a room"})
        events = self.sender.get_received()
        self.assertFalse(any(event["name"] == "message" for event in events))

    def test_join_rejects_non_object_payload(self):
        self.sender.emit("join", "general")
        events = self.sender.get_received()
        self.assertTrue(any(event["name"] == "error_message" for event in events))

    def test_join_rejects_non_text_name(self):
        self.sender.emit("join", {"name": 123, "room": "general"})
        events = self.sender.get_received()
        self.assertTrue(any(event["name"] == "error_message" for event in events))

    def test_oversized_message_is_rejected(self):
        self.join(self.sender, "Ada")
        self.sender.emit("message", {"text": "x" * 501})
        events = self.sender.get_received()
        self.assertFalse(any(event["name"] == "message" for event in events))
        self.assertTrue(any(event["name"] == "error_message" for event in events))

    def test_home_page_loads(self):
        response = chat.app.test_client().get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Room Chat", response.data)


if __name__ == "__main__":
    unittest.main()
