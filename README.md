# TW Mask API
## 簡介

2020 年武漢肺肺炎席捲全球
感謝政府利用藥局來分發口罩
並公開口罩數量地圖資料

## 結果示例 
https://twmask.herokuapp.com/twmask
### 特色
1. 自動取得位置
2. 計算最近的藥局
3. 取得指定數量的藥局
4. 以距離排序藥局
5. 使用 redis 加速
6. 定時抓取口罩資料
7. 以公里標示距離

## 資料來源
### 藥局資料
https://data.nhi.gov.tw/Datasets/DatasetDetail.aspx?id=329&Mid=A111068
### 口罩資料
https://data.nhi.gov.tw/Datasets/DatasetResource.aspx?rId=A21030000I-D50001-001
## 資料格式
藥局資料欄位包含 "醫事機構代碼、醫事機構名稱、醫事機構種類 、電話、地 址 、分區業務組、特約類別、服務項目 、診療科別 、終止合約或歇業日期 、固定看診時段 、備註"

藥局資料我們先假設不會有太大變動，我們抓取一次存檔備用即可

口罩資料欄位包含 "醫事機構代碼  醫事機構名稱  醫事機構地址  醫事機構電話  成人口罩剩餘數 兒童口罩剩餘數 來源資料時間"

口罩資料政府固定30秒更新一次，不過資料僅供參考，實際到現場還是會有一定的誤差
而且資料下載，不知道是受到 DDOS 還是政府的網路和設備都比較慢
所以目前規劃一個小時再重新抓取一次

## 思考方向
### 期待可以在知道在特定地點下，可以去最近的有口罩的藥局
### 第一個問題要解決取得目前位置的功能
地理位置定位，可以透過 瀏灠器提供的定位取得使用的位置，不過需要使用者同意取得位置資訊
https://developer.mozilla.org/zh-TW/docs/Web/API/Geolocation/Using_geolocation
### 語言 python 
### 知道目前位置要知道藥局和目前位置的遠近
### 藥局只有地址，需要將地址轉換為經緯度資料
位置轉換
https://github.com/DenisCarriere/geocoder
### 計算兩點遠近
計算距離
https://geopy.readthedocs.io/en/stable/#module-geopy.distance
### 如何使用服務
提供json response
### 選取服務提供者
heroku
## 參考
### https://bit.ly/twmask
### https://technews.tw/2020/02/04/government-admits-panic-masks-changed-to-health-insurance-card-restriction-on-6th/
