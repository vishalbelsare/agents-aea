# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2020 Fetch.AI Limited
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

"""This module contains the tests of the soef connection module."""

import logging
import time
from threading import Thread

import pytest

from aea.configurations.base import ConnectionConfig, PublicId
from aea.crypto.fetchai import FetchAICrypto
from aea.helpers.search.models import (
    Constraint,
    ConstraintType,
    Description,
    Location,
    Query,
)
from aea.identity.base import Identity
from aea.mail.base import Envelope
from aea.multiplexer import Multiplexer

from packages.fetchai.connections.soef.connection import SOEFConnection
from packages.fetchai.protocols.oef_search.message import OefSearchMessage

from tests.common.utils import wait_for_condition

from . import models

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


@pytest.mark.integration
def test_soef():
    """Perform tests over real network."""
    # First run OEF in a separate terminal: python scripts/oef/launch.py -c ./scripts/oef/launch_config.json
    crypto = FetchAICrypto()
    identity = Identity("", address=crypto.address)

    # create the connection and multiplexer objects
    configuration = ConnectionConfig(
        api_key="TwiCIriSl0mLahw17pyqoA",
        soef_addr="soef.fetch.ai",
        soef_port=9002,
        restricted_to_protocols={PublicId.from_str("fetchai/oef_search:0.3.0")},
        connection_id=SOEFConnection.connection_id,
    )
    soef_connection = SOEFConnection(configuration=configuration, identity=identity,)
    multiplexer = Multiplexer([soef_connection])

    try:
        # Set the multiplexer running in a different thread
        t = Thread(target=multiplexer.connect)
        t.start()

        wait_for_condition(lambda: multiplexer.is_connected, timeout=5)

        # register an agent with location
        agent_location = Location(52.2057092, 2.1183431)
        service_instance = {"location": agent_location}
        service_description = Description(
            service_instance, data_model=models.AGENT_LOCATION_MODEL
        )
        message = OefSearchMessage(
            performative=OefSearchMessage.Performative.REGISTER_SERVICE,
            service_description=service_description,
        )
        envelope = Envelope(
            to="soef",
            sender=crypto.address,
            protocol_id=message.protocol_id,
            message=message,
        )
        logger.info(
            "Registering agent at location=({},{}) by agent={}".format(
                agent_location.latitude, agent_location.longitude, crypto.address,
            )
        )
        multiplexer.put(envelope)

        # register personality pieces
        service_instance = {"piece": "genus", "value": "service"}
        service_description = Description(
            service_instance, data_model=models.AGENT_PERSONALITY_MODEL
        )
        message = OefSearchMessage(
            performative=OefSearchMessage.Performative.REGISTER_SERVICE,
            service_description=service_description,
        )
        envelope = Envelope(
            to="soef",
            sender=crypto.address,
            protocol_id=message.protocol_id,
            message=message,
        )
        logger.info("Registering agent personality")
        multiplexer.put(envelope)

        # register service key
        service_instance = {"key": "test", "value": "test"}
        service_description = Description(
            service_instance, data_model=models.SET_SERVICE_KEY_MODEL
        )
        message = OefSearchMessage(
            performative=OefSearchMessage.Performative.REGISTER_SERVICE,
            service_description=service_description,
        )
        envelope = Envelope(
            to="soef",
            sender=crypto.address,
            protocol_id=message.protocol_id,
            message=message,
        )
        logger.info("Registering agent service key")
        multiplexer.put(envelope)

        # find agents near me
        radius = 0.1
        close_to_my_service = Constraint(
            "location", ConstraintType("distance", (agent_location, radius))
        )
        closeness_query = Query(
            [close_to_my_service], model=models.AGENT_LOCATION_MODEL
        )
        message = OefSearchMessage(
            performative=OefSearchMessage.Performative.SEARCH_SERVICES,
            query=closeness_query,
        )
        envelope = Envelope(
            to="soef",
            sender=crypto.address,
            protocol_id=message.protocol_id,
            message=message,
        )
        logger.info(
            "Searching for agents in radius={} of myself at location=({},{})".format(
                radius, agent_location.latitude, agent_location.longitude,
            )
        )
        multiplexer.put(envelope)
        wait_for_condition(lambda: not multiplexer.in_queue.empty(), timeout=20)

        # check for search results
        envelope = multiplexer.get()
        message = envelope.message
        assert len(message.agents) >= 0

        # find agents near me with filter
        radius = 0.1
        close_to_my_service = Constraint(
            "location", ConstraintType("distance", (agent_location, radius))
        )
        personality_filters = [
            Constraint("genus", ConstraintType("==", "vehicle")),
            Constraint(
                "classification", ConstraintType("==", "mobility.railway.train")
            ),
        ]

        service_key_filters = [
            Constraint("test", ConstraintType("==", "test")),
        ]

        closeness_query = Query(
            [close_to_my_service] + personality_filters + service_key_filters
        )

        message = OefSearchMessage(
            performative=OefSearchMessage.Performative.SEARCH_SERVICES,
            query=closeness_query,
        )
        envelope = Envelope(
            to="soef",
            sender=crypto.address,
            protocol_id=message.protocol_id,
            message=message,
        )
        logger.info(
            "Searching for agents in radius={} of myself at location=({},{}) with personality filters".format(
                radius, agent_location.latitude, agent_location.longitude,
            )
        )
        time.sleep(3)  # cause requests rate limit on server :(
        multiplexer.put(envelope)
        wait_for_condition(lambda: not multiplexer.in_queue.empty(), timeout=20)

        envelope = multiplexer.get()
        message = envelope.message
        assert len(message.agents) >= 0

        # test ping command
        service_description = Description({}, data_model=models.PING_MODEL)
        message = OefSearchMessage(
            performative=OefSearchMessage.Performative.REGISTER_SERVICE,
            service_description=service_description,
        )
        envelope = Envelope(
            to="soef",
            sender=crypto.address,
            protocol_id=message.protocol_id,
            message=message,
        )
        logger.info("Registering agent service key")
        multiplexer.put(envelope)
        time.sleep(3)
        assert multiplexer.in_queue.empty()

    finally:
        # Shut down the multiplexer
        multiplexer.disconnect()
        t.join()
