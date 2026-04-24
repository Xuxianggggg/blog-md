# 使用 Pandoc 将 Word 文档转换为 Markdown

## 目标

将 Microsoft Word 文档 `.docx` 转换为 GitHub Flavored Markdown 格式 `.md`，并自动提取文档中的图片资源。

---

## 一、安装 Pandoc

### 方法一：使用 winget 安装

在 PowerShell 中执行：

```powershell
winget install JohnMacFarlane.Pandoc
```

安装完成后，关闭当前 PowerShell 窗口，重新打开一个新的 PowerShell。

检查是否安装成功：

```powershell
pandoc --version
```

如果能看到 Pandoc 的版本信息，说明安装成功。

---

### 方法二：下载安装包安装

也可以访问 Pandoc 官方网站下载安装包：

```text
https://pandoc.org/installing.html
```

下载 Windows 版本的 `.msi` 安装包后，双击安装即可。

安装完成后，同样需要重新打开 PowerShell，再检查：

```powershell
pandoc --version
```

---

## 二、准备 Word 文档

将需要转换的 Word 文档放在一个文件夹中，例如：

```text
input.docx
```

然后在 PowerShell 中进入该文件夹。

---

## 三、转换 Word 为 Markdown

执行以下命令：

```powershell
pandoc "input.docx" -t gfm --wrap=none --extract-media="." -o "output.md"
```

说明：

| 参数 | 含义 |
|---|---|
| `"input.docx"` | 输入的 Word 文档 |
| `-t gfm` | 输出为 GitHub Flavored Markdown |
| `--wrap=none` | 不自动换行，保持 Markdown 内容更干净 |
| `--extract-media="."` | 提取 Word 中的图片到当前目录 |
| `-o "output.md"` | 输出 Markdown 文件 |

---

## 四、转换结果

执行成功后，文件夹中会生成：

```text
output.md
media/
```

其中：

- `output.md` 是转换后的 Markdown 文件
- `media/` 文件夹中保存从 Word 文档中提取出来的图片

Markdown 文件中的图片引用通常类似：

```markdown
![](media/image1.png)
```

---

## 五、常用命令模板

如果 Word 文件名是：

```text
example.docx
```

可以执行：

```powershell
pandoc "example.docx" -t gfm --wrap=none --extract-media="." -o "example.md"
```

如果想固定输出文件名为 `output.md`：

```powershell
pandoc "example.docx" -t gfm --wrap=none --extract-media="." -o "output.md"
```

---

## 六、注意事项

1. 命令中的横线必须使用英文短横线 `-`。
2. 参数 `--version`、`--wrap=none`、`--extract-media` 前面是两个英文短横线。
3. 如果文件名或路径中包含空格，建议使用英文双引号包起来。
4. 安装 Pandoc 后，如果命令无法识别，可以关闭并重新打开 PowerShell，或重启电脑。
5. 推荐使用 PowerShell 执行 Pandoc 命令。

---

## 最终推荐命令

```powershell
pandoc "input.docx" -t gfm --wrap=none --extract-media="." -o "output.md"
```
