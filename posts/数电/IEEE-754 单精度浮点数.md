# IEEE-754 单精度浮点数笔记整理

## 1. 为什么需要 IEEE-754？

计算机底层只能存储二进制数据，也就是 0 和 1。整数可以比较直接地转成二进制，但小数的表示会复杂很多。

👉 [打开 IEEE 754 单精度浮点数转换器](/blog-md/tools/float32-converter.html)

重要概念：

| **中文**      | **Français**                     | **English**                            |
|---------------|----------------------------------|----------------------------------------|
| IEEE-754 标准 | norme IEEE-754                   | IEEE-754 standard                      |
| 浮点数        | nombre à virgule flottante       | floating-point number                  |
| 单精度浮点数  | nombre flottant simple précision | single-precision floating-point number |
| 双精度浮点数  | nombre flottant double précision | double-precision floating-point number |
| 二进制        | binaire                          | binary                                 |

## 2. 单精度浮点数的 32 位结构

单精度浮点数，也就是很多语言里的 float，占用 **32 bit**。这 32 位被分成三个部分：

![IEEE-754 图示](https://img.lxxsfile.org/assets/632a1f34e1541baa6082d04785f4fe02ada23650de82f42ffd47459c55fac05b.png)

| **部分**        | **位数** | **作用**                            | **Français**        |
|-----------------|----------|-------------------------------------|---------------------|
| 符号位 sign     | 1 bit    | 表示正负，0 为正，1 为负            | bit de signe        |
| 指数位 exponent | 8 bit    | 表示数值的尺度，也就是 2 的多少次方 | Exposant            |
| 尾数位 fraction | 23 bit   | 表示有效数字，也决定精度            | fraction / mantisse |

整体可以理解为：

一个浮点数 = 符号 × 有效数字 × 2 的指数次方

更接近标准写法：

```plaintext
value = (-1)^sign × significand × 2^exponent
```

重要概念：

| **中文** | **Français**           | **English**         |
|----------|------------------------|---------------------|
| 符号位   | bit de signe           | sign bit            |
| 指数位   | exposant               | exponent            |
| 尾数位   | fraction / mantisse    | fraction / mantissa |
| 有效数字 | chiffres significatifs | significant digits  |
| 位       | bit                    | bit                 |

## 3. 偏移量：为什么指数要加 127？

单精度浮点数的指数位有 8 位，可以表示 0 ~ 255。但真实指数可能是负数，例如 2^-3。

为了避免直接存储负指数，IEEE-754 使用了 **偏移量**：

存储指数 = 真实指数 + 偏移量

对于单精度浮点数：

```plaintext
bias = 127
```

所以：

```plaintext
stored exponent = real exponent + 127
real exponent = stored exponent - 127
```

例如真实指数是 3：

```plaintext
stored exponent = 3 + 127 = 130
```

130 转成二进制是：

```plaintext
10000010
```

重要概念：

| **中文** | **Français**             | **English**     |
|----------|--------------------------|-----------------|
| 偏移量   | biais                    | bias            |
| 真实指数 | exposant réel            | real exponent   |
| 存储指数 | exposant stocké          | stored exponent |
| 阶码     | exposant / exposant réel | exponent        |

## 4. 例子：8.5 如何存成单精度浮点数？

![IEEE-754 图示](https://img.lxxsfile.org/assets/bff6a65502f11463937bed9c63e7627dfff83a33f82f76ba54229294d3fc5b0b.png)

以十进制数 8.5 为例。

#### 第一步：确定符号位

8.5 是正数，所以符号位是：

```plaintext
0
```

#### 第二步：转成二进制

整数部分：

```plaintext
8 = 1000
```

小数部分：

```plaintext
0.5 = 0.1
```

所以：

```plaintext
8.5 = 1000.1₂
```

关于小数如何转化成二进制（我们用0.6875来举例）：

![IEEE-754 图示](https://img.lxxsfile.org/assets/19a76485fb2ed4a033cc6b4ec4e009b73a55f09145f54952492a0074852fd39e.png)

![IEEE-754 图示](https://img.lxxsfile.org/assets/c7fe46e6ee24387fffb1887e24241cf2d4ed9c5363c3c6b70bb8da625bed8027.png)

#### 第三步：规格化

把小数点移动到第一个 1 后面：

```plaintext
1000.1₂ = 1.0001₂ × 2^3
```

![IEEE-754 图示](https://img.lxxsfile.org/assets/7d7b9a747071ea96419f38a722440206d53b96f35ac9f85c6e28d6dba7be2143.png)

![IEEE-754 图示](https://img.lxxsfile.org/assets/49021390962052f31a192df4ace151063dd3c1fdc2e4edac870ea85d2c3a297e.png)

所以真实指数是：

```plaintext
3
```

存储指数是：

```plaintext
3 + 127 = 130
```

二进制为：

```plaintext
10000010
```

#### 第四步：处理尾数位

规格化结果是：

```plaintext
1.0001
```

![IEEE-754 图示](https://img.lxxsfile.org/assets/554c7e1642c5db7e5375e90208ff52cbf7de2acec952bfaddacb710caecd3bf9.png)

对于规格数，最前面的 1. 是默认存在的，不需要存储，这叫做 **隐藏位**。

所以真正存入尾数位的是：

```plaintext
0001
```

尾数位一共 23 位，不足的部分在后面补 0：

```plaintext
00010000000000000000000
```

#### 最终结果

![IEEE-754 图示](https://img.lxxsfile.org/assets/7ac8037a7a3c58d22497a322394f747cb597181e83412a5352bab3fc129e1b29.png)

重要概念：

| **中文** | **Français**              | **English**   |
|----------|---------------------------|---------------|
| 规格化   | normalisation             | normalization |
| 隐藏位   | bit implicite / bit caché | hidden bit    |
| 尾数补零 | remplissage par zéros     | zero padding  |

## 5. 规格数、非规格数和特殊值

IEEE-754 的单精度浮点数可以分成三大类：

1. 规格数 normal number
2. 非规格数 subnormal number
3. 特殊值 special values

### 5.1 规格数

当指数位既不全为 0，也不全为 1 时，这个数就是 **规格数**。

```plaintext
exponent: 00000001 ~ 11111110
```

规格数的有效数字形式是：

```plaintext
1.xxxxx
```

这里的 1. 是隐藏的，不存入 fraction。

重要概念：

| **中文** | **Français**     | **English**   |
|----------|------------------|---------------|
| 规格数   | nombre normalisé | normal number |
| 隐含的 1 | 1 implicite      | implicit 1    |
| 有效数字 | significande     | significand   |

### 5.2 非规格数

当指数位全为 0 时，这个数是 **非规格数**。

```plaintext
exponent = 00000000
```

非规格数不再隐藏 1.，而是使用：

```plaintext
0.xxxxx
```

它的作用是表示非常接近 0 的数，让浮点数从最小规格数到 0 之间有一个更平滑的过渡。

这个机制叫：

逐渐下溢 / gradual underflow

重要概念：

| **中文** | **Français**                     | **English**       |
|----------|----------------------------------|-------------------|
| 非规格数 | nombre dénormalisé / sous-normal | subnormal number  |
| 逐渐下溢 | sous-dépassement graduel         | gradual underflow |
| 下溢     | sous-dépassement                 | underflow         |

### 5.3 特殊值：Infinity 和 NaN

当指数位全为 1 时，就是特殊值。

```plaintext
exponent = 11111111
```

然后根据尾数位区分：

| **指数位** | **尾数位** | **含义** |
|------------|------------|----------|
| 全 1       | 全 0       | Infinity |
| 全 1       | 不全为 0   | NaN      |

#### Infinity

- +Infinity 正无穷
- -Infinity 负无穷

它通常出现在浮点数上溢，或者某些除以 0 的浮点运算中。

#### NaN

NaN 表示：

Not a Number

也就是“不是一个数”。

常见情况：

```plaintext
0.0 / 0.0
sqrt(-1)
Infinity - Infinity
```

重要概念：

| **中文** | **Français**           | **English**        |
|----------|------------------------|--------------------|
| 正无穷   | infini positif         | positive infinity  |
| 负无穷   | infini négatif         | negative infinity  |
| 非数     | pas un nombre          | NaN / Not a Number |
| 特殊值   | valeurs spéciales      | special values     |
| 上溢     | dépassement / overflow | overflow           |

## 6. 单精度浮点数为什么会丢失精度？

单精度浮点数只有 23 位 fraction，但规格数还会隐含一个 1，所以有效二进制位数大约是：

24 bit

这意味着它不能精确表示所有整数和小数。

例如：

```plaintext
16777216 = 2^24
```

这个数可以被单精度浮点数精确表示。

但是：

```plaintext
16777217 = 2^24 + 1
```

在单精度浮点数中无法精确表示，通常会被舍入成：

```plaintext
16777216
```

因为在这个数量级上，相邻两个可表示浮点数之间的间隔已经变成了 2。

所以：

- 16777216 可以表示
- 16777217 不能精确表示
- 16777218 可以表示

重要概念：

| **中文**       | **Français**                  | **English**            |
|----------------|-------------------------------|------------------------|
| 精度丢失       | perte de précision            | loss of precision      |
| 舍入           | arrondi                       | rounding               |
| 可表示数       | nombre représentable          | representable number   |
| 相邻浮点数间隔 | écart entre flottants voisins | floating-point spacing |
| 机器精度       | précision machine             | machine precision      |

## 7. 浮点数间隔

浮点数不是连续的。它们更像是一组离散的点。

在某些范围内，两个相邻浮点数之间的距离很小；但数值越大，相邻浮点数之间的距离也会变大。

例如单精度浮点数中：

| **范围附近**        | **相邻浮点数间隔** |
|---------------------|--------------------|
| 1 ~ 2               | 约 2^-23           |
| 8388608 ~ 16777215  | 1                  |
| 16777216 ~ 33554430 | 2                  |
| 更大的范围          | 间隔继续增大       |

这就是为什么大整数用 float 存储时会出现精度问题。

重要概念：

| **中文**   | **Français**                     | **English**                |
|------------|----------------------------------|----------------------------|
| 浮点数间隔 | espacement des nombres flottants | floating-point spacing     |
| 离散值     | valeurs discrètes                | discrete values            |
| 连续小数   | nombres décimaux continus        | continuous decimal numbers |
| 近似表示   | représentation approximative     | approximate representation |

## 8. 为什么单精度大约只有 7 位十进制有效数字？

单精度浮点数的有效二进制位数约为 24 位。

因为：

```plaintext
2^24 = 16777216
```

而：

```plaintext
10^7 < 16777216 < 10^8
```

所以单精度浮点数大约能保证 **7 位十进制有效数字**。

注意，这里的“7 位有效数字”不是指只能存 7 位数字，而是指在发生舍入或精度丢失时，通常只能可靠保证大约 7 位十进制有效数字。

重要概念：

| **中文**       | **Français**                    | **English**                |
|----------------|---------------------------------|----------------------------|
| 十进制有效数字 | chiffres significatifs décimaux | decimal significant digits |
| 二进制有效位   | bits significatifs binaires     | binary significant bits    |
| 可靠精度       | précision fiable                | reliable precision         |

## 9. Java 中的常见表现

在 Java 里：

```java
float f = 16777217f;
System.out.println(f);
```

输出可能是：

```plaintext
1.6777216E7
```

也就是：

```plaintext
16777216
```

因为 16777217 无法被 float 精确表示。

另外：

```java
Float.NaN == Float.NaN
```

结果是：

```plaintext
false
```

判断 NaN 应该使用：

```java
Float.isNaN(x)
```

重要概念：

| **中文**   | **Français**                   | **English**                    |
|------------|--------------------------------|--------------------------------|
| 比较浮点数 | comparer des nombres flottants | compare floating-point numbers |
| NaN 判断   | test de NaN                    | NaN check                      |
| 误差范围   | marge d’erreur                 | error tolerance                |

## 10. 学习时最重要的总结

IEEE-754 单精度浮点数可以这样记：

1 位符号位 + 8 位指数位 + 23 位尾数位

核心理解：

浮点数不是精确存储所有小数，而是在有限 bit 内近似表示数值。

最重要的几个点：

| **重点**                    | **解释**               |
|-----------------------------|------------------------|
| float 只有 32 bit           | 存储空间有限           |
| 指数决定范围                | 能表示多大或多小的数   |
| 尾数决定精度                | 能表示得多细           |
| bias 是 127                 | 用来存储正负指数       |
| 规格数隐藏 1.               | 节省 1 bit 精度        |
| 非规格数隐藏 0.             | 用于表示接近 0 的小数  |
| Infinity 和 NaN 是特殊值    | 用于表示溢出或非法结果 |
| float 约 7 位十进制有效数字 | 超过后可能发生精度丢失 |
| 浮点数有间隔                | 数值越大，间隔越大     |

## 11. 法语术语速查表

| **中文**   | **Français**                     | **English**            |
|------------|----------------------------------|------------------------|
| 浮点数     | nombre à virgule flottante       | floating-point number  |
| 单精度     | simple précision                 | single precision       |
| 双精度     | double précision                 | double precision       |
| 符号位     | bit de signe                     | sign bit               |
| 指数       | exposant                         | exponent               |
| 尾数       | mantisse / fraction              | mantissa / fraction    |
| 有效数字   | chiffres significatifs           | significant digits     |
| 偏移量     | biais                            | bias                   |
| 规格化     | normalisation                    | normalization          |
| 规格数     | nombre normalisé                 | normal number          |
| 非规格数   | nombre dénormalisé / sous-normal | subnormal number       |
| 隐藏位     | bit implicite / bit caché        | hidden bit             |
| 正无穷     | infini positif                   | positive infinity      |
| 负无穷     | infini négatif                   | negative infinity      |
| 非数       | pas un nombre                    | Not a Number           |
| 精度丢失   | perte de précision               | loss of precision      |
| 舍入       | arrondi                          | rounding               |
| 上溢       | dépassement                      | overflow               |
| 下溢       | sous-dépassement                 | underflow              |
| 逐渐下溢   | sous-dépassement graduel         | gradual underflow      |
| 浮点数间隔 | espacement des nombres flottants | floating-point spacing |
