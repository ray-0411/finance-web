@echo off
REM 切換到專案資料夾
cd /d C:\Users\Ray\Desktop\coding\summer_project\finance

REM 執行資料庫備份腳本
python db.py

REM Git 自動提交
git add .

REM 取得日期時間
set mydate=%date:~0,10%
set mytime=%time:~0,8%

REM Commit，若無變更則顯示 Nothing to commit
git commit -m "Auto backup on %mydate% %mytime%" || echo Nothing to commit

REM 推送到遠端
git push