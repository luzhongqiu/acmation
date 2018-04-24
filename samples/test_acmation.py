# -*- encoding: utf-8 -*-
from src.acmation import KeywordTree


def test_word():
    acp = KeywordTree()
    acp.add(["more"], meta_data={'id': 1})
    acp.add(["more", "able"], meta_data={'id': 2})
    acp.add(["we", "are"], meta_data={'id': 3})
    acp.add(["are"])
    acp.add(['....'], meta_data={'id': 5})
    acp.finalize()
    content = """we are family, we are more able to .... """
    for i in acp.search(content, cut_word=True, greedy=True):
        print(i)


def test_char():
    acp = KeywordTree()
    acp.add("more", meta_data={'id': 1})
    acp.add("more able", meta_data={'id': 2})
    acp.add("we are", meta_data={'id': 3})
    acp.add("are")
    acp.add('....', meta_data={'id': 5})
    acp.finalize()
    content = """we are family, we are more able to .... """
    for i in acp.search(content, greedy=False):
        print(i)


if __name__ == '__main__':
    test_word()
    print('-' * 30)
    test_char()
