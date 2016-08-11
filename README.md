
 
## 用途
   文本模糊匹配，例如搜索引擎Lucene 从4.0版本开始就[使用了LevenshteinAutomaton对用户输入的搜索字符进行模糊查询](http://blog.mikemccandless.com/2011/03/lucenes-fuzzyquery-is-100-times-faster.html)
 
 
## 原理
### Levenshtein 距离
  计算用户输入字符串和索引字符串之间的[编辑距离](https://en.wikipedia.org/wiki/Edit_distance), 最常用的是Levenshtein距离。基于Levenshtein距离的模糊匹配允许用户即使输入的查询字符串与匹配的目标字符串存在*n*个字符的插入/删除/替换 差异， 匹配仍然能够成功。 例如，  索引字符串 *'ab'* 的匹配Levenshtein距离为1的全部DFA状态转移图如下 ,  其中深色表示accepting state  
  ![ab_1](https://s31.postimg.org/6phun6sm3/ab_1.png)  
实际使用的时候不一会构建一个这样复杂的匹配所有全部可能状态的[DFA](https://en.wikipedia.org/wiki/Deterministic_finite_automaton)，这里为举例说明  

Levenshtein距离公式  
![formulate_levenshtein-distance](https://wikimedia.org/api/rest_v1/media/math/render/svg/f0a48ecfc9852c042382fdc33c19e11a16948e85)  
  ![](https://wikimedia.org/api/rest_v1/media/math/render/svg/bdc0315678caad28648aafedb6ebafb16bd1655c)表示字符串*a*的前*i*个字符与字符串*b*的前*j*个字符的Levenshtein距离， min函数对应的第一项表示从*a[i]* 删除最后一个字符时的情况， 第二项表示从插入一个字符的情况， 第3项表示替换， 即*a[i]*与*b[j]*匹配或者不匹配时候的情况  
  例如， 输入字符串 *'cabana'*, 匹配目标 *'banana'*, Levenshtein矩阵计算过程如下：
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

### Damerau-Levenshtein 距离
Damerau-Levenshtein距离公式  
![formulate_damerau-levenshtein_distance](https://wikimedia.org/api/rest_v1/media/math/render/svg/100d33e8f77df157b4006d39569a1ad31ff9ee10)  
该公式与Levenshtein距离公式的主要区别是加入了一项 ![](https://wikimedia.org/api/rest_v1/media/math/render/svg/af88b142298dbf69c276bf4eae36258b657f3fb3)用来计算相邻两个字符的置换( transposition)

Damerau-Levenshtein DFA, string=*'ab'*, n = 1  , 深色表示accepting state  
![DL_ab_1](https://s31.postimg.org/chmk82rtn/DL_ab_1.png)  
可以看出， 该DFA与纯Levenshtein的主要区别是可以接受 *'ba'* 作为输入。实际使用的时候不一定会构建一个这样复杂的匹配所有全部可能状态的DFA，这里仅为举例说明  

## 与其它算法相比的优缺点
### 与[*trie*](https://zh.wikipedia.org/wiki/Trie)比较
缺点
  1. 字符串匹配速度较[*marisa trie*](https://pypi.python.org/pypi/marisa-trie])慢， 匹配时的时间复杂度里面包括索引数量项，而*trie*树一旦构建完成就与索引数量无关搜索速度只与最大索引**长度**有关
  2. 自动机前缀匹配结果远不如*trie*， 例如输入‘快乐’无法匹配到‘快乐大本营’， 因为这两个字符串相差3个字符，而实际使用时一般最多设置编辑距离为2.  
  
优点
  1. 容错，支持模糊查询，DamerauLevenshtein还支持匹配任意两个相邻字符换位后的结果，非常适合用来做拼写检查以及语义分析

### 与[*KMP算法*](http://blog.csdn.net/v_july_v/article/details/7041827)比较
优点
  1. 本文实现的*SparseDamerauLevenshtein*速度比[*KMP*](https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm)算法快，时间复杂度为_M * N * C_, 其中*M*为索引数量， *N*为输入的搜索字符串长度， *C*为设定的最大编辑距离，一般为*1*或者*2*. 而*Kmp*算法时间复杂度为_N + M * avg_len_, 其中*avg_len*为平均索引长度， *N*是需要匹配前先计算的，由于一般搜索时输入的字符串不会太长，这一项开销可以忽略不计。综上， 比较*SparseDamerauLevenshtein*和*KMP*的时间复杂度实际上就是比较_M * N_和_M * avg_len_的复杂度。由于*N*一般都小于索引的平均长度*avg_len*, 所以**实际用于自动完成或者前缀搜索时 *SparseDamerauLevenshtein* 比 *KMP* 算法快**。
  
缺点
  1. **前后缀搜索效果均不如*KMP***(Trie树只能搜索前缀, 基于编辑距离的匹配算法在两个字符串长度相差较大时无能为力)， **尤其是用户输入的搜索字符串较短时.**

## 实现细节
  SparseLevenshteinAutomaton的实现基于[github repo](https://github.com/julesjacobs/levenshtein),  本文实现与该repo相比的主要区别是  
  1.  jules jacobs的实现主要是simple *proof of concept*, 本文的实现是一个包含了测试代码，提供了隐藏了具体实现细节、包括完整字符串模糊匹配接口的wrapper class  
  2.  **扩展**了jules jacobs实现的功能。 本文实现了基于Damerau-Levenshtein距离的Sparse Damerau-Levenshtein Automaton, 可以识别任意相邻两个字符置换/换位后的字符串, 提供了state_equal等验证空间压缩版本的Sparse Automaton功能正确性的检验函数。
 
  实现细节  
  1. 不保存整个Levenshtein距离矩阵，只保存矩阵当前行(DameruLevenshteinAutomaton会保存矩阵的前一行作为内部状态， 而LevenshteinAutomaton类不直接保存任何状态)  
  2. SparseLevenshteinAutomaton和SparseDameruLevenshteinAutomaton类每一行只保存当前小于*max_edit*的矩阵行元素的下标和值, 这样每一次匹配一个输入字符的时候只需要处理最多*2 \* max_edit + 1*个元素, 使得匹配单个字符的时间复杂度由*Length(string) *  下降为***c***, 其中*Length(string)*为索引字符串长度,*c*为最大编辑距离，一般可忽略, 从而使得整个算法变得实际可用
  3. SparseDameruLevenshteinAutomaton实现使用optimal string alignment算法， 该算法的伪码来自[wiki](https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance)  
  ![optimal_string_alignment_pseudocode](https://s31.postimg.org/4fq21jfcb/optimal_string_alignment_pseudocode.png)
  

## 测试输出
  [本文所述python实现github](https://github.com/vcbin/SparseDamerauLevenshteinAutomaton), 其中包括[字符串模糊匹配类定义及实现文件](https://github.com/vcbin/SparseDamerauLevenshteinAutomaton/blob/master/levenshtein_test.py)，
  [测试代码文件](https://github.com/vcbin/SparseDamerauLevenshteinAutomaton/blob/master/levenshtein_tester.py),   [测试输出文件](https://github.com/vcbin/SparseDamerauLevenshteinAutomaton/blob/master/test_run_out)  
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
                '快乐大本营' ->         "快乐大本营"    "----"

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
                '快乐大本营' ->         "快乐大本营"    "----"  "快乐购"        "快乐家族"      "快乐男声"      "快乐中国"      "快乐垂钓"      "快乐本大营"

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
快乐垂钓 -> 0.3
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
                '快乐大本营' ->         "快乐大本营"    "----"  "快乐本大营" 

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
        prefix: 快乐大本营, word: 快乐男声, cur_i: 4, match error count 3
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
