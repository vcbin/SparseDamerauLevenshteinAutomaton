# 使用Damerau-Levenshtein自动机实现字符串模糊查询
 
## 原理

Levenshtein距离公式  
![formulate_levenshtein-distance](https://wikimedia.org/api/rest_v1/media/math/render/svg/f0a48ecfc9852c042382fdc33c19e11a16948e85)

Levenshtein DFA, string=*'ab'*, n = 1  , 深色表示accepting state  
![ab_1](https://s31.postimg.org/6phun6sm3/ab_1.png)  
实际使用的时候不会构建一个这样复杂的匹配所有全部可能状态的DFA，这里仅为举例说明  
  
  输入字符串 *'cabana'*, 匹配目标 *'banana'*, Levenshtein矩阵计算过程如下：
```
      b, a, n, a, n, a                                                                                                      
  [0, 1, 2, 3, 4, 5, 6]
c [1, 1, 2, 3, 3, 3, 3]
a [2, 2, 1, 2, 3, 3, 3]
b [3, 2, 2, 2, 3, 3, 3]
a [3, 3, 2, 3, 2, 3, 3]
n [3, 3, 3, 2, 3, 2, 3]
a [3, 3, 3, 3, 2, 3, 2]

```


Damerau-Levenshtein距离公式  
![formulate_damerau-levenshtein_distance](https://wikimedia.org/api/rest_v1/media/math/render/svg/100d33e8f77df157b4006d39569a1ad31ff9ee10)  
该公式与Levenshtein距离公式的主要区别是加入了一项 ![](https://wikimedia.org/api/rest_v1/media/math/render/svg/af88b142298dbf69c276bf4eae36258b657f3fb3)用来计算相邻两个字符的置换( transposition)

Damerau-Levenshtein DFA, string=*'ab'*, n = 1  , 深色表示accepting state  
![DL_ab_1](https://s31.postimg.org/chmk82rtn/DL_ab_1.png)  
可以看出， 该DFA与纯Levenshtein的主要区别是可以接受 *'ba'* 作为输入。实际使用的时å不会构建一个这样复杂的匹配所有全部可能状态的DFA，这里仅为举例说明  

## 实现细节
  1. 不保存整个矩阵，只保存矩阵当前行(DameruLevenshteinAutomaton还会保存前一行)  
  2. SparseLevenshteinAutomaton和SparseDameruLevenshteinAutomaton类每一行只保存当前小于*max_edit*的矩阵行元素的下标和值, 这样每一次匹配一个输入字符的时候只需要处理最多*2 * max_edit + 1*个元素  
  3. SparseDameruLevenshteinAutomaton实现使ç¨optimal string alignment算法， 该算法的伪码可以参考[wiki](https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance)  
  

## 测试输出
  [本文所述python实现及测试代码](https://github.com/vcbin/SparseDamerauLevenshteinAutomaton)  
DamerauLevenshteinAutomaton测试输出  
```
  SparseLevenshteinAutomaton test                                                                                             
快乐大本营 -> 0.9 
天天向上 -> 0.85
快乐大本营： 大电影 -> 0.8
大本营花絮 -> 0.75
快乐购 -> 0.7
快乐家族 -> 0.6 
快乐男声 -> 0.5 
快乐中国 -> 0.4 
快乐垂钓 -> 0.3 
快乐本大营 -> 0.1 

lev distance = 0
                lev distance 0, time: 0.000234
                '快乐大本è¥' ->         "快乐大本营"    "----"

                lev distance 0, time: 0.000047
                '大本营' ->     "----"


lev distance = 1
                lev distance 1, time: 0.000439
                '快乐大本营' ->         "快乐大本营"    "----"

                lev distance 1, time: 0.000067
                '大本营' ->     "----"


lev distance = 2
        prefix: 快乐大本营, word: 快乐本大营, cur_i: 4, match error count 2
                lev distance 2, time: 0.000830
                '快乐大本营' ->         "快乐大本营"    "----"  "快乐本大营"

        prefix: 大本营, word: 大本营花絮, cur_i: 2, match error count 2
                lev distance 2, time: 0.000134
                '大本营' ->     "----"  "大本营花絮"


lev distance = 3
        prefix: 快乐大本营, word: 快乐本大营, cur_i: 4, match error count 2
        prefix: 快乐大本营, word: 快乐家族, cur_i: 4, match error count 3
        prefix: 快乐大本营, word: 快乐购, cur_i: 4, match error count 3
        prefix: 快乐大本营, word: 快乐男声, cur_i: 4, match error count 3
        prefix: 快乐大本营, word: 快乐中国, cur_i: 4, match error count 3
        prefix: 快乐大本营, word: 快乐垂钓, cur_i: 4, match error count 3
                lev distance 3, time: 0.000943
                '快乐大本营' ->         "快乐大本营"    "----"  "快乐购"        "快乐家族"      "快乐男声"      "快乐中国"      "快乐垂钓"      "快ä¹本大营"

        prefix: 大本营, word: 大本营花絮, cur_i: 2, match error count 2
                lev distance 3, time: 0.000144
                '大本营' ->     "----"  "大本营花絮"


lev distance = 4
        prefix: 快乐大本营, word: 快乐本大营, cur_i: 4, match error count 2
        prefix: 快乐大本营, word: 快乐家族, cur_i: 4, match error count 3
        prefix: 快乐大本营, word: 快乐购, cur_i: 4, match error count 3
        prefix: 快乐大本营, word: 快乐男声, cur_i: 4, match error count 3
        prefix: 快乐大本营, word: 快乐中国, cur_i: 4, match error count 3
        prefix: 快乐大本营, word: 快乐垂钓, cur_i: 4, match error count 3
                lev distance 4, time: 0.000998
                '快乐大本营' ->         "快乐大本营"    "----"  "快乐购"        "快乐家族"      "快乐男声"      "快乐中国"      "快乐垂钓"      "快乐本大营"

        prefix: 大本营, word: 大本营花絮, cur_i: 2, match error count 2
                lev distance 4, time: 0.000148
                '大本营' ->     "----"  "大本营花絮"

```


DamerauLevenshteinAutomaton测试输出  
```
DamerauLevenshteinAutomaton test                                                                                                                  

快乐大本营 -> 0.9
天天向上 -> 0.85
快乐大本营： 大电影 -> 0.8
大本营花絮 -> 0.75
快乐购 -> 0.7
快乐家族 -> 0.6
快乐男声 -> 0.5
快乐中国 -> 0.4
快乐å钓 -> 0.3
快乐本大营 -> 0.1

lev distance = 0
                lev distance 0, time: 0.000271
                '快乐大本营' ->         "快乐大本营"    "----"

                lev distance 0, time: 0.000051
                '大本营' ->     "----"


lev distance = 1
        prefix: 快乐大本营, word: 快乐本大营, cur_i: 4, match error count 1
                lev distance 1, time: 0.000553
                '快乐大本营' ->         "快乐大本营"    "----"  "快乐本大营" 

                lev distance 1, time: 0.000076
                '大本营' ->     "----"


lev distance = 2
        prefix: 快乐大本营, word: 快乐本大营, cur_i: 4, match error count 1
                lev distance 2, time: 0.000786
                'å¿«乐大本营' ->         "快乐大本营"    "----"  "快乐本大营" 

        prefix: 大本营, word: 大本营花絮, cur_i: 2, match error count 2
                lev distance 2, time: 0.000146
                '大本营' ->     "----"  "大本营花絮" 


lev distance = 3
        prefix: 快乐大本营, word: 快乐本大营, cur_i: 4, match error count 1
        prefix: 快乐大本营, word: 快乐家族, cur_i: 4, match error count 3
        prefix: 快乐大本营, word: 快乐购, cur_i: 4, match error count 3
        prefix: 快乐大本营, word: 快乐男声, cur_i: 4, match error count 3
        prefix: 快乐大本营, word: 快乐中国, cur_i: 4, match error count 3
        prefix: 快乐大本营, word: 快乐垂钓, cur_i: 4, match error count 3
                lev distance 3, time: 0.001079
                '快乐大本营' ->         "快乐大本营"    "----"  "快乐购"        "快乐家族"      "快乐男声"      "快乐中国"      "快乐垂钓"      "快乐本大营"

        prefix: 大本营, word: 大本营花絮, cur_i: 2, match error count 2
                lev distance 3, time: 0.000155
                '大本营' ->     "----"  "大本营花絮"
                   
                   
lev distance = 4
        prefix: 快乐大本营, word: 快乐本大营, cur_i: 4, match error count 1
        prefix: 快乐大本营, word: 快乐家族, cur_i: 4, match error count 3
        prefix: 快乐大本营, word: 快乐购, cur_i: 4, match error count 3
        prefix: 快ä¹大本营, word: 快乐男声, cur_i: 4, match error count 3
        prefix: 快乐大本营, word: 快乐中国, cur_i: 4, match error count 3
        prefix: 快乐大本营, word: 快乐垂钓, cur_i: 4, match error count 3
                lev distance 4, time: 0.001142
                '快乐大本营' ->         "快乐大本营"    "----"  "快乐购"        "快乐家族"      "快乐男声"      "快乐中国"      "快乐垂钓"      "快乐本大营"

        prefix: 大本营, word: 大本营花絮, cur_i: 2, match error count 2
                lev distance 4, time: 0.000160
                '大本营' ->     "----"  "大本营花絮"


```



# 参考文献
[Levenshtein automata can be simple and fast](http://julesjacobs.github.io/2015/06/17/disqus-levenshtein-simple-and-fast.html)  
[Levenshtein_distance](https://en.wikipedia.org/wiki/Levenshtein_distance)  
[Damerau–Levenshtein distance](https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance) 
