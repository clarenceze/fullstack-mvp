#!/bin/bash
# ===============================================
# 文件路径：deploy/deploy_nginx.sh
# 功能：自动部署 Nginx 配置与 Certbot 自动续签任务
# 作者：Hu Rongze
# ===============================================

set -e  # 一旦命令出错立即退出

echo "🚀 开始部署 Nginx 与 Certbot 自动续签配置..."

# 1️⃣ 创建 Certbot 验证路径（Let's Encrypt 用于验证域名所有权）
echo "📂 创建验证目录 /var/www/certbot ..."
sudo mkdir -p /var/www/certbot
sudo chmod 755 /var/www/certbot

# 2️⃣ 拷贝 Nginx 配置文件
if [ -f "./nginx/api.conf" ]; then
  if [ -f "/etc/nginx/conf.d/api.conf" ]; then
    echo "⚙️ 检测到旧的 /etc/nginx/conf.d/api.conf，正在覆盖..."
  fi
  echo "📦 拷贝新的 Nginx 配置文件..."
  sudo cp -f ./nginx/api.conf /etc/nginx/conf.d/api.conf
else
  echo "❌ 未找到 nginx/api.conf，请检查路径是否正确。"
  exit 1
fi


# 3️⃣ 拷贝 certbot-renew.sh 到 /usr/local/bin/
if [ -f "./deploy/certbot-renew.sh" ]; then
  echo "🧩 拷贝 certbot-renew.sh 到 /usr/local/bin/ ..."
  sudo cp ./deploy/certbot-renew.sh /usr/local/bin/certbot-renew.sh
  sudo chmod +x /usr/local/bin/certbot-renew.sh
else
  echo "❌ 未找到 deploy/certbot-renew.sh，请检查文件是否存在。"
  exit 1
fi

# 4️⃣ 拷贝 systemd service/timer 文件
if [ -f "./deploy/certbot-renew.service" ] && [ -f "./deploy/certbot-renew.timer" ]; then
  echo "🧠 拷贝 systemd 服务与定时器文件..."
  sudo cp ./deploy/certbot-renew.service /etc/systemd/system/certbot-renew.service
  sudo cp ./deploy/certbot-renew.timer /etc/systemd/system/certbot-renew.timer
else
  echo "❌ 未找到 systemd 配置文件，请检查 deploy/ 目录。"
  exit 1
fi

# 5️⃣ 注册并启动定时任务
echo "🔁 注册 certbot-renew.timer 定时任务..."
sudo systemctl daemon-reload
sudo systemctl enable certbot-renew.timer
sudo systemctl start certbot-renew.timer

# 6️⃣ 测试 nginx 配置语法并 reload
echo "🧪 测试 nginx 配置语法..."
sudo nginx -t
echo "♻️ 重新加载 nginx ..."
sudo systemctl reload nginx

echo "✅ 部署完成！请使用以下命令确认状态："
echo "   sudo systemctl status certbot-renew.timer"
echo "   sudo systemctl list-timers | grep certbot"
