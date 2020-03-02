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

"""This module contains the scaffold contract definition."""
import logging
import random
from typing import Any, Dict, List

from vyper.utils import keccak256

from aea.configurations.base import ContractConfig, ContractId
from aea.contracts.ethereum import Contract
from aea.crypto.base import LedgerApi
from aea.decision_maker.messages.transaction import TransactionMessage
from aea.mail.base import Address

NFT = 1
FT = 2

logger = logging.getLogger(__name__)


class ERC1155Contract(Contract):
    """The ERC1155 contract class."""

    def __init__(
        self,
        contract_id: ContractId,
        contract_config: ContractConfig,
        contract_interface: Dict[str, Any],
    ):
        """Initialize.

        super().__init__(contract_id, contract_config)


        :param contract_id: the contract id.
        :param config: the contract configurations.
        :param contract_interface: the contract interface.
        """
        super().__init__(contract_id, contract_config, contract_interface)
        self.is_items_created = False
        self.is_items_minted = False
        self.is_trade = False
        self.token_ids = []  # type: List[int]
        self.item_ids = []  # type: List[int]

    def create_item_ids(self, token_type: int, token_ids: List[int]) -> None:
        """Populate the item_ids list."""
        assert self.token_ids is [], "Item ids already created."
        self.token_ids = token_ids
        for token_id in token_ids:
            self.item_ids.append(Helpers().generate_id(token_type, token_id))

    def get_deploy_transaction(
        self, deployer_address: Address, ledger_api: LedgerApi
    ) -> TransactionMessage:
        """
        Deploy a smart contract.

        :params deployer_address: The address that deploys the smart-contract
        """
        assert not self.is_deployed, "The contract is already deployed!"
        tx = self._create_deploy_transaction(
            deployer_address=deployer_address, ledger_api=ledger_api
        )

        #  Create the transaction message for the Decision maker
        tx_message = TransactionMessage(
            performative=TransactionMessage.Performative.PROPOSE_FOR_SIGNING,
            skill_callback_ids=[ContractId("fetchai", "erc1155_skill", "0.1.0")],
            tx_id="contract_deploy",
            tx_sender_addr=deployer_address,
            tx_counterparty_addr="",
            tx_amount_by_currency_id={"ETH": 0},
            tx_sender_fee=0,
            tx_counterparty_fee=0,
            tx_quantities_by_good_id={},
            info={},
            ledger_id="ethereum",
            signing_payload={"tx": tx},
        )

        return tx_message

    def _create_deploy_transaction(
        self, deployer_address: Address, ledger_api: LedgerApi
    ) -> Dict[str, Any]:
        """
        Get the deployment transaction.

        :params: deployer_address: The address that will deploy the contract.

        :returns tx: The Transaction dictionary.
        """
        # create the transaction dict
        tx_data = self.instance.constructor().__dict__.get("data_in_transaction")
        tx = {
            "from": deployer_address,  # Only 'from' address, don't insert 'to' address
            "value": 0,  # Add how many ethers you'll transfer during the deploy
            "gas": 0,  # Trying to make it dynamic ..
            "gasPrice": ledger_api.api.toWei("50", "gwei"),  # Get Gas Price
            "nonce": ledger_api.api.eth.getTransactionCount(
                deployer_address
            ),  # Get Nonce
            "data": tx_data,  # Here is the data sent through the network
        }

        # estimate the gas and update the transaction dict
        gas_estimate = ledger_api.api.eth.estimateGas(transaction=tx)
        logger.info("gas estimate deploy: {}".format(gas_estimate))
        tx["gas"] = gas_estimate
        return tx

    def get_create_batch_transaction(
        self, deployer_address: Address, ledger_api: LedgerApi
    ) -> TransactionMessage:
        """
        Create an mint a batch of items.

        :params address: The address that will receive the items
        :params mint_quantities: A list[10] of ints. The index represents the id in the item_ids list.
        """
        # create the items

        tx = self._get_create_batch_tx(
            deployer_address=deployer_address, ledger_api=ledger_api
        )

        #  Create the transaction message for the Decision maker
        tx_message = TransactionMessage(
            performative=TransactionMessage.Performative.PROPOSE_FOR_SIGNING,
            skill_callback_ids=[ContractId("fetchai", "erc1155_skill", "0.1.0")],
            tx_id="contract_create_batch",
            tx_sender_addr=deployer_address,
            tx_counterparty_addr="",
            tx_amount_by_currency_id={"ETH": 0},
            tx_sender_fee=0,
            tx_counterparty_fee=0,
            tx_quantities_by_good_id={},
            info={},
            ledger_id="ethereum",
            signing_payload={"tx": tx},
        )

        return tx_message

    def _get_create_batch_tx(
        self, deployer_address: Address, ledger_api: LedgerApi
    ) -> str:
        """Create a batch of items."""
        # create the items
        nonce = ledger_api.api.eth.getTransactionCount(deployer_address)
        tx = self.instance.functions.createBatch(
            deployer_address, self.item_ids
        ).buildTransaction(
            {
                "chainId": 3,
                "gas": 300000,
                "gasPrice": ledger_api.api.toWei("50", "gwei"),
                "nonce": nonce,
            }
        )
        return tx

    def get_mint_batch_transaction(
        self,
        deployer_address: Address,
        recipient_address: Address,
        mint_quantities: List[int],
        ledger_api: LedgerApi,
    ):

        assert len(mint_quantities) == len(self.item_ids), "Wrong number of items."
        tx = self._create_mint_batch_tx(
            deployer_address=deployer_address,
            recipient_address=recipient_address,
            batch_mint_quantities=mint_quantities,
            ledger_api=ledger_api,
        )

        tx_message = TransactionMessage(
            performative=TransactionMessage.Performative.PROPOSE_FOR_SIGNING,
            skill_callback_ids=[ContractId("fetchai", "erc1155_skill", "0.1.0")],
            tx_id="contract_mint_batch",
            tx_sender_addr=deployer_address,
            tx_counterparty_addr="",
            tx_amount_by_currency_id={"ETH": 0},
            tx_sender_fee=0,
            tx_counterparty_fee=0,
            tx_quantities_by_good_id={},
            info={},
            ledger_id="ethereum",
            signing_payload={"tx": tx},
        )

        return tx_message

    def _create_mint_batch_tx(
        self, deployer_address, recipient_address, batch_mint_quantities, ledger_api,
    ) -> str:
        """Mint a batch of items."""
        # mint batch
        nonce = ledger_api.api.eth.getTransactionCount(
            ledger_api.api.toChecksumAddress(deployer_address)
        )
        nonce += 1
        tx = self.instance.functions.mintBatch(
            recipient_address, self.item_ids, batch_mint_quantities
        ).buildTransaction(
            {
                "chainId": 3,
                "gas": 300000,
                "gasPrice": ledger_api.api.toWei("50", "gwei"),
                "nonce": nonce,
            }
        )

        return tx

    def _create_trade_tx(self, from_address, to_address, item_id, from_supply, to_supply, value_eth_wei, trade_nonce, signature, ledger_api: LedgerApi) -> str:
        """
        Create a trade tx.

        :params terms: The class (can be Dict[str, Any]) that contains the details for the transaction.
        :params signature: The signed terms from the counterparty.
        """
        data = b"hello"
        nonce = ledger_api.api.eth.getTransactionCount(from_address)
        tx = self.instance.functions.trade(
            from_address,
            to_address,
            item_id,
            from_supply,
            to_supply,
            value_eth_wei,
            trade_nonce,
            signature,
            data,
        ).buildTransaction(
            {
                "chainId": 3,
                "gas": 2818111,
                "from": from_address,
                "value": value_eth_wei,
                "gasPrice": ledger_api.api.toWei("50", "gwei"),
                "nonce": nonce,
            }
        )

        return tx

    def _create_trade_batch_tx(self, terms, signature, ledger_api: LedgerApi) -> str:
        """
        Create a batch trade tx.

        :params terms: The class (can be Dict[str, Any]) that contains the details for the transaction.
        :params signature: The signed terms from the counterparty.
        """
        data = b"hello"
        nonce = ledger_api.api.eth.getTransactionCount(terms.from_address)
        import pdb

        pdb.set_trace()
        tx = self.instance.functions.tradeBatch(
            terms.from_address,
            terms.to_address,
            terms.item_ids,
            terms.from_supplies,
            terms.to_supplies,
            terms.value_eth_wei,
            terms.trade_nonce,
            signature,
            data,
        ).buildTransaction(
            {
                "chainId": 3,
                "gas": 2818111,
                "from": terms.from_address,
                "value": terms.value_eth_wei,
                "gasPrice": ledger_api.api.toWei("50", "gwei"),
                "nonce": nonce,
            }
        )
        return tx

    def get_balance(self, from_address: Address, item_id: int):
        """Get the balance for the specific id."""
        return self.instance.functions.balanceOf(from_address, item_id).call()

    def get_atomic_swap_single_proposal(
        self, from_address, to_address, item_id, from_supply, to_supply, value, trade_nonce, signature, ledger_api: LedgerApi
    ) -> TransactionMessage:
        """Make a trustless trade between to agents for a single token."""
        # assert self.address == terms.from_address, "Wrong from address"
        value_eth_wei = ledger_api.api.toWei(value, 'ether')
        tx = self._create_trade_tx(from_address, to_address, item_id, from_supply, to_supply, value_eth_wei, trade_nonce, signature, ledger_api)

        tx_message = TransactionMessage(
            performative=TransactionMessage.Performative.PROPOSE_FOR_SIGNING,
            skill_callback_ids=[ContractId("fetchai", "erc1155_skill", "0.1.0")],
            tx_id="contract_deployment",
            tx_sender_addr=from_address,
            tx_counterparty_addr="",
            tx_amount_by_currency_id={"ETH": 0},
            tx_sender_fee=0,
            tx_counterparty_fee=0,
            tx_quantities_by_good_id={},
            info={},
            ledger_id="ethereum",
            signing_payload={"tx": tx},
        )

        return tx_message

    def get_balance_of_batch(self, address):
        """Get the balance for a batch of items"""
        return self.instance.functions.balanceOfBatch(
            [address] * 10, self.item_ids
        ).call()

    def get_atomic_swap_batch_transaction_proposal(
        self, deployer_address, contract, terms, signature
    ) -> TransactionMessage:
        """Make a trust-less trade for a batch of items between 2 agents."""
        assert deployer_address == terms.from_address, "Wrong 'from' address"
        tx = contract.get_trade_batch_tx(terms=terms, signature=signature)

        tx_message = TransactionMessage(
            performative=TransactionMessage.Performative.PROPOSE_FOR_SIGNING,
            skill_callback_ids=[ContractId("fetchai", "erc1155_skill", "0.1.0")],
            tx_id="contract_deployment",
            tx_sender_addr=terms.from_address,
            tx_counterparty_addr="",
            tx_amount_by_currency_id={"ETH": 0},
            tx_sender_fee=0,
            tx_counterparty_fee=0,
            tx_quantities_by_good_id={},
            info={},
            ledger_id="ethereum",
            signing_payload={"tx": tx},
        )

        return tx_message

    def get_hash_single_transaction(self, terms) -> TransactionMessage:
        """Sign the transaction before send them to agent1."""
        # assert self.address == terms.to_address
        from_address_hash = self.instance.functions.getAddress(
            terms.from_address
        ).call()
        to_address_hash = self.instance.functions.getAddress(terms.to_address).call()
        tx_hash = Helpers().get_single_hash(
            _from=from_address_hash,
            _to=to_address_hash,
            _id=terms.item_id,
            _from_value=terms.from_supply,
            _to_value=terms.to_supply,
            _value_eth=terms.value_eth_wei,
            _nonce=terms.trade_nonce,
        )

        tx_message = TransactionMessage(
            performative=TransactionMessage.Performative.PROPOSE_FOR_SIGNING,
            skill_callback_ids=[ContractId("fetchai", "erc1155_skill", "0.1.0")],
            tx_id="contract_deployment",
            tx_sender_addr=terms.from_address,
            tx_counterparty_addr="",
            tx_amount_by_currency_id={"ETH": 0},
            tx_sender_fee=0,
            tx_counterparty_fee=0,
            tx_quantities_by_good_id={},
            info={},
            ledger_id="ethereum",
            signing_payload={"tx_hashh": tx_hash},
        )

        return tx_message

    def get_hash_batch_transaction(self, terms):
        """Sign the transaction before send them to agent1."""
        # assert self.address == terms.to_address
        from_address_hash = self.instance.functions.getAddress(
            terms.from_address
        ).call()
        to_address_hash = self.instance.functions.getAddress(terms.to_address).call()
        tx_hash = Helpers().get_hash(
            _from=from_address_hash,
            _to=to_address_hash,
            _ids=terms.item_ids,
            _from_values=terms.from_supplies,
            _to_values=terms.to_supplies,
            _value_eth=terms.value_eth_wei,
            _nonce=terms.trade_nonce,
        )

        return tx_hash

    def generate_trade_nonce(self, address):
        """Generate a valid trade nonce."""
        trade_nonce = random.randrange(0, 10000000)
        while self.instance.functions.is_nonce_used(address, trade_nonce).call():
            trade_nonce = random.randrange(0, 10000000)
        return trade_nonce


