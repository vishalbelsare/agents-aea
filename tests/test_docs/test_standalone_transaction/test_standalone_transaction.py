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

"""This module contains the tests for the code-blocks in the standalone-transaction.md file."""

import logging
import os
from unittest.mock import patch

from aea.test_tools.test_cases import BaseAEATestCase

from tests.conftest import CUR_PATH, ROOT_DIR
from tests.test_docs.helper import extract_code_blocks, extract_python_code

from .standalone_transaction import (
    logger,
    run,
)

MD_FILE = "docs/standalone-transaction.md"
PY_FILE = "test_docs/test_standalone_transaction/standalone_transaction.py"

test_logger = logging.getLogger(__name__)


class TestStandaloneTransaction(BaseAEATestCase):
    """This class contains the tests for the code-blocks in the agent-vs-aea.md file."""

    @classmethod
    def _patch_logger(cls):

        cls.patch_logger_info = patch.object(logger, "info")
        cls.mocked_logger_info = cls.patch_logger_info.__enter__()

    @classmethod
    def _unpatch_logger(cls):
        cls.mocked_logger_info.__exit__()

    @classmethod
    def setup_class(cls):
        """Setup the test class."""
        BaseAEATestCase.setup_class()
        cls._patch_logger()
        doc_path = os.path.join(ROOT_DIR, MD_FILE)
        cls.code_blocks = extract_code_blocks(filepath=doc_path, filter="python")
        test_code_path = os.path.join(CUR_PATH, PY_FILE)
        cls.python_file = extract_python_code(test_code_path)

    def test_read_md_file(self):
        """Test the last code block, that is the full listing of the demo from the Markdown."""
        assert (
            self.code_blocks[-1] == self.python_file
        ), "Files must be exactly the same."

    def test_run_end_to_end(self):
        """Run the transaction from the file."""
        try:
            run()
            self.mocked_logger_info.assert_any_call("Transaction complete.")
        except RuntimeError:
            test_logger.info("RuntimeError: Some transactions have failed")

    # def test_run_mocked_digest(self):
    #     """Run the transaction from the file."""
    #     try:
    #         with patch(
    #             "aea.crypto.helpers.try_generate_testnet_wealth", return_value=Mock()
    #         ):
    #             with patch(
    #                 "aea.crypto.fetchai.FetchAIApi.send_transaction",
    #                 return_value="cdbea3c61cf243416b3a479f3262b972f544370acd8cb36448f077d67cd2936c",
    #             ):
    #                 run()
    #                 self.mocked_logger_info.assert_any_call(
    #                     "The transaction digest is cdbea3c61cf243416b3a479f3262b972f544370acd8cb36448f077d67cd2936c"
    #                 )
    #                 self.mocked_logger_info.assert_any_call("Transaction complete.")
    #     except RuntimeError:
    #         test_logger.info("RuntimeError: Some transactions have failed")

    def test_code_blocks_exist(self):
        """Test that all the code-blocks exist in the python file."""
        for blocks in self.code_blocks:
            assert (
                blocks in self.python_file
            ), "Code-block doesn't exist in the python file."
