#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ref
# http://julesjacobs.github.io/2015/06/17/disqus-levenshtein-simple-and-fast.html
class LevenshteinAutomaton(object):

    def __init__(self, string, n, weight=1.0):
        self.string = string
        self.max_edits = n
        self.weight = weight

    def get_string(self):
        return self.string

    def get_n(self):
        return self.n

    def get_weight(self):
        return self.weight

    def start(self):
        return range(len(self.string) + 1)

    def step(self, state, c):
        new_state = [state[0] + 1]
        for i in range(len(state) - 1):
            cost = 0 if self.string[i] == c else 1
            new_state.append(
                min(new_state[i] + 1, state[i] + cost, state[i + 1] + 1))
        return [min(x, self.max_edits + 1) for x in new_state]

    def is_match(self, state):
        return state[-1] <= self.max_edits

    def can_match(self, state):
        return min(state) <= self.max_edits

    def match_error(self, state):
        return state[-1]

    def transitions(self, state):
        return set(c for (i, c) in enumerate(self.string) if state[i] <= self.max_edits)


class SparseLevenshteinAutomaton(object):

    def __init__(self, string, n, weight=1.0):
        self.string = string
        self.max_edits = n
        self.weight = weight

    def get_string(self):
        return self.string

    def get_n(self):
        return self.n

    def get_weight(self):
        return self.weight

    def start(self):
        return (range(self.max_edits + 1), range(self.max_edits + 1))
        # return (range(min(self.max_edits, len(self.string)) + 1),
        # range(min(self.max_edits, len(self.string) + 1)))

    def step(self, (indices, values), c):
        if indices and indices[0] == 0 and values[0] < self.max_edits:
            new_indices = [0]
            new_values = [values[0] + 1]
        else:
            new_indices = []
            new_values = []

        for j, i in enumerate(indices):
            if i == len(self.string):
                break
            cost = 0 if self.string[i] == c else 1
            val = values[j] + cost
            if new_indices and new_indices[-1] == i:
                val = min(val, new_values[-1] + 1)
            if j + 1 < len(indices) and indices[j + 1] == i + 1:
                val = min(val, values[j + 1] + 1)
            if val <= self.max_edits:
                new_indices.append(i + 1)
                new_values.append(val)

        return (new_indices, new_values)

    def is_match(self, (indices, values)):
        return bool(indices) and indices[-1] == len(self.string)

    def can_match(self, (indices, values)):
        return bool(indices)

    def match_error(self, state):
        return state[1][-1]  # state is tuple of (key_list, value_list)

    def transitions(self, (indices, values)):
        return set(self.string[i] for i in indices if i < len(self.string))


def explore(lev, state, states,
            counter, matching, transitions):
    # lists can't be hashed in Python because they are mutable, so convert to
    # a tuple
    key = (tuple(state[0]), tuple(state[1]))
    if key in states:
        return states[key]
    i = counter[0]
    counter[0] += 1
    states[key] = i
    if lev.is_match(state):
        matching.append(i)
    for c in lev.transitions(state) | set(['*']):
        newstate = lev.step(state, c)
        j = explore(lev, newstate, states, counter, matching, transitions)
        transitions.append((i, j, c))
    return i


def state_equal(dense_state,  sparse_state):
        # print type(dense_s), type(sparse_state)
    indices, values = sparse_state
    # print type(indices), type(values)
    assert(len(indices) == len(values))
    # print indices, values
    sparse_len = len(indices)
    for i in range(sparse_len):
                # print "i %d, indices[i] %d, len(dense_s) %d, len(values) %d" \
                    # % (i, indices[i], len(dense_s), len(values))
        assert(indices[i] < len(dense_state))
        if values[i] != dense_state[indices[i]]:
            # print "len(dense_state)= %d" % len(dense_state)
            print
            print "%s\t(%s, %s)" % (dense_state, indices, values)
            return False
    return True


