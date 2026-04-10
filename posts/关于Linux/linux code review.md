# Linux 复习资料（小测试之后的内容整理）

这份资料整理的是我们在**小测试之后**继续讨论过的知识点，方便你考试前快速复习。

---

## 1. `cat` 的用法

`cat` 来自 **concatenate**，最常见的作用是：**显示文件内容**。

### 基本用法

```bash
cat 文件名
```

例如：

```bash
cat test.txt
```

会把 `test.txt` 的内容直接显示在终端里。

### 查看多个文件

```bash
cat a.txt b.txt
```

会先显示 `a.txt` 的内容，再显示 `b.txt` 的内容。

### 配合重定向

```bash
cat a.txt > b.txt
```

把 `a.txt` 的内容写入 `b.txt`。

```bash
cat a.txt >> b.txt
```

把 `a.txt` 的内容追加到 `b.txt` 后面。

### 手动输入内容创建文件

```bash
cat > test.txt
```

输入内容后，按 `Ctrl + D` 结束并保存。

### 常见参数

```bash
cat -n test.txt
```

给每一行加行号。

---

## 2. `>` 和 `>>` 的区别

### `>`：覆盖写入

```bash
echo hello > test.txt
```

会把内容写入 `test.txt`，如果文件里原来有内容，会被**清空后重写**。

### `>>`：追加写入

```bash
echo hello >> test.txt
```

会把内容**追加到文件末尾**，不会删除原来的内容。

### 一句话记忆

- `>` ：重新写
- `>>` ：继续写

---

## 3. `<` 和 `<<` 的区别

### `<`：输入重定向

```bash
wc -l < test.txt
```

意思是：让 `wc -l` 从 `test.txt` 读取内容，而不是从键盘读取。

### `<<`：here document

```bash
cat << EOF
hello
world
EOF
```

表示把后面这几行文字作为前面命令的输入。

### 四个符号对比

- `>` ：输出到文件（覆盖）
- `>>` ：输出到文件（追加）
- `<` ：从文件读取输入
- `<<` ：从一段多行文本读取输入

---

## 4. 不用 `nano` 新建 `.txt` 并输入内容

### 方法 1：用 `cat`

```bash
cat > test.txt
```

然后直接输入内容，结束时按 `Ctrl + D`。

### 方法 2：写一行

```bash
echo "hello world" > test.txt
```

### 方法 3：一次写多行

```bash
cat << EOF > test.txt
第一行
第二行
第三行
EOF
```

---

## 5. `factor $RANDOM` 是什么意思

### `$RANDOM`

在 `bash` 里，`$RANDOM` 是一个**随机数变量**，每次取值都会生成一个随机整数。

```bash
echo $RANDOM
```

### `factor`

`factor` 用来做**质因数分解**。

```bash
factor 12
```

输出类似：

```text
12: 2 2 3
```

### 合起来

```bash
factor $RANDOM
```

意思是：

**先生成一个随机整数，再把这个随机整数分解质因数。**

---

## 6. `déplacer / modifier / effacer` 和权限的关系

这三个法语词在 Linux 权限里可以这样理解：

### `modifier`
最接近的是：

```text
w
```

也就是 **write**，写权限。

### `effacer`
删除文件通常不只看文件本身，而更常看**所在目录**有没有权限。
严格说，删除通常和目录的：

```text
w + x
```

有关。

### `déplacer`
移动文件本质上也和目录权限关系更大，通常涉及：

```text
w + x
```

在源目录和目标目录上的权限。

### 简化记忆

- `modifier` → 文件的 `w`
- `effacer` → 目录的 `w + x`
- `déplacer` → 目录的 `w + x`

---

## 7. 这条 loto 命令的意思

```bash
echo $(shuf -n 6 -i 1-49 | sort -n) "chance" $(shuf -n 2 -i 1-10) > tirageLoto.txt
```

### 分解解释

#### `shuf -n 6 -i 1-49`
从 1 到 49 中随机取 6 个数。

#### `| sort -n`
把这 6 个数字按从小到大排序。

#### `$( ... )`
命令替换：先执行括号里的命令，再把结果放回来。

#### `"chance"`
直接输出单词 `chance`。

