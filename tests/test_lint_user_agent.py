import io
import json
import unittest
from unittest import mock

from scripts import lint_domain_lists as lint


def feed(payload: object) -> mock.MagicMock:
    response = mock.MagicMock()
    response.__enter__.return_value = io.BytesIO(json.dumps(payload).encode())
    return response


class CurrentUserAgentTests(unittest.TestCase):
    def test_uses_mozillas_latest_release(self) -> None:
        with mock.patch.object(lint.urllib.request, "urlopen", return_value=feed({"LATEST_FIREFOX_VERSION": "171.0.2"})):
            agent = lint.current_user_agent()
        self.assertEqual(agent, "Mozilla/5.0 (X11; Linux x86_64; rv:171.0) Gecko/20100101 Firefox/171.0")

    def test_network_failure_keeps_the_built_in_agent(self) -> None:
        with mock.patch.object(lint.urllib.request, "urlopen", side_effect=OSError("offline")):
            self.assertEqual(lint.current_user_agent(), lint.USER_AGENT)

    def test_unexpected_feed_keeps_the_built_in_agent(self) -> None:
        for payload in ({}, {"LATEST_FIREFOX_VERSION": ""}, {"LATEST_FIREFOX_VERSION": "abc"}, ["160.0"]):
            with self.subTest(payload=payload), mock.patch.object(lint.urllib.request, "urlopen", return_value=feed(payload)):
                self.assertEqual(lint.current_user_agent(), lint.USER_AGENT)

    def test_bad_json_keeps_the_built_in_agent(self) -> None:
        response = mock.MagicMock()
        response.__enter__.return_value = io.BytesIO(b"<html>")
        with mock.patch.object(lint.urllib.request, "urlopen", return_value=response):
            self.assertEqual(lint.current_user_agent(), lint.USER_AGENT)


if __name__ == "__main__":
    unittest.main()