class DamerauLevenshteinAutomaton(LevenshteinAutomaton):
    ''' # ref https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance'''

    def __init__(self, word, n, state=[], c=u""):
        super(DamerauLevenshteinAutomaton, self).__init__(word, n)
        self._prev_state = state
        self._prev_c = c

    # def step(self, state, c, prev_state, prev_c):
        # '''simple implementation of Optimal string alignment distance algorithm of wikipedia
        # the optimal string alignment algorithm computes the number of edit operations needed to make the strings equal under the condition that NO SUBSTRING is EDITED MORE THAN ONCE
        # Note that for the optimal string alignment distance,
        # the triangle inequality does not hold: OSA(CA,AC) + OSA(AC,ABC) < OSA(CA,ABC), and so it is not a true metric.'''
        # assert(state)
        # if prev_state:
        # assert(len(prev_state) == len(state))
        # new_state = [state[0] + 1]
        # for i in range(len(state) - 1):
        # cost = 0 if self.string[i] == c else 1
        # cur_min = min(new_state[i] + 1, state[i] + cost, state[i + 1] + 1)
        # # print
        # # print ("prev_state= %s\t, i= %d, c='%s', prev_c='%s', self.string='%s'" % (prev_state, i, c, prev_c, self.string))
        # if prev_state and len(prev_c) and i > 0 and \
        # self.string[i - 1] == c and self.string[i] == prev_c:
        # # cost == 0 when c == prev_c == self.string[i] == self.string[i - 1]
        # # assert (prev_state)
        # # print
        # # print ("prev_state= %s\t, i= %d, c='%s', prev_c='%s', self.string='%s'" % (prev_state, i, c, prev_c, self.string))
        # cur_min = min(cur_min, prev_state[i - 1] + cost)
        # new_state.append(cur_min)

        # assert(len(new_state) == len(self.string) + 1)
        # res_state = [min(x, self.max_edits + 1) for x in new_state]
        # # print "len(prev_state): %d\t%s\t%s" % (len(prev_state), prev_state, prev_c)
        # # print "len(res_state)= %d\t%s\t%s" % (len(res_state), res_state, c)
        # # print
        # return res_state

    def step(self, state, c):
        '''simple implementation of Optimal string alignment distance algorithm of wikipedia
        the optimal string alignment algorithm computes the number of edit operations needed to make the strings equal under the condition that NO SUBSTRING is EDITED MORE THAN ONCE
        Note that for the optimal string alignment distance,
        the triangle inequality does not hold: OSA(CA,AC) + OSA(AC,ABC) < OSA(CA,ABC), and so it is not a true metric.'''
        assert(state)
        prev_state = self._prev_state
        if prev_state:
            assert(len(prev_state) == len(state))
        prev_c = self._prev_c
        new_state = [state[0] + 1]
        for i in range(len(state) - 1):
            cost = 0 if self.string[i] == c else 1
            cur_min = min(new_state[i] + 1, state[i] + cost, state[i + 1] + 1)
            # print
            # print ("prev_state= %s\t, i= %d, c='%s', prev_c='%s', self.string='%s'" % (prev_state, i, c, prev_c, self.string))
            if prev_state and len(prev_c) and i > 0 and \
               self.string[i - 1] == c and self.string[i] == prev_c:
                    # cost == 0 when c == prev_c == self.string[i] == self.string[i - 1]
                    # assert (prev_state)
                    # print
                    # print ("prev_state= %s\t, i= %d, c='%s', prev_c='%s', self.string='%s'" % (prev_state, i, c, prev_c, self.string))
                cur_min = min(cur_min, prev_state[i - 1] + cost)
            new_state.append(cur_min)

        assert(len(new_state) == len(self.string) + 1)
        res_state = [min(x, self.max_edits + 1) for x in new_state]
        self._prev_state = state
        self._prev_c = c
        # print "len(prev_state): %d\t%s\t%s" % (len(prev_state), prev_state, prev_c)
        # print "len(res_state)= %d\t%s\t%s" % (len(res_state), res_state, c)
        # print

        return res_state

    def clear_state(self):
        """clear internal previous state and previous query character variables
        :returns: None

        """
        self._prev_state = []
        self._prev_c = u""


