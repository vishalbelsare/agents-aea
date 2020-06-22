# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2019 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This module contains tests for decision_maker."""

import pytest

from aea.decision_maker.scaffold import DecisionMakerHandler


def test_init_and_not_implemented():
    """Initialise the decision maker handler."""
    decision_maker_handler = DecisionMakerHandler(identity="identity", wallet="wallet")
    with pytest.raises(NotImplementedError):
        decision_maker_handler.handle("message")
