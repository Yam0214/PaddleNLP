# Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
# Copyright 2021 The HuggingFace Inc. team.
#
# Licensed under the Apache License, Version 2.0 (the "License"
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

__all__ = ["FunnelTokenizer"]

from collections.abc import Iterable
import os
from ..bert.tokenizer import BertTokenizer
from .. import BasicTokenizer, WordpieceTokenizer
from .. import PretrainedTokenizer
import unicodedata
from ..tokenizer_utils import _is_control


def stem(token):
    if token[:2] == "##":
        return token[2:]
    else:
        return token


class FunnelTokenizer(BertTokenizer):
    cls_token_type_id = 2
    resource_files_names = {"vocab_file": "vocab.txt"}  # for save_pretrained
    pretrained_resource_files_map = {
        "vocab_file": {
            "funnel-transformer/small": "https://bj.bcebos.com/paddlenlp/models/transformers/funnel-transformer/small/vocab.txt",
            "funnel-transformer/small-base": "https://bj.bcebos.com/paddlenlp/models/transformers/funnel-transformer/small-base/vocab.txt",
            "funnel-transformer/medium": "https://bj.bcebos.com/paddlenlp/models/transformers/funnel-transformer/medium/vocab.txt",
            "funnel-transformer/medium-base": "https://bj.bcebos.com/paddlenlp/models/transformers/funnel-transformer/medium-base/vocab.txt",
            "funnel-transformer/intermediate": "https://bj.bcebos.com/paddlenlp/models/transformers/funnel-transformer/intermediate/vocab.txt",
            "funnel-transformer/intermediate-base": "https://bj.bcebos.com/paddlenlp/models/transformers/funnel-transformer/intermediate-base/vocab.txt",
            "funnel-transformer/large": "https://bj.bcebos.com/paddlenlp/models/transformers/funnel-transformer/large/vocab.txt",
            "funnel-transformer/large-base": "https://bj.bcebos.com/paddlenlp/models/transformers/funnel-transformer/large-base/vocab.txt",
            "funnel-transformer/xlarge": "https://bj.bcebos.com/paddlenlp/models/transformers/funnel-transformer/xlarge/vocab.txt",
            "funnel-transformer/xlarge-base": "https://bj.bcebos.com/paddlenlp/models/transformers/funnel-transformer/xlarge-base/vocab.txt",
        },
    }
    pretrained_init_configuration = {
        "funnel-transformer/small": {"do_lower_case": True},
        "funnel-transformer/small-base": {"do_lower_case": True},
        "funnel-transformer/medium": {"do_lower_case": True},
        "funnel-transformer/medium-base": {"do_lower_case": True},
        "funnel-transformer/intermediate": {"do_lower_case": True},
        "funnel-transformer/intermediate-base": {"do_lower_case": True},
        "funnel-transformer/large": {"do_lower_case": True},
        "funnel-transformer/large-base": {"do_lower_case": True},
        "funnel-transformer/xlarge": {"do_lower_case": True},
        "funnel-transformer/xlarge-base": {"do_lower_case": True},
    }

    def __init__(
        self,
        vocab_file,
        do_lower_case=True,
        unk_token="<unk>",
        sep_token="<sep>",
        pad_token="<pad>",
        cls_token="<cls>",
        mask_token="<mask>",
        bos_token="<s>",
        eos_token="</s>",
        wordpieces_prefix="##",
        **kwargs
    ):
        if not os.path.isfile(vocab_file):
            raise ValueError(
                "Can't find a vocabulary file at path '{}'. To load the "
                "vocabulary from a pretrained model please use "
                "`tokenizer = BertTokenizer.from_pretrained(PRETRAINED_MODEL_NAME)`".format(vocab_file)
            )
        self.vocab = self.load_vocabulary(vocab_file, unk_token=unk_token)
        self.basic_tokenizer = BasicTokenizer(do_lower_case=do_lower_case)
        self.wordpiece_tokenizer = WordpieceTokenizer(vocab=self.vocab, unk_token=unk_token)

    def __call__(
        self,
        text,
        text_pair=None,
        max_seq_len=None,
        stride=0,
        is_split_into_words=False,
        pad_to_max_seq_len=False,
        truncation_strategy="longest_first",
        return_position_ids=False,
        return_token_type_ids=True,
        return_attention_mask=True,
        return_length=False,
        return_overflowing_tokens=False,
        return_special_tokens_mask=False,
    ):
        return super().__call__(
            text,
            text_pair=text_pair,
            max_seq_len=max_seq_len,
            stride=stride,
            is_split_into_words=is_split_into_words,
            pad_to_max_seq_len=pad_to_max_seq_len,
            truncation_strategy=truncation_strategy,
            return_position_ids=return_position_ids,
            return_token_type_ids=return_token_type_ids,
            return_attention_mask=return_attention_mask,
            return_length=return_length,
            return_overflowing_tokens=return_overflowing_tokens,
            return_special_tokens_mask=return_special_tokens_mask,
        )

    @property
    def vocab_size(self):
        """
        return the size of vocabulary.
        Returns:
            int: the size of vocabulary.
        """
        return len(self.vocab)

    def _tokenize(self, text):
        """
        End-to-end tokenization for BERT models.
        Args:
            text (str): The text to be tokenized.

        Returns:
            list: A list of string representing converted tokens.
        """
        split_tokens = []
        for token in self.basic_tokenizer.tokenize(text):
            for sub_token in self.wordpiece_tokenizer.tokenize(token):
                split_tokens.append(sub_token)
        return split_tokens

    def tokenize(self, text):
        """
        End-to-end tokenization for BERT models.
        Args:
            text (str): The text to be tokenized.

        Returns:
            list: A list of string representing converted tokens.
        """
        return self._tokenize(text)

    def convert_tokens_to_string(self, tokens):
        """
        Converts a sequence of tokens (list of string) in a single string. Since
        the usage of WordPiece introducing `##` to concat subwords, also remove
        `##` when converting.
        Args:
            tokens (list): A list of string representing tokens to be converted.
        Returns:
            str: Converted string from tokens.
        """

        out_string = " ".join(tokens).replace(" ##", "").strip()
        out_string = (
            out_string.replace(" .", ".")
            .replace(" ?", "?")
            .replace(" !", "!")
            .replace(" ,", ",")
            .replace(" ' ", "'")
            .replace(" n't", "n't")
            .replace(" 'm", "'m")
            .replace(" 's", "'s")
            .replace(" 've", "'ve")
            .replace(" 're", "'re")
        )
        return out_string

    def num_special_tokens_to_add(self, pair=False):
        """
        Returns the number of added tokens when encoding a sequence with special tokens.

        Note:
            This encodes inputs and checks the number of added tokens, and is therefore not efficient. Do not put this
            inside your training loop.

        Args:
            pair: Returns the number of added tokens in the case of a sequence pair if set to True, returns the
                number of added tokens in the case of a single sequence if set to False.

        Returns:
            Number of tokens added to sequences
        """
        token_ids_0 = []
        token_ids_1 = []
        return len(self.build_inputs_with_special_tokens(token_ids_0, token_ids_1 if pair else None))

    def build_offset_mapping_with_special_tokens(self, offset_mapping_0, offset_mapping_1=None):
        """
        Build offset map from a pair of offset map by concatenating and adding offsets of special tokens.

        A BERT offset_mapping has the following format:
        ::
            - single sequence: ``(0,0) X (0,0)``
            - pair of sequences: `(0,0) A (0,0) B (0,0)``

        Args:
            offset_mapping_ids_0 (:obj:`List[tuple]`):
                List of char offsets to which the special tokens will be added.
            offset_mapping_ids_1 (:obj:`List[tuple]`, `optional`):
                Optional second list of char offsets for offset mapping pairs.

        Returns:
            :obj:`List[tuple]`: List of char offsets with the appropriate offsets of special tokens.
        """
        if offset_mapping_1 is None:
            return [(0, 0)] + offset_mapping_0 + [(0, 0)]

        return [(0, 0)] + offset_mapping_0 + [(0, 0)] + offset_mapping_1 + [(0, 0)]

    def create_token_type_ids_from_sequences(self, token_ids_0, token_ids_1=None):
        _sep = [self.sep_token_id]
        _cls = [self.cls_token_id]
        if token_ids_1 is None:
            return len(_cls) * [self.cls_token_type_id] + len(token_ids_0 + _sep) * [0]
        return len(_cls) * [self.cls_token_type_id] + len(token_ids_0 + _sep) * [0] + len(token_ids_1 + _sep) * [1]

    def get_special_tokens_mask(self, token_ids_0, token_ids_1=None, already_has_special_tokens=False):
        """
        Retrieves sequence ids from a token list that has no special tokens added. This method is called when adding
        special tokens using the tokenizer ``encode`` methods.

        Args:
            token_ids_0 (List[int]): List of ids of the first sequence.
            token_ids_1 (List[int], optional): List of ids of the second sequence.
            already_has_special_tokens (bool, optional): Whether or not the token list is already
                formatted with special tokens for the model. Defaults to None.

        Returns:
            results (List[int]): The list of integers in the range [0, 1]: 1 for a special token, 0 for a sequence token.
        """

        if already_has_special_tokens:
            if token_ids_1 is not None:
                raise ValueError(
                    "You should not supply a second sequence if the provided sequence of "
                    "ids is already formatted with special tokens for the model."
                )
            return list(map(lambda x: 1 if x in [self.sep_token_id, self.cls_token_id] else 0, token_ids_0))

        if token_ids_1 is not None:
            return [1] + ([0] * len(token_ids_0)) + [1] + ([0] * len(token_ids_1)) + [1]
        return [1] + ([0] * len(token_ids_0)) + [1]

    def truncate_sequences(
        self, ids, pair_ids=None, num_tokens_to_remove=0, truncation_strategy="longest_first", stride=0
    ):
        """
        Truncates a sequence pair in place to the maximum length.

        Args:
            ids: list of tokenized input ids. Can be obtained from a string by chaining the
                `tokenize` and `convert_tokens_to_ids` methods.
            pair_ids: Optional second list of input ids. Can be obtained from a string by chaining the
                `tokenize` and `convert_tokens_to_ids` methods.
            num_tokens_to_remove (:obj:`int`, `optional`, defaults to ``0``):
                number of tokens to remove using the truncation strategy
            truncation_strategy: string selected in the following options:
                - 'longest_first' (default) Iteratively reduce the inputs sequence until the input is under max_seq_len
                    starting from the longest one at each token (when there is a pair of input sequences).
                    Overflowing tokens only contains overflow from the first sequence.
                - 'only_first': Only truncate the first sequence. raise an error if the first sequence is shorter or equal to than num_tokens_to_remove.
                - 'only_second': Only truncate the second sequence
                - 'do_not_truncate': Does not truncate (raise an error if the input sequence is longer than max_seq_len)
            stride (:obj:`int`, `optional`, defaults to ``0``):
                If set to a number along with max_seq_len, the overflowing tokens returned will contain some tokens
                from the main sequence returned. The value of this argument defines the number of additional tokens.
        """
        if num_tokens_to_remove <= 0:
            return ids, pair_ids, []

        if truncation_strategy == "longest_first":
            overflowing_tokens = []
            if pair_ids is None or len(ids) <= len(pair_ids):
                for _ in range(num_tokens_to_remove):
                    if pair_ids is None or len(ids) >= len(pair_ids):
                        overflowing_tokens = [ids[-1]] + overflowing_tokens
                        ids = ids[:-1]
                    else:
                        pair_ids = pair_ids[:-1]
                window_len = min(len(ids), stride)
            else:
                for _ in range(num_tokens_to_remove):
                    if pair_ids is None or len(ids) > len(pair_ids):
                        overflowing_tokens = [ids[-1]] + overflowing_tokens
                        ids = ids[:-1]
                    else:
                        pair_ids = pair_ids[:-1]
                window_len = min(len(ids), stride)
            if window_len > 0:
                overflowing_tokens = ids[-window_len:] + overflowing_tokens
        elif truncation_strategy == "only_first":
            assert len(ids) > num_tokens_to_remove
            window_len = min(len(ids), stride + num_tokens_to_remove)
            overflowing_tokens = ids[-window_len:]
            ids = ids[:-num_tokens_to_remove]
        elif truncation_strategy == "only_second":
            assert pair_ids is not None and len(pair_ids) > num_tokens_to_remove
            window_len = min(len(pair_ids), stride + num_tokens_to_remove)
            overflowing_tokens = pair_ids[-window_len:]
            pair_ids = pair_ids[:-num_tokens_to_remove]
        elif truncation_strategy == "do_not_truncate":
            raise ValueError("Input sequence are too long for max_length. Please select a truncation strategy.")
        else:
            raise ValueError(
                "Truncation_strategy should be selected in ['longest_first', 'only_first', 'only_second', 'do_not_truncate']"
            )
        return (ids, pair_ids, overflowing_tokens)

    def batch_encode(
        self,
        batch_text_or_text_pairs,
        max_seq_len=512,
        pad_to_max_seq_len=False,
        stride=0,
        is_split_into_words=False,
        truncation_strategy="longest_first",
        return_position_ids=False,
        return_token_type_ids=True,
        return_attention_mask=False,
        return_length=False,
        return_overflowing_tokens=False,
        return_special_tokens_mask=False,
    ):
        """
        Performs tokenization and uses the tokenized tokens to prepare model
        inputs. It supports batch inputs of sequence or sequence pair.
        Args:
            batch_text_or_text_pairs (list):
                The element of list can be sequence or sequence pair, and the
                sequence is a string or a list of strings depending on whether
                it has been pretokenized. If each sequence is provided as a list
                of strings (pretokenized), you must set `is_split_into_words` as
                `True` to disambiguate with a sequence pair.
            max_seq_len (int, optional):
                If set to a number, will limit the total sequence returned so
                that it has a maximum length. If there are overflowing tokens,
                those overflowing tokens will be added to the returned dictionary
                when `return_overflowing_tokens` is `True`. Defaults to `None`.
            stride (int, optional):
                Only available for batch input of sequence pair and mainly for
                question answering usage. When for QA, `text` represents questions
                and `text_pair` represents contexts. If `stride` is set to a
                positive number, the context will be split into multiple spans
                where `stride` defines the number of (tokenized) tokens to skip
                from the start of one span to get the next span, thus will produce
                a bigger batch than inputs to include all spans. Moreover, 'overflow_to_sample'
                and 'offset_mapping' preserving the original example and position
                information will be added to the returned dictionary. Defaults to 0.
            pad_to_max_seq_len (bool, optional):
                If set to `True`, the returned sequences would be padded up to
                `max_seq_len` specified length according to padding side
                (`self.padding_side`) and padding token id. Defaults to `False`.
            truncation_strategy (str, optional):
                String selected in the following options:
                - 'longest_first' (default) Iteratively reduce the inputs sequence
                until the input is under `max_seq_len` starting from the longest
                one at each token (when there is a pair of input sequences).
                - 'only_first': Only truncate the first sequence.
                - 'only_second': Only truncate the second sequence.
                - 'do_not_truncate': Do not truncate (raise an error if the input
                sequence is longer than `max_seq_len`).
                Defaults to 'longest_first'.
            return_position_ids (bool, optional):
                Whether to include tokens position ids in the returned dictionary.
                Defaults to `False`.
            return_token_type_ids (bool, optional):
                Whether to include token type ids in the returned dictionary.
                Defaults to `True`.
            return_attention_mask (bool, optional):
                Whether to include the attention mask in the returned dictionary.
                Defaults to `False`.
            return_length (bool, optional):
                Whether to include the length of each encoded inputs in the
                returned dictionary. Defaults to `False`.
            return_overflowing_tokens (bool, optional):
                Whether to include overflowing token information in the returned
                dictionary. Defaults to `False`.
            return_special_tokens_mask (bool, optional):
                Whether to include special tokens mask information in the returned
                dictionary. Defaults to `False`.
        Returns:
            list[dict]:
                The dict has the following optional items:
                - **input_ids** (list[int]): List of token ids to be fed to a model.
                - **position_ids** (list[int], optional): List of token position ids to be
                  fed to a model. Included when `return_position_ids` is `True`
                - **token_type_ids** (list[int], optional): List of token type ids to be
                  fed to a model. Included when `return_token_type_ids` is `True`.
                - **attention_mask** (list[int], optional): List of integers valued 0 or 1,
                  where 0 specifies paddings and should not be attended to by the
                  model. Included when `return_attention_mask` is `True`.
                - **seq_len** (int, optional): The input_ids length. Included when `return_length`
                  is `True`.
                - **overflowing_tokens** (list[int], optional): List of overflowing tokens.
                  Included when if `max_seq_len` is specified and `return_overflowing_tokens`
                  is True.
                - **num_truncated_tokens** (int, optional): The number of overflowing tokens.
                  Included when if `max_seq_len` is specified and `return_overflowing_tokens`
                  is True.
                - **special_tokens_mask** (list[int], optional): List of integers valued 0 or 1,
                  with 0 specifying special added tokens and 1 specifying sequence tokens.
                  Included when `return_special_tokens_mask` is `True`.
                - **offset_mapping** (list[int], optional): list of pair preserving the
                  index of start and end char in original input for each token.
                  For a sqecial token, the index pair is `(0, 0)`. Included when
                  `stride` works.
                - **overflow_to_sample** (int, optional): Index of example from which this
                  feature is generated. Included when `stride` works.
        """

        def get_input_ids(text):
            if isinstance(text, str):
                tokens = self._tokenize(text)
                return self.convert_tokens_to_ids(tokens)
            elif isinstance(text, (list, tuple)) and len(text) > 0 and isinstance(text[0], str):
                return self.convert_tokens_to_ids(text)
            elif isinstance(text, (list, tuple)) and len(text) > 0 and isinstance(text[0], int):
                return text
            else:
                raise ValueError(
                    "Input is not valid. Should be a string, a list/tuple of strings or a list/tuple of integers."
                )

        batch_encode_inputs = []
        for example_id, tokens_or_pair_tokens in enumerate(batch_text_or_text_pairs):
            if not isinstance(tokens_or_pair_tokens, (list, tuple)):
                text, text_pair = tokens_or_pair_tokens, None
            elif is_split_into_words and not isinstance(tokens_or_pair_tokens[0], (list, tuple)):
                text, text_pair = tokens_or_pair_tokens, None
            else:
                text, text_pair = tokens_or_pair_tokens

            first_ids = get_input_ids(text)
            second_ids = get_input_ids(text_pair) if text_pair is not None else None

            if stride > 0 and second_ids is not None:

                max_len_for_pair = (
                    max_seq_len - len(first_ids) - self.num_special_tokens_to_add(pair=True)
                )  # need -4  <sep> A </sep> </sep> B <sep>

                token_offset_mapping = self.rematch(text)
                token_pair_offset_mapping = self.rematch(text_pair)

                while True:
                    encoded_inputs = {}

                    ids = first_ids
                    mapping = token_offset_mapping
                    if len(second_ids) <= max_len_for_pair:
                        pair_ids = second_ids
                        pair_mapping = token_pair_offset_mapping
                    else:
                        pair_ids = second_ids[:max_len_for_pair]
                        pair_mapping = token_pair_offset_mapping[:max_len_for_pair]

                    offset_mapping = self.build_offset_mapping_with_special_tokens(mapping, pair_mapping)
                    sequence = self.build_inputs_with_special_tokens(ids, pair_ids)
                    token_type_ids = self.create_token_type_ids_from_sequences(ids, pair_ids)

                    # Build output dictionnary
                    encoded_inputs["input_ids"] = sequence
                    if return_token_type_ids:
                        encoded_inputs["token_type_ids"] = token_type_ids
                    if return_special_tokens_mask:
                        encoded_inputs["special_tokens_mask"] = self.get_special_tokens_mask(ids, pair_ids)
                    if return_length:
                        encoded_inputs["seq_len"] = len(encoded_inputs["input_ids"])

                    # Check lengths
                    assert max_seq_len is None or len(encoded_inputs["input_ids"]) <= max_seq_len

                    # Padding
                    needs_to_be_padded = (
                        pad_to_max_seq_len and max_seq_len and len(encoded_inputs["input_ids"]) < max_seq_len
                    )

                    encoded_inputs["offset_mapping"] = offset_mapping

                    if needs_to_be_padded:
                        difference = max_seq_len - len(encoded_inputs["input_ids"])
                        if self.padding_side == "right":
                            if return_attention_mask:
                                encoded_inputs["attention_mask"] = [1] * len(encoded_inputs["input_ids"]) + [
                                    0
                                ] * difference
                            if return_token_type_ids:
                                # 0 for padding token mask
                                encoded_inputs["token_type_ids"] = (
                                    encoded_inputs["token_type_ids"] + [self.pad_token_type_id] * difference
                                )
                            if return_special_tokens_mask:
                                encoded_inputs["special_tokens_mask"] = (
                                    encoded_inputs["special_tokens_mask"] + [1] * difference
                                )
                            encoded_inputs["input_ids"] = (
                                encoded_inputs["input_ids"] + [self.pad_token_id] * difference
                            )
                            encoded_inputs["offset_mapping"] = encoded_inputs["offset_mapping"] + [(0, 0)] * difference
                        elif self.padding_side == "left":
                            if return_attention_mask:
                                encoded_inputs["attention_mask"] = [0] * difference + [1] * len(
                                    encoded_inputs["input_ids"]
                                )
                            if return_token_type_ids:
                                # 0 for padding token mask
                                encoded_inputs["token_type_ids"] = [
                                    self.pad_token_type_id
                                ] * difference + encoded_inputs["token_type_ids"]
                            if return_special_tokens_mask:
                                encoded_inputs["special_tokens_mask"] = [1] * difference + encoded_inputs[
                                    "special_tokens_mask"
                                ]
                            encoded_inputs["input_ids"] = [self.pad_token_id] * difference + encoded_inputs[
                                "input_ids"
                            ]
                            encoded_inputs["offset_mapping"] = [(0, 0)] * difference + encoded_inputs["offset_mapping"]
                    else:
                        if return_attention_mask:
                            encoded_inputs["attention_mask"] = [1] * len(encoded_inputs["input_ids"])

                    if return_position_ids:
                        encoded_inputs["position_ids"] = list(range(len(encoded_inputs["input_ids"])))

                    encoded_inputs["overflow_to_sample"] = example_id
                    batch_encode_inputs.append(encoded_inputs)

                    if len(second_ids) <= max_len_for_pair:
                        break
                    else:
                        second_ids = second_ids[max_len_for_pair - stride :]
                        token_pair_offset_mapping = token_pair_offset_mapping[max_len_for_pair - stride :]

            else:
                batch_encode_inputs.append(
                    self.encode(
                        first_ids,
                        second_ids,
                        max_seq_len=max_seq_len,
                        pad_to_max_seq_len=pad_to_max_seq_len,
                        truncation_strategy=truncation_strategy,
                        return_position_ids=return_position_ids,
                        return_token_type_ids=return_token_type_ids,
                        return_attention_mask=return_attention_mask,
                        return_length=return_length,
                        return_overflowing_tokens=return_overflowing_tokens,
                        return_special_tokens_mask=return_special_tokens_mask,
                    )
                )

        return batch_encode_inputs

    def rematch(self, text):
        """
        changed from https://github.com/bojone/bert4keras/blob/master/bert4keras/tokenizers.py#L372
        """
        tokens = self.custom_tokenize(text)

        normalized_text, char_mapping = "", []

        for i, ch in enumerate(text):
            if self.basic_tokenizer.do_lower_case:
                ch = ch.lower()
                ch = unicodedata.normalize("NFD", ch)
                ch = "".join([c for c in ch if unicodedata.category(c) != "Mn"])

            ch = "".join([c for c in ch if not (ord(c) == 0 or ord(c) == 0xFFFD or _is_control(c))])
            normalized_text += ch

            char_mapping.extend([i] * len(ch))

        text, token_mapping, offset = normalized_text, [], 0

        for token in tokens:
            token = stem(token)

            start = text[offset:].index(token) + offset
            end = start + len(token)

            token_mapping.append((char_mapping[start], char_mapping[end - 1] + 1))
            offset = end

        return token_mapping

    def custom_tokenize(self, text):
        split_tokens = []
        for token in self.basic_tokenizer.tokenize(text):
            for sub_token in self.wordpiece_tokenizer.tokenize(token):
                split_tokens.append(sub_token if sub_token != self.unk_token else token)
        return split_tokens
