# -*- encoding: utf-8 -*-
from src.acmation import acmation

def test_acmation():
    key = [(1, ["a"]), (2, ["bc"]), (3, ["bcf"]), (4, ["cfg"]), (5, ["life"]), (6, ["your", "life"]),
           (7, ["something"]), (8, ["more", "able", "to"]), (9, ["your"])]  # 创建模式串
    acp = acmation()
    for k, v in key:
        acp.insert(k, v)  # 添加模式串
    acp.ac_automation()
    text = """ I have a house,  your life will be better"""

    text = text.split()
    d = acp.runkmp(text)  # 运行自动机
    assert d == {
        1: 1,
        6: 1
    }
