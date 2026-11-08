# Wordle Solver

## A Python-based [Wordle](https://www.nytimes.com/games/wordle/index.html) Solver using constraint-based candidate filtering 

## How to Run:

### Pre-build:

    uv sync

### Game:

    uv run main.py

### Tests:

    uv run python -m pytest

## Candidate Filtering

### Как работает Candidate Filtering

Алгоритм *Candidate Filtering*, реализован следующим образом:

1. На вход подаются `guess` и `feedback` параметры. 
2. Эти данные преобразуются в словарь где ключом выступает буква из `guess`, а по ключу в словаре сохраняются значения `feedback` для этой буквы, вместе с индексами, объединённые в список.
3. Полученный словарь преобразуется в ограничения: описываются индексы, где буква точно должна быть, где буква точно быть не может, и какое кол-во букв минимально и максимально допустимо в словах.
4. Полученные ограничения применяются на кандидатах, отсеивая недопустимые слова.

### FAQ

**Вопрос 1.** Почему нельзя фильтровать кандидатов только через проверку *letter in word*?

> Потому что тогда алгоритм не будет учитывать некоторые краевые случаи, например дубликаты. В ситуациях, когда есть информация об отсутствии *и* присутствии символа, необходимо это учитывать явно ограничивая количество допустимых символов. 

**Вопрос 2.** Почему *Solver* не должен иметь доступ к скрытому ответу игрового движка?

> Так как это ведёт к логической ошибке: для чего нам вообще алгоритм отбора кандидатов, если мы можем **сразу** возвращать ответ?

**Вопрос 3.** Какова вычислительная сложность фильтрации одного наблюдения, если у нас \(N\) кандидатов, а длина слова фиксирована и равна пяти?

> Получается **O(5*n)** так как нужно проверить *каждого* кандидата потенциально для *каждого* ограничения букв.

## Frequency Strategy

### Как работает Frequency Strategy

Алгоритм *Frequency Strategy* основан на подсчёте частот **уникальных букв** каждого слова в выбранном наборе кандидатов:

1. Алгоритм разбивает кандидатов на **неповторяющееся** множество букв.
2. Для каждой буквы считается частота нахождения этой буквы в наборе кандидатов. При том, если буква находится несколько раз, то считается только **одно** её вхождение.
3. Полученное число для каждой буквы из слова суммируется с числами других букв **этого слова**.
4. В итоге получается `score` конкретного кандидата.
5. В полученном списке `scores` вычисляется максимумальное значение `score`, с учётом **лексикографического tie-breaking**.

### Benchmark

| COUNT | TIME (ms) |
| ----- | --------- |
| 10    |    0.03   |
| 100   |    0.22   |
| 200   |    0.89   |
| 500   |    1.07   |
| 1000  |    2.56   |
| 1500  |    3.85   |
| 2000  |    4.67   |
| 2500  |    6.13   |
| 3000  |    8.64   |
| 3500  |    7.87   | 
| 4000  |    11.18  |
| 4500  |    10.36  |
| 5000  |    11.68  |

### FAQ

**Вопрос 1.** Почему повторяющиеся буквы *не* должны приносить дополнительный `score` в нашей частотной модели?

> Потому что текущая модель основывается на уникальных буквах **текущих кандидатов**, в противном случае повторное начисление очков бы искусственно завысило оценку этого слова.

**Вопрос 2.** Почему выбор самого частотного слова *не* гарантирует минимального количества попыток до победы?

> Потому что главная цель алгоритма это каждый шаг урезать как можно большее количество слов, при этом оставляя победное. А если выбирать каждый раз слово с самой большей частотностью, то это не поможет убрать максимальное кол-во слов.

**Вопрос 3.** Если число кандидатов равно \(N\), какова временная сложность `select_guess()` при фиксированной длине слова? Можно ли её улучшить?

