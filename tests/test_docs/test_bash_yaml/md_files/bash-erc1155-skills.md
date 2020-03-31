``` bash
python scripts/oef/launch.py -c ./scripts/oef/launch_config.json
```
``` bash
aea create my_erc1155_deploy
cd my_erc1155_deploy
aea add connection fetchai/oef:0.1.0
aea add skill fetchai/erc1155_deploy:0.1.0
aea add contract fetchai/erc1155:0.1.0
aea install
```
``` bash
aea generate-key ethereum
aea add-key ethereum eth_private_key.txt
```
``` bash
aea create my_erc1155_client
cd my_erc1155_client
aea add connection fetchai/oef:0.1.0
aea add skill fetchai/erc1155_client:0.1.0
aea add contract fetchai/erc1155:0.1.0
aea install
```
``` bash
aea generate-key ethereum
aea add-key ethereum eth_private_key.txt
```
``` bash
aea generate-wealth ethereum
```
``` bash
addr: ${OEF_ADDR: 127.0.0.1}
```
``` bash
aea run --connections fetchai/oef:0.1.0
```
``` bash
cd ..
aea delete my_seller_aea
aea delete my_buyer_aea
```
``` yaml
ledger_apis:
  ethereum:
    address: https://ropsten.infura.io/v3/f00f7b3ba0e848ddbdc8941c527447fe
    chain_id: 3
    gas_price: 50
```
``` yaml
name: erc1155_deploy
author: fetchai
version: 0.1.0
license: Apache-2.0
fingerprint:
  __init__.py: Qmbm3ZtGpfdvvzqykfRqbaReAK9a16mcyK7qweSfeN5pq1
  behaviours.py: QmRPDq4oDTozx5BhqU1GEXCH2CcCC7N8sTRSraAq8zHJ6g
  handlers.py: QmZpZ1aGpSD7CAjgJWYNWv97DN65Jeqkipes6RtZREan8E
  strategy.py: QmWpc8aMte2vJ4akiKn6qTfXWavfE1vBtJqX1E7CFuLYaC
description: "The ERC1155 deploy skill has the ability to deploy and interact with the smart contract."
contracts: ['fetchai/erc1155:0.1.0']
behaviours:
  service_registration:
    class_name: ServiceRegistrationBehaviour
    args:
      services_interval: 60
handlers:
  default:
    class_name: FIPAHandler
    args: {}
  transaction:
    class_name: TransactionHandler
    args: {}
models:
  strategy:
    class_name: Strategy
    args:
      ledger_id: 'ethereum'
      is_ledger_tx: True
      nft: 1
      ft: 2
      nb_tokens: 10
      from_supply: 10
      to_supply: 0
      value: 0
      search_schema:
        attribute_one:
          name: has_erc1155_contract
          type: bool
          is_required: True
      search_data:
        has_erc1155_contract: True
protocols: ['fetchai/fipa:0.1.0', 'fetchai/oef:0.1.0', 'fetchai/default:0.1.0']
ledgers: ['fetchai']
dependencies:
  vyper: { version: "==0.1.0b12"}
```