# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from google.protobuf import json_format

class TestProtobufApi(unittest.TestCase):

    def test_parse(self):
        # JSON to protobuf
        message = json_format.Parse(json_string, YourMessageClass())

        # Protobuf to JSON
        json_string = json_format.MessageToJson(message)