class SparseDamerauLevenshteinAutomaton(SparseLevenshteinAutomaton):
    """SparseDamerauLevenshteinAutomaton implemented by optimal string alignment algorithm
    Note that this class is NOT thread safe"""

    def __init__(self, word, n, state=([], []), c=u""):
        super(SparseDamerauLevenshteinAutomaton, self).__init__(word, n)
        self._prev_state = state
        self._prev_c = c

    # def step(self, (indices, values), c, (prev_indices, prev_values), prev_c):
        # if indices and indices[0] == 0 and values[0] < self.max_edits:
        # new_indices = [0]
        # new_values = [values[0] + 1]
        # else:
        # new_indices = []
        # new_values = []

        # for j, i in enumerate(indices):
        # if i == len(self.string):
        # break
        # cost = 0 if self.string[i] == c else 1
        # val = values[j] + cost
        # if new_indices and new_indices[-1] == i:
        # val = min(val, new_values[-1] + 1)
        # if j + 1 < len(indices) and indices[j + 1] == i + 1:
        # val = min(val, values[j + 1] + 1)

        # # print
        # # print ("prev_state=(%s, %s)\ti= %d, j= %d\t\t, prev_c='%s', c='%s'\tself.string='%s'" % (prev_indices, prev_values, i, j, prev_c, c, self.string))
        # if prev_indices and \
        # i > 0 and  i < len(self.string) and \
        # self.string[i - 1] == c and self.string[i] == prev_c:
        # idx = None
        # for k, l in enumerate(prev_indices):
        # if l == i - 1:
        # idx = k
        # break
        # assert(idx is not None)
        # val = min(val, prev_values[idx] + cost)
        # # print
        # # print ('''prev_state=(%s, %s)\ti= %d, j= %d\t
        # # idx = %d, prev_values[idx]= %d, cost= %d, val= %d\tprev_c=\'%s\', c=\'%s\'\tself.string=\'%s\''''
        # # % (prev_indices, prev_values, i, j, idx, prev_values[idx], cost, val,
        # # prev_c, c, self.string))
        # if val <= self.max_edits:
        # new_indices.append(i + 1)
        # new_values.append(val)

        # return (new_indices, new_values)

    def step(self, (indices, values), c):
        if indices and indices[0] == 0 and values[0] < self.max_edits:
            new_indices = [0]
            new_values = [values[0] + 1]
        else:
            new_indices = []
            new_values = []

        prev_state = self._prev_state
        prev_indices, prev_values = prev_state
        prev_c = self._prev_c
        for j, i in enumerate(indices):
            if i == len(self.string):
                break
            cost = 0 if self.string[i] == c else 1
            val = values[j] + cost
            if new_indices and new_indices[-1] == i:
                val = min(val, new_values[-1] + 1)
            if j + 1 < len(indices) and indices[j + 1] == i + 1:
                val = min(val, values[j + 1] + 1)

            # print
            # print ("prev_state=(%s, %s)\tstate=(%s, %s)\ti= %d, j= %d\t\t, prev_c='%s', c='%s'\tself.string='%s'" % (prev_indices, prev_values, indices, values, i, j, prev_c, c, self.string))
            if prev_indices and \
               i > 0 and  i < len(self.string) and \
               self.string[i - 1] == c and self.string[i] == prev_c:
                idx = None
                # look around first
                if j < len(prev_indices) and j >= 0 and prev_indices[j] == i - 1:
                    idx = j
                elif j - 1 < len(prev_indices) and j - 1 >= 0 and prev_indices[j - 1] == i - 1:
                    idx = j - 1
                elif j + 1 < len(prev_indices) and j + 1 >= 0 and prev_indices[j + 1] == i - 1:
                    idx = j + 1
                else:
                    for k, l in enumerate(prev_indices):
                        if l == i - 1:
                            idx = k
                            break
                assert(idx is not None)
                val = min(val, prev_values[idx] + cost)
                # print
                # print ('''prev_state=(%s, %s)\ti= %d, j= %d\t
                # idx = %d, prev_values[idx]= %d, cost= %d, val= %d\tprev_c=\'%s\', c=\'%s\'\tself.string=\'%s\''''
                # % (prev_indices, prev_values, i, j, idx, prev_values[idx], cost, val,
                # prev_c, c, self.string))
            if val <= self.max_edits:
                new_indices.append(i + 1)
                new_values.append(val)

        self._prev_state = (indices, values)
        self._prev_c = c
        return (new_indices, new_values)

    def clear_state(self):
        """clear internal previous state and previous query character variables
        :returns: None

        """
        self._prev_state = ([], [])
        self._prev_c = u""


def exploreSpaDamLev(lev, state,
                     states, counter, matching, transitions):
    # lists can't be hashed in Python because they are mutable, so convert to
    # a tuple
    assert(isinstance(lev, SparseDamerauLevenshteinAutomaton))
    key = (tuple(state[0]), tuple(state[1]))
    if key in states:
        return states[key]
    i = counter[0]
    counter[0] += 1
    states[key] = i
    if lev.is_match(state):
        matching.append(i)
    for c in lev.transitions(state) | set(['*']):
        # lev.clear_state() # this line made DamerauLevenshtein identical to # Levenshtein
        newstate = lev.step(state, c)
        j = exploreSpaDamLev(lev, newstate, states, counter, matching, transitions)
        transitions.append((i, j, c))
    return i