> Для начала считается `score_words` для набора \(N\) кандидатов с итоговой сложностью O\(5\*N\). После идёт выбор максимума из полученного списка в за O\(N\). Суммируя эти сложности получается O\(N\). Benchmark это подверждает.

## Entropy Strategy

### Как работает Entropy Strategy

Алгоритм *Entropy Strategy* основан на выборе ответа с **максимальной энтропией** в выбранном наборе кандидатов:

1. Алгоритм вычисляет `feedback` для всего набора кандидатов принимая каждого кандидата за ответ, тем самым разбивая набор кандидатов на подгруппы, имеющих одинаковое значение `feedback`.
2. Для полученной группы оцениваем *вероятность* нахождения путём деления кол-ва членнов в группе на общее кол-во кандидатов.
3. По полученным вероятностям считаем *энтропию Шеннона* и ищем в нём кандидата с **максимальной энтропией**, учитывая **лексикографический tie-breaking**.
4. Полученный кандидат и является самым лучшим ходом.

### Benchmark

#### Win-Rate Benchmark Comparison

#### Benchmark parameters: 

1. Loops count: 100
2. Word count: 1000


| Metric                   | Frequency                 | Entropy          |
| ------------------------ | ------------------------- | ---------------- |
| Win Rate %               | 98.0                      | 100.0            |
| Avg. Attempts (wins)     | 3.439                     | 3.26             |
| Failures                 | 2                         | 0                |
| Mean Decision Time (s)   | 0.00108                   | 1.60399          |
| Maximum Attempts (wins)  | 6                         | 6                |
| Minimum Attempts (wins)  | 2                         | 2                |
| Total Benchmark Time (s) | 0.79150                   | 523.30018        | 
| Lost Words               | `mases`, `lazes`          | -                |


#### Performance Benchmark Comparison

| Word Count | Frequency | Entropy   | Delta words | Frequency | Entropy | Delta words^2 | 
| ---------- | --------- | --------- | ----------- | --------- | ------- | ------------- |
| 10         | 0.0001    | 0.0007    | -           | -         | -       | -             |
| 20         | 0.0001    | 0.0024    | x2          | x1        | x3.42   | x4            |
| 50         | 0.0002    | 0.0137    | x2.5        | x2        | x5.71   | x6.25         |
| 100        | 0.0006    | 0.0617    | x2          | x3        | x4.5    | x4            |
| 250        | 0.0010    | 0.3222    | x2.5        | x1.67     | x5.22   | x6.25         |   
| 500        | 0.0019    | 1.3212    | x2          | x1.9      | x4.1    | x4            |
| 1000       | 0.0052    | 5.3679    | x2          | x2.74     | x4.06   | x4            |
| 2000       | 0.0089    | 22.7194   | x2          | x1.71     | x4.23   | x4            |
| 3000       | 0.0135    | 49.5733   | x1.5        | x1.52     | x2.18   | x2.25         |
| 4000       | 0.0160    | 84.6703   | x1.33       | x1.19     | x1.71   | x1.7689       |
| 5000       | 0.0199    | 140.3017  | x1.25       | x1.24     | x1.65   | x1.5625       |


### FAQ

**Вопрос 1.** Почему энтропия хода может быть высокой, даже если само слово имеет сравнительно низкий **Frequency Score**?

> Энтропия и частотность слова это показатели, которые оценивают разные характеристики. Энтропия оценивает то, на сколько групп слово разделит группу кандидатов и их вероятности, а **Frequency Score** частоту конкретных букв. Несмотря на то, что на практике эти значения могут кореллировать, они не взаимосвязаны.

**Вопрос 2.** Почему энтропия равна нулю, когда все возможные ответы дают одну и ту же комбинацию `feedback`?

> Потому что энтропия показывает неопределённость в ответах на попытку. Если все ответы имеют один и тот же `feedback`, это значит что они формируют одну и ту же группу, т.е. никакого разделения не происходит.

