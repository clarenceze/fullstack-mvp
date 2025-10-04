#!/bin/bash
# ===============================================
# 文件路径：deploy/certbot-renew.sh
# 功能：自动检测并续签 Let's Encrypt SSL 证书
# 作者：Hu Rongze
# ===============================================

# 一旦命令出错立即退出
set -e

# 日志目录与日志文件（按日期生成）
LOG_DIR="/var/log/letsencrypt"
LOG_FILE="$LOG_DIR/renew-$(date +%F).log"

# 确保日志目录存在
mkdir -p $LOG_DIR

# 执行 certbot 自动续签命令
# --quiet：静默模式，不输出多余信息
# --deploy-hook：续签成功后执行 nginx reload
# >> $LOG_FILE 2>&1：将输出与错误信息都写入日志
/usr/bin/certbot renew --quiet --deploy-hook "systemctl reload nginx" >> $LOG_FILE 2>&1

# 手动运行时输出提示
echo "✅ [$(date '+%Y-%m-%d %H:%M:%S')] 证书续签检查完成，日志保存至：$LOG_FILE"