class Helpers:
    """Helper functions for hashing."""

    def get_single_hash(
        self, _from, _to, _id, _from_value, _to_value, _value_eth, _nonce
    ) -> bytes:
        """Generate a hash mirroring the way we are creating this in the contract."""
        return keccak256(
            b"".join(
                [
                    _from,
                    _to,
                    _id.to_bytes(32, "big"),
                    _from_value.to_bytes(32, "big"),
                    _to_value.to_bytes(32, "big"),
                    _value_eth.to_bytes(32, "big"),
                    _nonce.to_bytes(32, "big"),
                ]
            )
        )

    def get_hash(
        self, _from, _to, _ids, _from_values, _to_values, _value_eth, _nonce
    ) -> bytes:
        """Generate a hash mirroring the way we are creating this in the contract."""
        aggregate_hash = keccak256(
            b"".join(
                [
                    _ids[0].to_bytes(32, "big"),
                    _from_values[0].to_bytes(32, "big"),
                    _to_values[0].to_bytes(32, "big"),
                ]
            )
        )
        for i in range(len(_ids)):
            if not i == 0:
                aggregate_hash = keccak256(
                    b"".join(
                        [
                            aggregate_hash,
                            _ids[i].to_bytes(32, "big"),
                            _from_values[i].to_bytes(32, "big"),
                            _to_values[i].to_bytes(32, "big"),
                        ]
                    )
                )

        m_list = []
        m_list.append(_from)
        m_list.append(_to)
        m_list.append(aggregate_hash)
        m_list.append(_value_eth.to_bytes(32, "big"))
        m_list.append(_nonce.to_bytes(32, "big"))
        return keccak256(b"".join(m_list))

    def generate_id(self, token_id, item_id):
        token_id = token_id
        index = item_id
        final_id_int = (token_id << 128) + index
        return final_id_int


    def generate_trade_nonce(self, contract, address):
        """Generate a valid trade nonce."""
        trade_nonce = random.randrange(0, 10000000)
        while contract.instance.functions.is_nonce_used(address, trade_nonce).call():
            trade_nonce = random.randrange(0, 10000000)
        return trade_nonce


class TermsSingle:
    """Terms of the single trade."""

    def __init__(self, ledger_api, from_address, to_address, contract):
        """Initialization."""
        self.from_address = from_address
        self.to_address = to_address
        self.item_id = contract.item_ids[0]
        self.from_supply = 2
        self.to_supply = 0
        self.value_eth_wei = ledger_api.api.toWei('0', 'ether')
        self.trade_nonce = Helpers().generate_trade_nonce(contract=contract,
                                                          address=from_address)
        logger.info("terms_single: from={}, to={}, item_id={}, from_supply={}, to_supply={}, value_eth_wei={}, trade_nonce={}".format(self.from_address,
                                                                                                                                      self.to_address,
                                                                                                                                      self.item_id,
                                                                                                                                      self.from_supply,
                                                                                                                                      self.to_supply,
                                                                                                                                      self.value_eth_wei,
                                                                                                                                      self.trade_nonce))