#### `$(shuf -n 2 -i 1-10)`
从 1 到 10 中随机取 2 个数。

#### `> tirageLoto.txt`
把最终输出写进 `tirageLoto.txt` 文件中。

### 整体意思

这条命令会：

- 随机生成 6 个 1 到 49 的号码
- 再生成 2 个 1 到 10 的 `chance` 号码
- 然后把结果保存到 `tirageLoto.txt`

---

## 8. `mkdir -p`：一行创建父文件夹和子文件夹

### 推荐写法

```bash
mkdir -p parent/enfant
```

意思是：

- 创建 `parent`
- 再在里面创建 `enfant`

如果父目录已经存在，也不会报错。

### 对比

不用 `-p` 时，可以写成：

```bash
mkdir parent && mkdir parent/enfant
```

但考试里更常见也更简洁的是：

```bash
mkdir -p parent/enfant
```

---

## 9. 创建符号链接：`ln -s`

题目：

> 进入 `hutte/coffre`，然后为 `tirageLoto.txt` 创建一个叫 `tirageLotoLien.txt` 的符号链接。

### 做法

```bash
cd ~/Foret/Hutte/Coffre
ln -s tirageLoto.txt tirageLotoLien.txt
```

### 含义

```bash
ln -s 原文件 链接名
```

这里：

- 原文件：`tirageLoto.txt`
- 新链接名：`tirageLotoLien.txt`

### 检查

```bash
ls -l
```

会看到类似：

```text
tirageLotoLien.txt -> tirageLoto.txt
```

说明链接创建成功。

---

## 10. `ln` 和 `ln -s` 的区别

### `ln`

```bash
ln a.txt b.txt
```

创建的是**硬链接**。
可以理解成：给同一个文件再起一个名字。

### `ln -s`

```bash
ln -s a.txt b.txt
```

创建的是**符号链接**（软链接）。
可以理解成：建一个指向原文件的快捷方式。

### 最重要区别

- `ln`：硬链接
- `ln -s`：符号链接

### 简化理解

- 硬链接：像“同一个文件的另一个名字”
- 软链接：像“快捷方式”

---

## 11. `tar czf` 打包压缩目录

题目要求：

> 进入第一题创建的 `Examen_login_date_heure` 目录的父目录，然后把它打包成 `.tar.gz` 文件。

### 命令

```bash
tar czf Examen_login_date_heure.tar.gz Examen_login_date_heure
```

### 参数含义

- `c` = create，创建归档
- `z` = gzip 压缩
- `f` = file，后面跟输出文件名

### 这条命令的意思

把目录：

```text
Examen_login_date_heure
```

压缩成：

```text
Examen_login_date_heure.tar.gz
```

### 为什么要站在父目录执行

因为命令最后写的是目录名：

```bash
Examen_login_date_heure
```

所以你要站在它的上一级目录，才能正确找到它。

### 查看压缩包内容

```bash
tar tzf Examen_login_date_heure.tar.gz
```

这里：

- `t` = list，查看归档内容
- `z` = gzip
- `f` = 文件

---

## 12. 复习时最该记住的几句

### 文件查看与写入

```bash
cat file.txt
echo "hello" > file.txt
echo "hello" >> file.txt
cat > file.txt
```

### 重定向

```bash
command > file
command >> file
command < file
command << EOF
...
EOF
```

### 随机数与分解

```bash
echo $RANDOM
factor 12
factor $RANDOM
```

### 权限

```bash
chmod +r file
chmod +w file
chmod +x file
```

### 目录与链接

```bash
mkdir -p parent/enfant
ln -s cible lien
ls -l
```

### 打包压缩

```bash
tar czf archive.tar.gz dossier
tar tzf archive.tar.gz
```

---

## 13. 一句话总结

这部分你主要要掌握的是：

- `cat` 看文件和创建文件
- `>`、`>>`、`<`、`<<` 的区别
- 不用 `nano` 也能写文件
- `$RANDOM` 和 `factor`
- `w/x/r` 权限的实际含义
- `mkdir -p` 一行建父子目录
- `ln -s` 创建符号链接
- `tar czf` 打包压缩目录
