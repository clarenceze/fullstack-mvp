# 🦞 Assistant Status Widget 使用指南

## 📋 功能说明

右下角悬浮的龙虾状态面板，实时显示 OpenClaw AI 助手的工作状态。

---

## 🎨 显示效果

### 状态指示

| 状态 | 颜色 | 说明 |
|------|------|------|
| 🟢 工作中 | 绿色 | 2 分钟内有对话 |
| 🟡 待命中 | 黄色 | 2-30 分钟无对话 |
| ⚫ 离线 | 灰色 | 30 分钟以上无对话 |

### 多任务显示

支持同时显示最多 3 个任务，每个任务显示：
- 任务名称
- 进度条（0-100%）
- 当前状态消息

---

## 🔧 使用方法

### 1️⃣ 自动检测（日常对话）

前端会自动检测对话活跃度，无需任何配置。

**原理：**
- 监听页面消息事件
- 分析对话关键词识别任务
- 自动更新状态

---

### 2️⃣ 手动写入（大任务）

对于重要任务，OpenClaw 可以手动写入进度：

#### 方式 A: 写入 JSON 文件（推荐）

创建/更新 `docs/assistant-status.json`：

```json
{
  "status": "working",
  "updated_at": "2026-03-23T16:00:00+08:00",
  "tasks": [
    {
      "name": "iCloud 集成",
      "progress": 25,
      "message": "网络库修复完成",
      "status": "in_progress"
    }
  ],
  "stats": {
    "tasksCompleted": 5,
    "totalMessages": 42,
    "uptime": "2.5h"
  }
}
```

**Git 推送后自动同步到 GitHub Pages**

---

#### 方式 B: 调用 JavaScript API

如果网站有后端，可以在页面中调用：

```javascript
// 更新任务进度
window.assistantStatus.updateTask(
  'iCloud 集成',  // 任务名称
  50,             // 进度 0-100
  '认证成功'      // 状态消息
);
```

---

## 📊 大任务 5 节点更新模板

```
任务开始 → 写入 0%
{
  "tasks": [{
    "name": "任务名称",
    "progress": 0,
    "message": "刚开始"
  }]
}

进展 25% → 写入 25%
{
  "tasks": [{
    "name": "任务名称",
    "progress": 25,
    "message": "完成第一阶段"
  }]
}

进展 50% → 写入 50%
{
  "tasks": [{
    "name": "任务名称",
    "progress": 50,
    "message": "进行中"
  }]
}

进展 75% → 写入 75%
{
  "tasks": [{
    "name": "任务名称",
    "progress": 75,
    "message": "收尾阶段"
  }]
}

完成 100% → 写入 100%
{
  "tasks": [{
    "name": "任务名称",
    "progress": 100,
    "message": "完成！",
    "status": "completed"
  }]
}
```

---

## 🎨 自定义配置

### 修改位置

编辑 `docs/static/js/assistant-status.js`

### 常见配置

#### 1. 修改轮询间隔

```javascript
// 默认 10 秒
setTimeout(() => this.pollStatusFile(), 10000);

// 改为 30 秒
setTimeout(() => this.pollStatusFile(), 30000);
```

#### 2. 修改状态判断时间

```javascript
// 默认 2 分钟内算"工作中"
if (minutes < 2) { return { status: 'working', ... }; }

// 改为 5 分钟
if (minutes < 5) { return { status: 'working', ... }; }
```

#### 3. 添加任务关键词

```javascript
extractTask(message) {
  const keywords = {
    'iCloud': 'iCloud 集成',
    '网站': '网站开发',
    '你的关键词': '任务名称',  // 添加这里
  };
  // ...
}
```

---

## 🎨 样式定制

编辑 `docs/static/css/assistant-status.css`

### 修改颜色

```css
/* 主题色 */
.status-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  /* 改成你的主题色 */
}

/* 进度条颜色 */
.task-progress-bar {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}
```

### 修改位置

```css
#assistant-status {
  bottom: 20px;  /* 距离底部 */
  right: 20px;   /* 距离右侧 */
  
  /* 改到左下角 */
  /* bottom: 20px; */
  /* left: 20px; */
  /* right: auto; */
}
```

---

## 📱 移动端适配

已自动适配移动端：

- 屏幕宽度 < 768px 时自动缩小
- 支持触摸操作
- 不影响主要内容浏览

---

## 🐛 故障排查

### 问题 1: Widget 不显示

**检查：**
1. 浏览器控制台是否有错误
2. CSS/JS 文件是否正确加载
3. 是否被其他元素遮挡（z-index）

**解决：**
```bash
# 检查文件是否存在
ls docs/static/css/assistant-status.css
ls docs/static/js/assistant-status.js
```

---

### 问题 2: 状态不更新

**检查：**
1. 浏览器本地存储是否已满
2. JSON 文件是否正确
3. 网络请求是否被拦截

**解决：**
```javascript
// 清除本地存储
localStorage.removeItem('assistant-status');
location.reload();
```

---

### 问题 3: 进度条不动

**检查：**
1. JSON 文件格式是否正确
2. Git 推送是否成功
3. GitHub Pages 是否已同步

**解决：**
```bash
# 验证 JSON 格式
cat docs/assistant-status.json | python -m json.tool
```

---

## 📊 统计信息

Widget 会自动统计：

- ✅ 完成任务数
- 💬 消息总数
- ⏱️ 在线时长

数据保存在浏览器本地存储，刷新页面不会丢失。

---

## 🔒 隐私说明

- 所有数据保存在用户浏览器本地
- 不上传到任何服务器
- 不收集个人信息
- 开源代码可审查

---

## 📝 更新日志

### v1.0.0 (2026-03-23)
- ✅ 初始版本发布
- ✅ 自动状态检测
- ✅ 多任务支持
- ✅ 本地存储持久化
- ✅ 响应式设计

---

## 🤝 贡献

有任何问题或建议，欢迎提 Issue 或 PR！

---

**作者：** OpenClaw Assistant 🦞
**许可：** MIT License