class LevMatch(object):

    def __init__(self, key_list, n, weight_list=[]):
        for i, title in enumerate(key_list):
            if not isinstance(title, unicode):  # only work for python 2.x
                assert(isinstance(title, str))
                # convert to unicode object, not working
                key_list[i] = title.decode('utf-8')
        self._key_list = key_list
        self._n = n
        self._weight_list = weight_list
        if weight_list:
            self._word_weight_d = dict(zip(key_list, weight_list))

    def print_key_value(self):
        if (any(self._word_weight_d)):
            from collections import OrderedDict
            word_weight_ord_d = OrderedDict(sorted(self._word_weight_d.items(), key=lambda t: t[
                1], reverse=True))  # sorted by weight for display
            for k, v in word_weight_ord_d.items():
                print "%s -> %s" % (k, repr(v).decode("unicode-escape"))

    def items(self):
        return self._word_weight_d.items()

    def keys(self, prefix=u"", top_n=10, debug_info=False):
        '''time complexity: $M * N * n$ where $M$ is the total index count and $N$
        is the query string length, and $n$ is the maximum DamerauLevenshtein distance'''
        if (not len(prefix)):
            return self._key_list
        # print "prefix=%s , len = %d" % ( prefix, len(prefix))
        words = self._key_list
        words_lev_l = [SparseLevenshteinAutomaton(
            word, self._n) for word in words]
        words_lev_d = dict(zip(words, words_lev_l))
        exact_match_res_l = []
        fuzzy_match_res_l = []
        from timeit import default_timer as timer
        start_t = timer()
        for word in words:
            if len(word) and len(prefix) and (
                (len(prefix) == 1 and prefix[0] != word[0]) or
                    (len(word) > 1 and prefix[0] !=
                     word[0] and prefix[1] != word[1])
            ):
                continue  # it is unlikely that the first two input characters are misspelled
            if word == prefix:
                exact_match_res_l.append(word)
                continue
            cur_lev_state = words_lev_d[word].start()
            for i, cur_c in enumerate(prefix):
                cur_lev_state = words_lev_d[word].step(cur_lev_state, cur_c)
                # new_lev_state = words_lev_d[word].step(
                # cur_lev_state, cur_c, prev_lev_state, prev_c)
                # prev_lev_state = cur_lev_state
                # cur_lev_state = new_lev_state
                # prev_c = cur_c
                if not words_lev_d[word].can_match(cur_lev_state):
                    break
                # print " ",cur_lev_state

            if words_lev_d[word].is_match(cur_lev_state):
                # if words_lev_d[word].can_match(cur_lev_state): # NOT correct cause this potentially match a COMPLETELY different/irrelevent word
                # print cur_lev_state
                err_num = words_lev_d[word].match_error(cur_lev_state)
                # print "%s\t%s" % (type(err_num),err_num)
                # print "%s, match error char count: %d" % (type(err_num),
                # err_num)
                if (len(word) == len(prefix) and not err_num):
                    exact_match_res_l.append(word)
                else:
                    if debug_info:
                        print "\tprefix: %s, word: %s, cur_i: %d, match error count %d" % ("".join(prefix), word, i, err_num)
                    fuzzy_match_res_l.append(word)

        if (exact_match_res_l or fuzzy_match_res_l) and self._weight_list:
            import heapq

            def get_weight(word_weight_d, key):
                return word_weight_d[key]
            from functools import partial
            bound_get_weight = partial(get_weight, self._word_weight_d)
            exact_match_res_l = list(heapq.nlargest(
                top_n, exact_match_res_l, key=bound_get_weight))
            fuzzy_match_res_l = list(heapq.nlargest(
                top_n, fuzzy_match_res_l, key=bound_get_weight))
            # exact_match_res_lst = list(heapq.nlargest(
            # top_n, exact_match_res_l, key=lambda key: word_weight_d[key]))
            # fuzzy_match_res_lst = list(heapq.nlargest(
            # top_n, fuzzy_match_res_l, key=lambda key:
            # word_weight_d[key]))
        if debug_info:
            sep_str_l = [u"----"]
        else:
            sep_str_l = []
        res_l = exact_match_res_l + sep_str_l + fuzzy_match_res_l
        elapsed_t = timer() - start_t
        # import sys
        # res_out = repr([x.encode(sys.stdout.encoding) for x in exact_match_res_l + fuzzy_match_res_l]).decode('string-escape')
        # res_out = repr(res_l).decode('unicode-escape')
        if debug_info:
            print "\t\tlev distance %d, time: %f" % (self._n, elapsed_t)
            # print "\t\tmatch result:\t%s" % res_out
            print "\t\t'%s' -> \t%s" %  \
                ("".join((prefix)), "\t".join(
                    ['"' + elem + '"' for elem in res_l]))
            print

        return res_l


