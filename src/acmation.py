import json
class State(object):
    __slots__ = ['identifier', 'symbol', 'success', 'transitions', 'parent',
                 'matched_keyword', 'longest_strict_suffix', 'meta_data']

    def __init__(self, identifier, symbol=None, parent=None, success=False):
        self.symbol = symbol
        self.identifier = identifier
        self.transitions = {}
        self.parent = parent
        self.success = success
        self.matched_keyword = None
        self.longest_strict_suffix = None


class Result(object):
    __slots__ = ['keyword', 'location', 'meta_data']

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return_str= ''
        for k in self.__slots__:
            return_str += '{}:{:<20}\t'.format(k, json.dumps(getattr(self, k)))
        return return_str


class KeywordTree(object):
    def __init__(self, case_insensitive=False):
        '''
        @param case_insensitive: If true, case will be ignored when searching.
                                 Setting this to true will have a positive
                                 impact on performance.
                                 Defaults to false.
        '''
        self._zero_state = State(0)
        self._counter = 1
        self._finalized = False
        self._case_insensitive = case_insensitive

    def add(self, keywords, meta_data={}):
        '''
        Add a keyword to the tree.
        Can only be used before finalize() has been called.
        Keyword should be str or unicode.
        '''
        if self._finalized:
            raise ValueError('KeywordTree has been finalized.' +
                             ' No more keyword additions allowed')
        original_keyword = keywords
        if self._case_insensitive:
            if isinstance(keywords, list):
                keywords = map(str.lower, keywords)
            elif isinstance(keywords, str):
                keywords = keywords.lower()
            else:
                raise Exception('keywords error')
        if len(keywords) <= 0:
            return
        current_state = self._zero_state
        for word in keywords:
            try:
                current_state = current_state.transitions[word]
            except KeyError:
                next_state = State(self._counter, parent=current_state,
                                   symbol=word)
                self._counter += 1
                current_state.transitions[word] = next_state
                current_state = next_state
        current_state.success = True
        current_state.matched_keyword = original_keyword
        current_state.meta_data = meta_data

    def search(self, text, greedy=False, cut_word=False, cut_separator=' '):
        '''

        :param text:
        :param greedy:
        :param cut_word:
        :param cut_separator:
        :return:
        '''
        gen = self._search(text, cut_word, cut_separator)
        pre = None
        for result in gen:
            assert isinstance(result, Result)
            if not greedy:
                yield result
                continue
            if pre is None:
                pre = result

            if result.location > pre.location:
                yield pre
                pre = result
                continue

            if len(result.keyword) > len(pre.keyword):
                pre = result
                continue
        if pre is not None:
            yield pre

    def _search(self, text, cut_word=False, cut_separator=' '):
        '''
        Search a text for all occurences of the added keywords.
        Can only be called after finalized() has been called.
        O(n) with n = len(text)
        @return: Generator used to iterate over the results.
                 Or None if no keyword was found in the text.
        '''
        if not self._finalized:
            raise ValueError('KeywordTree has not been finalized.' +
                             ' No search allowed. Call finalize() first.')

        if self._case_insensitive:
            if isinstance(text, list):
                text = map(str.lower, text)
            elif isinstance(text, str):
                text = text.lower()
            else:
                raise Exception('context type error')

        if cut_word:
            if isinstance(text, str):
                text = text.split(cut_separator)

        current_state = self._zero_state
        for idx, symbol in enumerate(text):
            current_state = current_state.transitions.get(
                symbol, self._zero_state.transitions.get(symbol,
                                                         self._zero_state))
            state = current_state
            while state != self._zero_state:
                if state.success:
                    keyword = state.matched_keyword
                    yield Result(**{
                        'keyword': keyword,
                        'location': idx - len(keyword) + 1,
                        'meta_data': state.meta_data
                    })
                    # yield (keyword, idx - len(keyword) + 1, state.meta_data)
                state = state.longest_strict_suffix

    def finalize(self):
        '''
        Needs to be called after all keywords have been added and
        before any searching is performed.
        '''
        if self._finalized:
            raise ValueError('KeywordTree has already been finalized.')
        self._zero_state.longest_strict_suffix = self._zero_state
        self.search_lss_for_children(self._zero_state)
        self._finalized = True

    def __str__(self):
        return "ahocorapy KeywordTree"

    def search_lss_for_children(self, zero_state):
        processed = set()
        to_process = [zero_state]
        while to_process:
            state = to_process.pop()
            processed.add(state.identifier)
            for child in state.transitions.values():
                if child.identifier not in processed:
                    self.search_lss(child)
                    to_process.append(child)

    def search_lss(self, state):
        if state.longest_strict_suffix is None:
            parent = state.parent
            traversed = parent.longest_strict_suffix
            while True:
                if state.symbol in traversed.transitions and \
                                traversed.transitions[state.symbol] != state:
                    state.longest_strict_suffix = \
                        traversed.transitions[state.symbol]
                    break
                elif traversed == self._zero_state:
                    state.longest_strict_suffix = self._zero_state
                    break
                else:
                    traversed = traversed.longest_strict_suffix
            suffix = state.longest_strict_suffix
            if suffix.longest_strict_suffix is None:
                self.search_lss(suffix)
            for symbol, next_state in suffix.transitions.items():
                if (symbol not in state.transitions and
                            suffix != self._zero_state):
                    state.transitions[symbol] = next_state