**Вопрос 3.** Какова временная сложность твоего `select_guess()` при \(N\) кандидатах и фиксированной длине слова? Обоснуй результат анализом циклов.

> Цикл проходит по каждому кандидату и потом относительно каждого кандидата по всей группе кандидатов заново и собирает для каждого кандидата `feedback`. Потенциально у нас для \(N\) кандидатов может быть \(N\) разных `feedback`, а соответственно и \(N\) групп. Для каждой группы вычисляются частоты за O\(N\). Получается целая проходка за O\(N^2\) для группы из \(N\) кандидатов. Это наблюдение подтверждает Performance Benchmark (с поправкой на погрешности измерений), на нём видно что с увеличением числа слов в `Delta Words` раз время для **Frequency** возрастает линейно, а для **Entropy** квадратично.

**Вопрос 4.** Почему стратегия с максимальной энтропией не обязательно минимизирует среднее число ходов до победы?

> **EntropyStrategy** оптимизирует ожидаемое количество информации от текущего хода, но не моделирует будущую последовательность решений, непосредственную победу и ограничение в шесть попыток.

## Probe Guess Strategy

### Как работает Probe Guess Strategy

Алгоритм *Probe Guess Strategy* основан на *Entropy Strategy*, однако может выбрать слово не из выбранного набора кандидатов \(N\), а всего словаря \(G\) (набор кандидатов \(N\) выбирается из всего словаря игры \(G\)).:

1. Алгоритм вычисляет энтропию для каждого слова из всего словаря \(G\), относительно набора кандидатов \(N\) по алгоритму *Entropy Strategy*.
2. Из полученного списка энтропий выбирается слово с максимальным значением для набора кандидатов \(N\).
3. Если максимальная энтропия достигается на кандидате из \(N\), то в приоритете выбирается именно он, так как имеет шанс быть победным словом.
4. Также учитывается **лексикографический tie-breaking** если варианты для выбора принадлежат одной категории.
5. Полученное слово и является самым лучшим ходом.

### Benchmark

#### Win-Rate Benchmark Comparison

#### Benchmark parameters: 

1. Loops count: 25
2. Word count: 1000


| Metric                   | Probe Guess               | Entropy          |
| ------------------------ | ------------------------- | ---------------- |
| Win Rate %               | 100.0                     | 100.0            |
| Avg. Attempts (wins)     | 3.28                      | 3.48             |
| Failures                 | 0                         | 0                |

<details>