class DamLevMatch(LevMatch):

    def keys(self, prefix=u"", top_n=10, debug_info=False):
        '''time complexity: $M * N * n$ where $M$ is the total index count and $N$
        is the query string length, and $n$ is the maximum DamerauLevenshtein distance'''
        if (not len(prefix)):
            return self._key_list
        # print "prefix=%s , len = %d" % ( prefix, len(prefix))
        words = self._key_list
        words_lev_l = [SparseDamerauLevenshteinAutomaton(
            word, self._n) for word in words]
        words_lev_d = dict(zip(words, words_lev_l))
        exact_match_res_l = []
        fuzzy_match_res_l = []
        from timeit import default_timer as timer
        start_t = timer()
        for word in words:
            if len(word) and len(prefix) and (
                (len(prefix) == 1 and prefix[0] != word[0]) or
                    (len(word) > 1 and prefix[0] !=
                     word[0] and prefix[1] != word[1])
            ):
                continue  # it is unlikely that the first two input characters are misspelled
            if word == prefix:
                exact_match_res_l.append(word)
                continue
            cur_lev_state = words_lev_d[word].start()
            # prev_lev_state = ([], [])
            # prev_c = u""
            words_lev_d[word].clear_state()
            for i, cur_c in enumerate(prefix):
                cur_lev_state = words_lev_d[word].step(cur_lev_state, cur_c)
                # new_lev_state = words_lev_d[word].step(
                # cur_lev_state, cur_c, prev_lev_state, prev_c)
                # prev_lev_state = cur_lev_state
                # cur_lev_state = new_lev_state
                # prev_c = cur_c
                if not words_lev_d[word].can_match(cur_lev_state):
                    break
                # print " ",cur_lev_state

            if words_lev_d[word].is_match(cur_lev_state):
                # if words_lev_d[word].can_match(cur_lev_state): # NOT correct cause this potentially match a COMPLETELY different/irrelevent word
                # print cur_lev_state
                err_num = words_lev_d[word].match_error(cur_lev_state)
                # print "%s\t%s" % (type(err_num),err_num)
                # print "%s, match error char count: %d" % (type(err_num),
                # err_num)
                if (len(word) == len(prefix) and not err_num):
                    exact_match_res_l.append(word)
                else:
                    if debug_info:
                        print "\tprefix: %s, word: %s, cur_i: %d, match error count %d" % ("".join(prefix), word, i, err_num)
                    fuzzy_match_res_l.append(word)

        if (exact_match_res_l or fuzzy_match_res_l) and self._weight_list:
            import heapq

            def get_weight(word_weight_d, key):
                return word_weight_d[key]
            from functools import partial
            bound_get_weight = partial(get_weight, self._word_weight_d)
            exact_match_res_l = list(heapq.nlargest(
                top_n, exact_match_res_l, key=bound_get_weight))
            fuzzy_match_res_l = list(heapq.nlargest(
                top_n, fuzzy_match_res_l, key=bound_get_weight))
            # exact_match_res_lst = list(heapq.nlargest(
            # top_n, exact_match_res_l, key=lambda key: word_weight_d[key]))
            # fuzzy_match_res_lst = list(heapq.nlargest(
            # top_n, fuzzy_match_res_l, key=lambda key:
            # word_weight_d[key]))
        if debug_info:
            sep_str_l = [u"----"]
        else:
            sep_str_l = []
        res_l = exact_match_res_l + sep_str_l + fuzzy_match_res_l
        elapsed_t = timer() - start_t
        # import sys
        # res_out = repr([x.encode(sys.stdout.encoding) for x in exact_match_res_l + fuzzy_match_res_l]).decode('string-escape')
        # res_out = repr(res_l).decode('unicode-escape')
        if debug_info:
            print "\t\tlev distance %d, time: %f" % (self._n, elapsed_t)
            # print "\t\tmatch result:\t%s" % res_out
            print "\t\t'%s' -> \t%s" %  \
                ("".join((prefix)), "\t".join(
                    ['"' + elem + '"' for elem in res_l]))
            print

        return res_l
