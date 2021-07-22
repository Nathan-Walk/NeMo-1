# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from nemo_text_processing.text_normalization.normalize_with_audio import NormalizerWithAudio
from parameterized import parameterized

from .utils import PYNINI_AVAILABLE, parse_test_case_file


class TestRuNormalizeWithAudio:

    normalizer = NormalizerWithAudio(input_case='cased', lang='ru') if PYNINI_AVAILABLE else None

    @parameterized.expand(parse_test_case_file('ru/data_text_normalization/test_cases_cardinal.txt'))
    @pytest.mark.skipif(
        not PYNINI_AVAILABLE, reason="`pynini` not installed, please install via nemo_text_processing/setup.sh"
    )
    @pytest.mark.run_only_on('CPU')
    @pytest.mark.unit
    def test_norm_cardinal(self, expected, test_input):
        preds = self.normalizer.normalize(test_input, n_tagged=-1)
        assert expected in preds

    @parameterized.expand(parse_test_case_file('ru/data_text_normalization/test_cases_ordinal.txt'))
    @pytest.mark.skipif(
        not PYNINI_AVAILABLE, reason="`pynini` not installed, please install via nemo_text_processing/setup.sh"
    )
    @pytest.mark.run_only_on('CPU')
    @pytest.mark.unit
    def test_norm_ordinal(self, expected, test_input):
        preds = self.normalizer.normalize(test_input, n_tagged=-1)
        assert expected in preds

    @parameterized.expand(parse_test_case_file('ru/data_text_normalization/test_cases_decimal.txt'))
    @pytest.mark.skipif(
        not PYNINI_AVAILABLE, reason="`pynini` not installed, please install via nemo_text_processing/setup.sh"
    )
    @pytest.mark.run_only_on('CPU')
    @pytest.mark.unit
    def test_norm_decimal(self, expected, test_input):
        preds = self.normalizer.normalize(test_input, n_tagged=-1)
        assert expected in preds

    # @parameterized.expand(parse_test_case_file('ru/data_text_normalization/test_cases_measure_hard.txt'))
    # @pytest.mark.skipif(
    #     not PYNINI_AVAILABLE, reason="`pynini` not installed, please install via nemo_text_processing/setup.sh"
    # )
    # @pytest.mark.run_only_on('CPU')
    # @pytest.mark.unit
    # def test_norm_measure_hard(self, expected, test_input):
    #     preds = self.normalizer.normalize(test_input, n_tagged=-1)
    #     assert expected in preds

    @parameterized.expand(parse_test_case_file('ru/data_text_normalization/test_cases_measure.txt'))
    @pytest.mark.skipif(
        not PYNINI_AVAILABLE, reason="`pynini` not installed, please install via nemo_text_processing/setup.sh"
    )
    @pytest.mark.run_only_on('CPU')
    @pytest.mark.unit
    def test_norm_measure(self, expected, test_input):
        preds = self.normalizer.normalize(test_input, n_tagged=-1)
        assert expected in preds

    @parameterized.expand(parse_test_case_file('ru/data_text_normalization/test_cases_date.txt'))
    @pytest.mark.skipif(
        not PYNINI_AVAILABLE, reason="`pynini` not installed, please install via nemo_text_processing/setup.sh"
    )
    @pytest.mark.run_only_on('CPU')
    @pytest.mark.unit
    def test_norm_date(self, expected, test_input, n_tagged=-1):
        preds = self.normalizer.normalize(test_input, n_tagged=n_tagged)
        assert expected in preds, f'{test_input} FAILED with n_tagged={n_tagged}'

    @parameterized.expand(parse_test_case_file('ru/data_text_normalization/test_cases_electronic.txt'))
    @pytest.mark.skipif(
        not PYNINI_AVAILABLE, reason="`pynini` not installed, please install via nemo_text_processing/setup.sh"
    )
    @pytest.mark.run_only_on('CPU')
    @pytest.mark.unit
    def test_norm_date(self, expected, test_input):
        preds = self.normalizer.normalize(test_input, n_tagged=-1)
        assert expected in preds


if __name__ == '__main__':
    test = TestRuNormalizeWithAudio()
    test_cases = parse_test_case_file('ru/data_text_normalization/test_cases_date.txt')
    for expected, test_input in test_cases:
        test.test_norm_date(expected, test_input)