<summary> Game History: </summary>


    . Iteration #1

    Started entropy game
    max: tores 5.980848758455358 candidates_len: 1000
    max: dries 1.9219280948873623 candidates_len: 5
    max: fries 1.0 candidates_len: 2

    Started probe game
    max: tores 5.980848758455358 is in candidates: True candidates_len: 1000
    max: biped 2.321928094887362 is in candidates: False candidates_len: 5
    max: fries as a single candidate

    ! Iteration #2

    Started entropy game
    max: rates 6.086528301712345 candidates_len: 1000
    max: drawn 3.3660913291191923 candidates_len: 19
    max: foray 2.0 candidates_len: 4
    max: moray as a single candidate

    Started probe game
    max: rates 6.086528301712345 is in candidates: True candidates_len: 1000
    max: nomad 3.616348566075164 is in candidates: False candidates_len: 19
    max: moray as a single candidate

    . Iteration #3

    Started entropy game
    max: reals 5.964535927120791 candidates_len: 1000
    max: dines 3.2373008763572906 candidates_len: 32
    max: yikes 1.8423709931771084 candidates_len: 7
    max: bikes 1.0 candidates_len: 2

    Started probe game
    max: reals 5.964535927120791 is in candidates: True candidates_len: 1000
    max: twink 3.715018266288633 is in candidates: False candidates_len: 32
    max: baggy 1.584962500721156 is in candidates: False candidates_len: 3
    max: bikes as a single candidate

    ! Iteration #4

    Started entropy game
    max: rates 6.033247664682525 candidates_len: 1000
    max: loped 4.036979817890861 candidates_len: 38
    max: mixed 2.521640636343318 candidates_len: 7
    max: miked 1.0 candidates_len: 2
    max: mined as a single candidate

    Started probe game
    max: rates 6.033247664682525 is in candidates: True candidates_len: 1000
    max: doily 4.175430473912968 is in candidates: False candidates_len: 38
    max: miked 2.5 is in candidates: True candidates_len: 8
    max: mined 1.0 is in candidates: True candidates_len: 2

    Iteration #5

    Started entropy game
    max: saner 5.908004756867642 candidates_len: 1000
    max: blend 2.94770277922009 candidates_len: 9
    max: eking as a single candidate

    Started probe game
    max: saner 5.908004756867642 is in candidates: True candidates_len: 1000
    max: build 3.169925001442312 is in candidates: False candidates_len: 9
    max: eking as a single candidate

    Iteration #6

    Started entropy game
    max: tales 6.043444571762888 candidates_len: 1000
    max: ranks 3.0363722498302232 candidates_len: 19
    max: gauss 1.584962500721156 candidates_len: 3
    max: sagos as a single candidate

    Started probe game
    max: tales 6.043444571762888 is in candidates: True candidates_len: 1000
    max: drunk 3.431623565847431 is in candidates: False candidates_len: 19
    max: hasps 1.0 is in candidates: True candidates_len: 2
    max: sagos as a single candidate

    ! Iteration #7

    Started entropy game
    max: saner 5.93852728182673 candidates_len: 1000
    max: miles 3.040120474355139 candidates_len: 34
    max: pokes 2.5 candidates_len: 8
    max: gyves 1.0 candidates_len: 2
    max: tuxes as a single candidate

    Started probe game
    max: saner 5.93852728182673 is in candidates: True candidates_len: 1000
    max: moult 3.7711426205984724 is in candidates: False candidates_len: 34
    max: tuxes as a single candidate

    Iteration #8

    Started entropy game
    max: tears 6.010108529367174 candidates_len: 1000
    max: durst 2.0 candidates_len: 4

    Started probe game
    max: tears 6.010108529367174 is in candidates: True candidates_len: 1000
    max: durst 2.0 is in candidates: True candidates_len: 4

    - Iteration #9

    Started entropy game
    max: tares 6.062133021315155 candidates_len: 1000
    max: mania 3.7849418274376427 candidates_len: 21
    max: labia as a single candidate

    Started probe game
    max: tares 6.062133021315155 is in candidates: True candidates_len: 1000
    max: inlay 3.8208888513501886 is in candidates: False candidates_len: 21
    max: cavil 1.0 is in candidates: True candidates_len: 2
    max: labia as a single candidate

    Iteration #10

    Started entropy game
    max: tales 6.086917905503734 candidates_len: 1000
    max: molly 2.94770277922009 candidates_len: 9
    max: bulgy 1.0 candidates_len: 2
    max: bulky as a single candidate

    Started probe game
    max: tales 6.086917905503734 is in candidates: True candidates_len: 1000
    max: molly 2.94770277922009 is in candidates: True candidates_len: 9
    max: bulgy 1.0 is in candidates: True candidates_len: 2
    max: bulky as a single candidate

    Iteration #11

    Started entropy game
    max: tales 6.039596442769538 candidates_len: 1000
    max: apter as a single candidate

    Started probe game
    max: tales 6.039596442769538 is in candidates: True candidates_len: 1000
    max: apter as a single candidate

    Iteration #12

    Started entropy game
    max: tares 6.101703594861504 candidates_len: 1000
    max: husky 3.9321380397593746 candidates_len: 19
    max: soppy 1.0 candidates_len: 2

    Started probe game
    max: tares 6.101703594861504 is in candidates: True candidates_len: 1000
    max: husky 3.9321380397593746 is in candidates: True candidates_len: 19
    max: soppy 1.0 is in candidates: True candidates_len: 2

    Iteration #13

    Started entropy game
    max: tales 5.95358064584962 candidates_len: 1000
    max: spout 3.913977073182752 candidates_len: 22
    max: hoist 1.0 candidates_len: 2

    Started probe game
    max: tales 5.95358064584962 is in candidates: True candidates_len: 1000
    max: spout 3.913977073182752 is in candidates: True candidates_len: 22
    max: hoist 1.0 is in candidates: True candidates_len: 2

    Iteration #14

    Started entropy game
    max: rites 5.927817233803383 candidates_len: 1000
    max: taupe 3.4182958340544896 candidates_len: 12
    max: abate 1.0 candidates_len: 2

    Started probe game
    max: rites 5.927817233803383 is in candidates: True candidates_len: 1000
    max: taupe 3.4182958340544896 is in candidates: True candidates_len: 12
    max: abate 1.0 is in candidates: True candidates_len: 2

    Iteration #15

    Started entropy game
    max: reals 6.036453148366545 candidates_len: 1000
    max: tense 2.584962500721156 candidates_len: 6
    max: pesto as a single candidate

    Started probe game
    max: reals 6.036453148366545 is in candidates: True candidates_len: 1000
    max: tense 2.584962500721156 is in candidates: True candidates_len: 6
    max: pesto as a single candidate

    Iteration #16

    Started entropy game
    max: tores 6.0550466941162515 candidates_len: 1000
    max: domes 1.780672129520887 candidates_len: 12
    max: cones 1.6644977792004612 candidates_len: 7

    Started probe game
    max: tores 6.0550466941162515 is in candidates: True candidates_len: 1000
    max: nymph 2.584962500721156 is in candidates: False candidates_len: 12
    max: cones 1.0 is in candidates: True candidates_len: 2

    ! Iteration #17

    Started entropy game
    max: tares 6.131644471817727 candidates_len: 1000
    max: elude 4.3119357556115485 candidates_len: 43
    max: bedim 1.0 candidates_len: 2
    max: decoy as a single candidate

    Started probe game
    max: tares 6.131644471817727 is in candidates: True candidates_len: 1000
    max: cloud 4.515537790545582 is in candidates: False candidates_len: 43
    max: decoy as a single candidate

    - Iteration #18

    Started entropy game
    max: cares 6.0327849706027905 candidates_len: 1000
    max: hatch 2.6464393446710157 candidates_len: 10
    max: yacht as a single candidate

    Started probe game
    max: cares 6.0327849706027905 is in candidates: True candidates_len: 1000
    max: humph 2.9219280948873623 is in candidates: False candidates_len: 10
    max: nacho 1.0 is in candidates: True candidates_len: 2
    max: yacht as a single candidate

    - Iteration #19

    Started entropy game
    max: tares 6.215207637591103 candidates_len: 1000
    max: gists 3.3680424225727155 candidates_len: 21
    max: mists 1.0 candidates_len: 2

    Started probe game
    max: tares 6.215207637591103 is in candidates: True candidates_len: 1000
    max: lisps 3.6897037321995474 is in candidates: False candidates_len: 21
    max: dogma 1.584962500721156 is in candidates: False candidates_len: 3
    max: mists as a single candidate

    . Iteration #20

    Started entropy game
    max: tares 6.15442847661791 candidates_len: 1000
    max: heats 0.9182958340544896 candidates_len: 3
    max: neats 1.0 candidates_len: 2

    Started probe game
    max: tares 6.15442847661791 is in candidates: True candidates_len: 1000
    max: alpha 1.584962500721156 is in candidates: False candidates_len: 3
    max: neats as a single candidate

    Iteration #21

    Started entropy game
    max: dares 5.969266427965037 candidates_len: 1000
    max: abbes 1.0 candidates_len: 2
    max: agues as a single candidate

    Started probe game
    max: dares 5.969266427965037 is in candidates: True candidates_len: 1000
    max: abbes 1.0 is in candidates: True candidates_len: 2
    max: agues as a single candidate

    Iteration #22

    Started entropy game
    max: tares 6.074323265964096 candidates_len: 1000
    max: karts as a single candidate

    Started probe game
    max: tares 6.074323265964096 is in candidates: True candidates_len: 1000
    max: karts as a single candidate

    ! Iteration #23

    Started entropy game
    max: roles 5.839898686340553 candidates_len: 1000
    max: malls 2.5232314287976205 candidates_len: 15
    max: calls 0.8112781244591328 candidates_len: 4
    max: galls 0.9182958340544896 candidates_len: 3
    max: halls 1.0 candidates_len: 2
    max: palls as a single candidate

    Started probe game
    max: roles 5.839898686340553 is in candidates: True candidates_len: 1000
    max: sumac 3.1898980954642875 is in candidates: False candidates_len: 15
    max: aping 1.584962500721156 is in candidates: False candidates_len: 3
    max: palls as a single candidate

    Iteration #24

    Started entropy game
    max: dares 6.002163062388353 candidates_len: 1000
    max: noisy 4.193429088311724 candidates_len: 35
    max: scuff 1.584962500721156 candidates_len: 3
    max: shuck as a single candidate

    Started probe game
    max: dares 6.002163062388353 is in candidates: True candidates_len: 1000
    max: noisy 4.193429088311724 is in candidates: True candidates_len: 35
    max: scuff 1.584962500721156 is in candidates: True candidates_len: 3
    max: shuck as a single candidate

    ! Iteration #25

    Started entropy game
    max: tares 6.151423945429748 candidates_len: 1000
    max: riped 3.23345859334435 candidates_len: 32
    max: boyer 3.084962500721156 candidates_len: 12
    max: bower 1.0 candidates_len: 2
    max: boxer as a single candidate

    Started probe game
    max: tares 6.151423945429748 is in candidates: True candidates_len: 1000
    max: bingo 3.5664280318460246 is in candidates: False candidates_len: 32
    max: alway 1.584962500721156 is in candidates: False candidates_len: 3
    max: boxer as a single candidate

