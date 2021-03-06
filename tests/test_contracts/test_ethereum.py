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

"""This module contains tests for aea.contracts.base."""

import json
from pathlib import Path
from typing import cast

import pytest

import web3

from aea.configurations.base import (
    ComponentConfiguration,
    ComponentType,
    ContractConfig,
)
from aea.contracts import contract_registry
from aea.contracts.base import Contract
from aea.crypto.registries import ledger_apis_registry

from tests.conftest import ROOT_DIR


@pytest.fixture()
def dummy_contract(request):
    directory = Path(ROOT_DIR, "tests", "data", "dummy_contract")
    configuration = ComponentConfiguration.load(ComponentType.CONTRACT, directory)
    configuration._directory = directory
    configuration = cast(ContractConfig, configuration)

    if str(configuration.public_id) in contract_registry.specs:
        contract_registry.specs.pop(str(configuration.public_id))

    # load into sys modules
    Contract.from_config(configuration)

    # load into registry
    path = Path(configuration.directory, configuration.path_to_contract_interface)
    with open(path, "r") as interface_file:
        contract_interface = json.load(interface_file)

    contract_registry.register(
        id_=str(configuration.public_id),
        entry_point=f"{configuration.prefix_import_path}.contract:{configuration.class_name}",
        class_kwargs={"contract_interface": contract_interface},
        contract_config=configuration,
    )
    contract = contract_registry.make(str(configuration.public_id))
    yield contract
    contract_registry.specs.pop(str(configuration.public_id))


def test_get_instance_no_address(dummy_contract):
    """Tests the from config method and contract registry registration."""
    ledger_api = ledger_apis_registry.make(
        "ethereum",
        address="https://ropsten.infura.io/v3/f00f7b3ba0e848ddbdc8941c527447fe",
    )
    instance = dummy_contract.get_instance(ledger_api)
    assert type(instance) == web3._utils.datatypes.PropertyCheckingFactory
