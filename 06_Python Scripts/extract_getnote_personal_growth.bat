@echo off
chcp 65001 >nul
cd "C:/Users/Administrator/.claude/skills/extract-getnote-articles"

echo ============================================================
echo 开始提取"个人成长"知识库所有博主文案
echo ============================================================
echo.

echo [1/5] 提取 K森动画 (95篇)...
node extract.js "https://www.biji.com/subject/zYq5wvZY/DEFAULT?followId=1228233&followName=K%E6%A3%AE%E5%8A%A8%E7%94%BB" "E:/1.work/douyin/1.shuixing/00_InBox_收件箱/个人成长博主文案" 0 0 3
echo.

echo [2/5] 提取 西一昂（叨叨版） (138篇)...
node extract.js "https://www.biji.com/subject/zYq5wvZY/DEFAULT?followId=1221116&followName=%E8%A5%BF%E4%B8%80%E6%98%82%EF%BC%88%E5%8F%A8%E5%8F%A8%E7%89%88%EF%BC%89" "E:/1.work/douyin/1.shuixing/00_InBox_收件箱/个人成长博主文案" 0 0 3
echo.

echo [3/5] 提取 方了个方 (210篇)...
node extract.js "https://www.biji.com/subject/zYq5wvZY/DEFAULT?followId=1221115&followName=%E6%96%B9%E4%BA%86%E4%B8%AA%E6%96%B9" "E:/1.work/douyin/1.shuixing/00_InBox_收件箱/个人成长博主文案" 0 0 3
echo.

echo [4/5] 提取 Blink 的 AI 笔记 (10篇)...
node extract.js "https://www.biji.com/subject/zYq5wvZY/DEFAULT?followId=1209978&followName=Blink%20%E7%9A%84%20AI%20%E7%AC%94%E8%AE%B0" "E:/1.work/douyin/1.shuixing/00_InBox_收件箱/个人成长博主文案" 0 0 3
echo.

echo [5/5] 提取 创野小朱 (34篇)...
node extract.js "https://www.biji.com/subject/zYq5wvZY/DEFAULT?followId=1209835&followName=%E5%88%9B%E9%87%8E%E5%B0%8F%E6%9C%B1" "E:/1.work/douyin/1.shuixing/00_InBox_收件箱/个人成长博主文案" 0 0 3
echo.

echo ============================================================
echo 全部完成！
echo ============================================================
pause