</details>

#### Description:

> Я провёл опыт из 25 игр бок-о-бок с одинаковыми стартовыми словами и ответами. Ход каждой из игр представлен в **Game History**, а результаты представлены в табличке. </br>
> 1000 слов и всего 25 попыток это слишком нерепрезентативная выборка, чтобы утверждать, какой из алгоритмов лучше или хуже, несмотря даже на отличающиеся параметры средних попыток. Куда интереснее история игр и принятые решения. </br>
> Я ввёл условные обозначения для того чтобы можно было быстро обратить внимание и подчеркнуть какое было различие в партиях: </br>
> Нет обозначений - обе игры либо полностью одинаково по ответам, либо за одинаковое количество ходов, при разных ответах. </br>
> Точкой (.) я обозначил игры в которых **Probe Guess** оставил на последнем ходу единственного кандидата, в отличие от **Entropy Strategy**. При этом кол-во ходов одинаковое. </br>
> Восклицательный знак (!) - **Probe Guess** справился за меньшее кол-во ходов. </br>
> Минус (-) - **Probe Guess** потратил больше ходов.  </br>
> На примере игры #2 видна разница этих алгоритмов. Первый ход одинаковый, но уже на втором ходу **Probe Guess** решает выбрать слово `nomad` с большей энтропией, и не из набора кандидатов, а **Entropy Strategy** выбрал слово `drawn`. Это различие позволило **Probe Guess** на следующем же ходу оставить `moray` как единственного кандидата, что и стало ответом в игре и позволило сэкономить ход. По аналогичному сценарию идут игры с номерами: 4, 7, 17 и 23. </br>
> Также отличается игра #9. На втором ходу **Probe Guess** выбрало слово с большей энтропией чем **Entropy Strategy**, но так вышло что слово ход **Entropy Strategy** оставил лишь единственного кандидата `labia`, что и является правильным ответом, в то время как ход **Probe Guess** разделил на 2 кандидата с одинаковой энтропией в 1 бит. Там уже в игру вступил **tie-breaking**, поэтому на 3 ходу был выбран `cavil`, а не `labia`. По аналогичному сценарию идут игры 18 и 19. </br>
> Остальные партии по своей сути очень схожи. Хоть и принятые `guess` у них разные, в обоих стратегиях одинаковый исход по разделению кандидатов. </br>
> В общем и целом, по такому тесту можно заключить, что ситуации, где **Probe Guess** тратит лишний ход можно, но 25 партий из 1000 слов это всё же мало для того, чтобы утверждать что он мене эффективный, чем **Entropy Strategy**. Однако также, стоит подметить, что среднее кол-во ходов у **Probe Guess** меньше, и партий в которых он превзошёл **Entropy Strategy** на 2 больше, что и повлияло на среднее кол-во ходов. </br>

