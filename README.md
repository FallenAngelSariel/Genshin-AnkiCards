# Genshin-AnkiCards


`MediaProcess.py` 用于批量处理音频文件和图片，功能如下：
-  去除音频开头和结尾没有声音的部分
- 压缩并转换FLAC为mp3
- 批量重命名：增加前缀
- 批量重命名：删除前缀

`mdFileGenerate.py` 用于生成obsidian-to-anki插件格式的.md文件，功能如下：
- 计算卡片数量（每检测到END加1）
- 删除ID
- 在批量增加或删除前缀后，更新.md文件内链接的路径
- 更新Tags
- 生成obsidian-to-anki插件格式的.md文件，可直接点击scan-vault生成anki卡片
![|168](attachments/Pasted%20image%2020250518154732.png)
obsidian-to-anki插件有个需要完善的Bug，就是不允许媒体文件名称相同。比如下图

在点击scan-vault后，后面相同名字的媒体文件会覆盖前面，导致卡片内的mp3和png错误引用，也就是Furina中引用的是HuTao的链接，同时只会生成一张卡片。原因在于Anki 要求所有媒体文件（MP3/PNG等）存放在 `collection.media` 文件夹中，在利用obsidian-to-anki导入时**丢弃路径信息**。所以所有媒体文件**名字必须相互独立**，为便于管理本人采用*批量增加角色名字为前缀*。

（Windows: `C:\Users\<用户名>\AppData\Roaming\Anki2\<账户名>\collection.media\`）

脚本运行需要的路径信息如下：
![|260](attachments/Pasted%20image%2020250519172900.png)
OriginalSources为原始flac音频文件存放路径，`MediaProcess.py`放在Furina文件夹下运行，会检测OriginalSources中的flac并根据用户选择进行处理，然后存放在另一个文件夹下。`mdFileGenerate.py`放在Furina文件夹下选择功能运行，生成md文件，根据父文件夹名称生成Tags和Deck。比如上面图片父文件夹名字Furina，那么目标牌组是Furina嵌套在Genshin下，标签同理为Furina嵌套在Genshin下。
![|352](attachments/Pasted%20image%2020250519173908.png)
![|400](attachments/Pasted%20image%2020250519173843.png)
![|245](attachments/Pasted%20image%2020250519174350.png)



操作写得比较简陋，先做个备份，**请根据需要修改脚本** 

































