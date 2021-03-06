``` bash
aea create my_aea && cd my_aea
aea scaffold skill my_search
```
``` yaml
name: my_search
author: fetchai
version: 0.1.0
description: 'A simple search skill utilising the OEF search and communication node.'
license: Apache-2.0
aea_version: '>=0.5.0, <0.6.0'
fingerprint: {}
fingerprint_ignore_patterns: []
contracts: []
protocols:
- 'fetchai/oef_search:0.3.0'
skills: []
behaviours:
  my_search_behaviour:
    args:
      tick_interval: 5
    class_name: MySearchBehaviour
handlers:
  my_search_handler:
    args: {}
    class_name: MySearchHandler
models: {}
dependencies: {}
```
``` bash
aea fingerprint skill fetchai/my_search:0.1.0
```
``` bash
aea add protocol fetchai/oef_search:0.3.0
```
``` bash
aea add connection fetchai/oef:0.6.0
aea install
aea config set agent.default_connection fetchai/oef:0.6.0
```
``` bash
python scripts/oef/launch.py -c ./scripts/oef/launch_config.json
```
``` bash
aea fetch fetchai/simple_service_registration:0.7.0 && cd simple_service_registration
aea run --connections fetchai/oef:0.6.0
```
``` yaml
name: simple_service_registration
author: fetchai
version: 0.2.0
description: The simple service registration skills is a skill to register a service.
license: Apache-2.0
aea_version: '>=0.5.0, <0.6.0'
fingerprint:
  __init__.py: QmNkZAetyctaZCUf6ACxP5onGWsSxu2hjSNoFmJ3ta6Lta
  behaviours.py: QmT4nDbtEz5BDtSbw34fXzdZg4HfbYgV3dfMfsGe9R61n4
  strategy.py: QmWwPzDvmeuVutPwxL5taU1tBGA6aiMDRwo6bTTtLxxHRn
fingerprint_ignore_patterns: []
contracts: []
protocols:
- fetchai/oef_search:0.3.0
behaviours:
  service:
    args:
      services_interval: 30
    class_name: ServiceRegistrationBehaviour
handlers: {}
models:
  strategy:
    args:
      data_model:
        attribute_one:
          is_required: true
          name: country
          type: str
        attribute_two:
          is_required: true
          name: city
          type: str
      data_model_name: location
      service_data:
        city: Cambridge
        country: UK
    class_name: Strategy
dependencies: {}
```
```bash
aea run --connections fetchai/oef:0.6.0
```
