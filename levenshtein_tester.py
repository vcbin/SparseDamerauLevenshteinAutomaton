#!/usr/bin/env python
# -*- coding: utf-8 -*-


import codecs
import locale
import sys
from levenshtein_test import *


# # this will cause the backend codec decode error if put into levenshtein_test.py directly
# Wrap sys.stdout into a StreamWriter to allow writing unicode.
# ref:
# http://stackoverflow.com/questions/4545661/unicodedecodeerror-when-redirecting-to-file
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(
    sys.stdout)  # only for python 2.x


# test that the two automata are equivalent
# let's hope that they are not both broken in the same way

words = ["banana", "bananas", "cabana", "foobarbazfoobarbaz",
         "a", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", ""]

for n in [0, 1, 2, 3, 4]:
    for word in words:
        dense = LevenshteinAutomaton(word, n)
        sparse = SparseLevenshteinAutomaton(word, n)
        for query in words:
            s_dense = dense.start()
            s_sparse = sparse.start()
            indices, values = s_sparse
            # print "%s\t(%s,%s)" % (s_dense, indices, values)
            # if len(word) and len(query):
            # assert state_equal(s_dense,  s_sparse)
            if word == "banana" and query == "cabana" and n == 2:
                print "      %s" % ", ".join(list(word))
                print "  %s" % s_dense
            # print
            # print "word '%s', query '%s', n = %d" % (word, query, n)
            for c in query:
                s_dense = dense.step(s_dense, c)
                s_sparse = sparse.step(s_sparse, c)
                if len(word) and len(query):
                    assert state_equal(dense_state=s_dense,
                                       sparse_state=s_sparse)
                # assert dense.is_match(s_dense) == sparse.is_match(s_sparse)
                # assert dense.can_match(s_dense) == sparse.can_match(s_sparse)
                if word == "banana" and query == "cabana" and n == 2:
                    print c, s_dense


# use the automaton to build a DFA
counter = [0]  # list is a hack for mutable lexical scoping
states = {}
transitions = []
matching = []

print
print "DFA of SparseLevenshteinAutomaton, 'ab', n = 1"
lev = SparseLevenshteinAutomaton("ab", 1)
explore(lev, lev.start(), states, counter, matching, transitions)

transitions.sort(key=lambda (i, j, c): i)

# from graphviz import Digraph
# graphviz.Digraph("SparseLevenshtein_ab_1")
# # to do: add nodes and edges

# output to graphviz
print "digraph G {"
for t in transitions:
    print '%s -> %s [label=" %s "]' % t
for i in matching:
    print '%s [style=filled]' % i
print "}"


# use the automaton to build a DamerauLevenshtein DFA
counter = [0]  # list is a hack for mutable lexical scoping
states = {}
transitions = []
matching = []

print
print "DFA of SparseDamerauLevenshteinAutomaton, 'ab', n = 1"
DL_lev = SparseDamerauLevenshteinAutomaton("ab", 1)
DL_lev.clear_state()
exploreSpaDamLev(DL_lev, DL_lev.start(), states,
                 counter, matching, transitions)

transitions.sort(key=lambda (i, j, c): i)
# output to graphviz

print "digraph G {"
for t in transitions:
    print '%s -> %s [label=" %s "]' % t
for i in matching:
    print '%s [style=filled]' % i
print "}"


# test code goes from here # words = ["sitting", "kitten", "fitting",
# "setting", "fixing", "suprising"]
words = [u"快乐大本营", u"快乐本大营", u"快乐家族", u"快乐购", u"快乐男声", u"快乐中国",
         u"快乐垂钓", u"快乐大本营： 大电影", u"大本营花絮", u"天天向上"]
weights = [0.9, 0.1, 0.6, 0.7, 0.5, 0.4, 0.3, 0.8, 0.75, 0.85]
# query_str = "sitting"
query_str = [u"快乐大本营", u"大本营"]
# n = 2
# print "string:\t%s" % list(word)


print
print "SparseLevenshteinAutomaton test"
for n in [0, 1, 2, 3, 4]:
    # for n in [0, 1, 2]:
    fuzz_match_obj = LevMatch(words, n, weight_list=weights)
    if 0 == n:
        print
        fuzz_match_obj.print_key_value()
    print
    print "lev distance = %d" % n
    for query in query_str:
        fuzz_match_obj.keys(prefix=query,debug_info=True)
        # print
        # print "key list without weights"
        # fuzz_match_obj = LevMatch(words, n)
        # fuzz_match_obj.keys(prefix=query)


print
print "SparseLevenshteinAutomaton test"
for n in [0, 1, 2, 3, 4]:
    # for n in [0, 1, 2]:
    fuzz_match_obj = LevMatch(words, n, weight_list=weights)
    if 0 == n:
        print
        fuzz_match_obj.print_key_value()
    print
    print "lev distance = %d" % n
    for query in query_str:
        fuzz_match_obj.keys(prefix=query)
        # print
        # print "key list without weights"
        # fuzz_match_obj = LevMatch(words, n)
        # fuzz_match_obj.keys(prefix=query)


print
print "LevenshteinAutomaton debug output"
for n in [0, 1, 2, 3, 4]:
    for word in words:
        # print "word '%s'" % word
        dense = LevenshteinAutomaton(word, n)
        sparse = SparseLevenshteinAutomaton(word, n)
        for query in words:
            # print "query '%s'" % query
            s_dense = dense.start()
            assert(len(s_dense) == len(word) + 1)
            s_sparse = sparse.start()
            indices, values = s_sparse
            # print
            # print "%s\t(%s,%s)" % (s_dense, indices, values)
            # if len(word) and len(query):
            # assert state_equal(s_dense,  s_sparse)
            if word == "banana" and query == "cabana" and n == 2:
                print "      %s" % ", ".join(list(word))
                print "  %s" % s_dense
            for i, c in enumerate(query):
                s_dense = dense.step(s_dense, c)
                assert(len(s_dense) == len(word) + 1)
                s_sparse = sparse.step(s_sparse, c)
                # s_dense = dense.step(s_dense, c)
                # assert(len(s_dense) == len(word) + 1)
                # s_sparse = sparse.step(s_sparse, c)
                # print "current s_dense len: %d" % len(s_dense)
                # print "s_dense\ts_sparse" % (s_dense, s_sparse)
                # assert state_equal(dense_state = s_dense, sparse_state = s_sparse)
                # print "word '%s', query '%s', %d:'%s', n = %d" % (word,
                # query, i, c, n)
                indices, values = s_sparse
                # print "%s\t(%s,%s)" % (s_dense, indices, values)
                # print
                # if len(word) and len(query):
                # assert state_equal(dense._prev_state,  sparse._prev_state)
                assert state_equal(s_dense,  s_sparse)
                # assert dense.is_match(s_dense) == sparse.is_match(s_sparse)
                # assert dense.can_match(s_dense) == sparse.can_match(s_sparse)
                if word == "banana" and query == "cabana" and n == 2:
                    print c, s_dense


print
print "DamerauLevenshteinAutomaton debug output"
# let's hope me don't mess up with the indices scheme and the two version
# don't broke in same way
words = ["banana", "anbana", "abnana", "baanna", "abanna", "bananas", "cabana",
         "foobarbazfoobarbaz",
         "a", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", ""]
# words = ["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", ""]
# words = ["banana", "cabana"]


# not working for word 'banana' and query 'baanna' and n = 1,
# since one substring cannot edited twice restriction of optimal string
# alignment algorithm
for n in [0, 1, 2, 3, 4]:
    for word in words:
        # print "word '%s'" % word
        dense = DamerauLevenshteinAutomaton(word, n)
        sparse = SparseDamerauLevenshteinAutomaton(word, n)
        for query in words:
            # print "query '%s'" % query
            s_dense = dense.start()
            dense.clear_state()
            assert(len(s_dense) == len(word) + 1)
            s_sparse = sparse.start()
            sparse.clear_state()
            indices, values = s_sparse
            print
            print "%s\t(%s,%s)" % (s_dense, indices, values)
            # if len(word) and len(query):
            # assert state_equal(s_dense,  s_sparse)
            if word == "banana" and query == "baanna" and n == 1:
                print "      %s" % ", ".join(list(word))
                print "  %s" % s_dense
            for i, c in enumerate(query):
                # new_s_dense = dense.step(s_dense, c, prev_s_dense, prev_c)
                # prev_s_dense = s_dense
                # s_dense = new_s_dense
                # assert(len(s_dense) == len(word) + 1)
                # new_s_sparse = sparse.step(s_sparse, c, prev_s_sparse, prev_c)
                # prev_s_sparse = s_sparse
                # s_sparse = new_s_sparse
                # prev_c = c
                s_dense = dense.step(s_dense, c)
                assert(len(s_dense) == len(word) + 1)
                s_sparse = sparse.step(s_sparse, c)
                # print "current s_dense len: %d" % len(s_dense)
                # print "s_dense\ts_sparse" % (s_dense, s_sparse)
                # assert state_equal(dense_state = s_dense, sparse_state = s_sparse)
                print "word '%s', query '%s', %d:'%s', n = %d" % (word, query, i, c, n)
                indices, values = s_sparse
                print "%s\t(%s,%s)" % (s_dense, indices, values)
                print
                # if len(word) and len(query):
                # assert state_equal(dense._prev_state,  sparse._prev_state)
                assert state_equal(s_dense,  s_sparse)
                # assert dense.is_match(s_dense) == sparse.is_match(s_sparse)
                # assert dense.can_match(s_dense) == sparse.can_match(s_sparse)
                if word == "banana" and query == "baanna" and n == 1:
                    print c, s_dense


# print
# print "DamerauLevenshteinAutomaton debug output"
# words = [u"快乐大本营", u"快乐本大营"]
# # output matrix of 'banana' and 'abanna', have to do it all over again if we don't wrap it as a function
# for n in [0, 1, 2, 3, 4]:
    # for word in words:
        # # print "word '%s'" % word
        # dense = LevenshteinAutomaton(word, n)
        # sparse = SparseLevenshteinAutomaton(word, n)
        # for query in words:
            # # print "query '%s'" % query
            # s_dense = dense.start()
            # assert(len(s_dense) == len(word) + 1)
            # s_sparse = sparse.start()
            # indices, values = s_sparse
            # print
            # print "%s\t(%s,%s)" % (s_dense, indices, values)
            # # if len(word) and len(query):
                    # # assert state_equal(s_dense,  s_sparse)
            # if word == "banana" and query == "cabana" and n == 2:
                # print "      %s" % ", ".join(list(word))
                # print "  %s" % s_dense
            # for i,c in enumerate(query):
                # s_dense = dense.step(s_dense, c)
                # assert(len(s_dense) == len(word) + 1)
                # s_sparse = sparse.step(s_sparse, c)
                # # s_dense = dense.step(s_dense, c)
                # # assert(len(s_dense) == len(word) + 1)
                # # s_sparse = sparse.step(s_sparse, c)
                # # print "current s_dense len: %d" % len(s_dense)
                # # print "s_dense\ts_sparse" % (s_dense, s_sparse)
                # # assert state_equal(dense_state = s_dense, sparse_state = s_sparse)
                # print "word '%s', query '%s', %d:'%s', n = %d" % (word, query, i, c, n)
                # indices, values = s_sparse
                # print "%s\t(%s,%s)" % (s_dense, indices, values)
                # print
                # # if len(word) and len(query):
                    # # assert state_equal(dense._prev_state,  sparse._prev_state)
                # assert state_equal(s_dense,  s_sparse)
                # # assert dense.is_match(s_dense) == sparse.is_match(s_sparse)
                # # assert dense.can_match(s_dense) == sparse.can_match(s_sparse)
                # if word == "banana" and query == "cabana" and n == 2:
                    # print c, s_dense


words = [u"快乐大本营", u"快乐本大营", u"快乐家族", u"快乐购", u"快乐男声", u"快乐中国",
         u"快乐垂钓", u"快乐大本营： 大电影", u"大本营花絮", u"天天向上"]
weights = [0.9, 0.1, 0.6, 0.7, 0.5, 0.4, 0.3, 0.8, 0.75, 0.85]
# query_str = "sitting"
query_str = [u"快乐大本营", u"大本营"]

print
print "DamerauLevenshteinAutomaton test"
for n in [0, 1, 2, 3, 4]:
    # for n in [0, 1, 2]:
    fuzz_match_obj = DamLevMatch(words, n, weight_list=weights)
    if 0 == n:
        print
        fuzz_match_obj.print_key_value()
    print
    print "lev distance = %d" % n
    for query in query_str:
        fuzz_match_obj.keys(prefix=query, debug_info=True)
        # print
        # print "key list without weights"
        # fuzz_match_obj = LevMatch(words, n)
        # fuzz_match_obj.keys(prefix=query)