#### Performance Benchmark Comparison

| Word Count | Candidates Count | Entropy   | Probe Guess | Delta Candidates | Delta Words | Total Delta | Time Delta For Probe |
| ---------- | ---------------- | --------- | ----------- | ---------------- | ----------- | ----------- | -------------------- |
| 10         | 10               | 0.0006    | 0.0006      | -                | -           | -           | -                    |
| 100        | 10               | -//-      | 0.0054      | x1               | x10         | x10         | x9                   |
| 100        | 25               | 0.0035    | 0.0134      | x2.5             | x1          | x2.5        | x2.48                |
| 100        | 50               | 0.0133    | 0.0257      | x2               | x1          | x2          | x1.91                |


### FAQ

**Вопрос 1.** Почему попытка, которой нет среди `possible_answers`, может иметь большую энтропию, чем любой из оставшихся кандидатов?

> Потому что алгоритм оценивает все возможные слова по энтропии, в следствие чего может возникнуть ситуация, когда слово из всего словаря более информативно, чем любой кандидат. Такой случай представлен в тесте `test_probe_guess_over_candidates`.

**Вопрос 2.** Почему при равной энтропии разумно предпочесть слово, которое может быть правильным ответом?

> Потому что тогда есть вероятность, что это слово окажется победным, что позволит сократить количество ходов.

