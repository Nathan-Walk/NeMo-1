# Copyright (c) 2021, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
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

from nemo_text_processing.text_normalization.en.graph_utils import (
    NEMO_DIGIT,
    NEMO_NOT_QUOTE,
    GraphFst,
    delete_extra_space,
    delete_space,
    insert_space,
)
from nemo_text_processing.text_normalization.ru.utils import get_abs_path

try:
    import pynini
    from pynini.lib import pynutil

    PYNINI_AVAILABLE = True
except (ModuleNotFoundError, ImportError):
    PYNINI_AVAILABLE = True


class DateFst(GraphFst):
    """
    Finite state transducer for classifying date, e.g. 
        "01.05" -> tokens { date { day: "первое мая" } }

    Args:
        number_names: NumberNames graph
        deterministic: if True will provide a single transduction option,
            for False multiple transduction are generated (used for audio-based normalization)
    """

    def __init__(self, number_names: GraphFst, deterministic: bool):
        super().__init__(name="date", kind="classify", deterministic=deterministic)

        # Ru format: DD-MM-YYYY or DD-MM-YY
        month_abbr_to_names = pynini.string_file(get_abs_path("data/whitelist.tsv")).optimize()

        delete_sep = pynutil.add_weight(pynini.cross(".", " "), 1.09) | pynutil.add_weight(
            pynini.cross(pynini.union("/", "-"), " "), 1.1
        )

        numbers = number_names.ordinal_number_names

        zero = (pynutil.add_weight(pynini.cross("0", ""), -0.1)) | (
            pynutil.add_weight(pynini.cross("0", "ноль "), 0.1)
        )
        zero_digit = zero + pynini.compose(NEMO_DIGIT, numbers)
        digit_day = (pynini.union("1", "2", "3") + NEMO_DIGIT) | NEMO_DIGIT
        digit_day = pynini.compose(digit_day, numbers)
        day = (pynutil.insert("day: \"") + (zero_digit | digit_day) + pynutil.insert("\"")).optimize()

        digit_month = zero_digit | pynini.compose(pynini.accep("1") + NEMO_DIGIT, numbers)
        month_number_to_abbr = pynini.string_file(get_abs_path("data/months/numbers.tsv")).optimize()
        month_number_to_abbr = (
            (
                ((pynutil.add_weight(pynini.cross("0", ""), -0.1) | pynini.accep("1")) + NEMO_DIGIT) | NEMO_DIGIT
            ).optimize()
            @ month_number_to_abbr
        ).optimize()

        month_name = (
            (month_number_to_abbr @ month_abbr_to_names) | pynutil.add_weight(month_abbr_to_names, 0.1)
        ).optimize()
        month = (pynutil.insert("month: \"") + (month_name | digit_month) + pynutil.insert("\"")).optimize()
        year = pynini.compose(((NEMO_DIGIT ** 4) | (NEMO_DIGIT ** 2)), numbers).optimize()
        year |= zero_digit
        year_word_singular = ["год", "года", "году", "годом", "годе"]
        year_word_plural = ["годы", "годов", "годам", "годами", "годам"]

        year_word = pynini.cross("г.", pynini.union(*year_word_singular))
        year_word |= pynini.cross("гг.", pynini.union(*year_word_plural))
        year_word = pynini.closure((insert_space | pynini.accep(" ")) + year_word, 0, 1)
        year = pynutil.insert("year: \"") + year + year_word + pynutil.insert("\"")
        year_optional = pynini.closure(delete_sep + year, 0, 1).optimize()

        tagger_graph = (day + delete_sep + month + year_optional) | year

        # Verbalizer
        day = (
            pynutil.delete("day:")
            + delete_space
            + pynutil.delete("\"")
            + pynini.closure(NEMO_NOT_QUOTE, 1)
            + pynutil.delete("\"")
        )
        month = (
            pynutil.delete("month:")
            + delete_space
            + pynutil.delete("\"")
            + pynini.closure(NEMO_NOT_QUOTE, 1)
            + pynutil.delete("\"")
        )
        year = (
            pynutil.delete("year:")
            + delete_space
            + pynutil.delete("\"")
            + pynini.closure(NEMO_NOT_QUOTE, 1)
            + delete_space
            + pynutil.delete("\"")
        )
        year_optional = pynini.closure(delete_extra_space + year, 0, 1)
        graph_dmy = day + delete_extra_space + month + year_optional
        verbalizer_graph = (graph_dmy | year) + delete_space

        self.final_graph = pynini.compose(tagger_graph, verbalizer_graph).optimize()
        self.fst = pynutil.insert("day: \"") + self.final_graph + pynutil.insert("\"")
        self.fst = self.add_tokens(self.fst).optimize()
