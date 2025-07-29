FROM nginx:alpine

# 複製 shared 目錄到 nginx 目錄
COPY shared /usr/share/nginx/html/shared

# 複製前端檔案到 nginx 目錄
COPY student-app /usr/share/nginx/html/

# 複製自定義 nginx 配置
COPY student-app/nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 啟動 nginx
CMD ["nginx", "-g", "daemon off;"] 