**Вопрос 3.** Какова сложность **ProbeEntropyStrategy** при \(N\) возможных ответах и \(G\) допустимых попытках? Что произойдёт с производительностью, если \(G\) станет в десять раз больше?

> Алгоритм вычисляет энтропию для каждого слова из всего словаря \(G\), относительно набора кандидатов \(N\). Получается цикл вычислений для каждого слова из \(G\) вычисляется энтропия всех кандидатов \(N\). Получается O\(G*N\). Это подтверждает **Performance Benchmark**: при увеличении \(G\), а \(N\) зафиксировать, то и время увеличится линейно, аналогично и обратная ситуация, когда \(N\) меняется, а \(G\) нет, и тоже время увеличивается линейно в delta\(N\) раз.

**Вопрос 4.** Допустим, осталась одна попытка до поражения, а **ProbeEntropyStrategy** предлагает слово вне `candidates`, обладающее максимальной энтропией. Почему следовать этому выбору было бы ошибкой?

> То, что алгоритм не учитывает кол-во оставшихся попыток является серьёзным недостатком. В описанной ситуации выбирать слово вне `candidates` на последней попытке приведёт к гарантированному поражению. Несмотря на то, что это слово будет более информативно, чем любой из кандидатов, выйгрыш важнее, но алгоритм этого не учитывает.