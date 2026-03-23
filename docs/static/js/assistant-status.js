/**
 * Assistant Status Widget
 * 右下角悬浮状态面板
 * 
 * 功能：
 * 1. 自动检测对话活跃度判断状态
 * 2. 支持手动写入大任务进度
 * 3. 可收起/展开
 * 4. 本地存储持久化
 */

class AssistantStatus {
  constructor() {
    this.lastActive = Date.now();
    this.currentTask = '待命中';
    this.tasks = [];
    this.isCollapsed = false;
    this.stats = {
      tasksCompleted: 0,
      totalMessages: 0,
      uptime: 0
    };
    
    this.init();
  }

  init() {
    // 创建 DOM 结构
    this.createWidget();
    
    // 加载本地存储
    this.loadFromStorage();
    
    // 绑定事件
    this.bindEvents();
    
    // 启动更新循环
    setInterval(() => this.update(), 5000);
    
    // 监听对话消息（如果网站有聊天功能）
    this.listenToMessages();
    
    console.log('🦞 Assistant Status Widget initialized');
  }

  /**
   * 创建 Widget DOM 结构
   */
  createWidget() {
    const widget = document.createElement('div');
    widget.id = 'assistant-status';
    widget.innerHTML = `
      <div class="status-header">
        <span class="status-icon">🦞</span>
        <span class="status-text">OpenClaw Assistant</span>
        <span class="status-toggle">▼</span>
      </div>
      <div class="status-content">
        <div class="status-indicator">
          <span class="status-dot idle"></span>
          <span class="status-label">待命中</span>
        </div>
        <div class="task-list"></div>
        <div class="status-stats">
          <div class="stat-item">
            <div class="stat-value">0</div>
            <div class="stat-label">完成任务</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">0</div>
            <div class="stat-label">消息数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">0h</div>
            <div class="stat-label">在线时长</div>
          </div>
        </div>
      </div>
    `;
    
    document.body.appendChild(widget);
    this.widget = widget;
  }

  /**
   * 从本地存储加载状态
   */
  loadFromStorage() {
    try {
      const saved = localStorage.getItem('assistant-status');
      if (saved) {
        const data = JSON.parse(saved);
        this.lastActive = data.lastActive || Date.now();
        this.currentTask = data.currentTask || '待命中';
        this.tasks = data.tasks || [];
        this.stats = data.stats || this.stats;
        this.isCollapsed = data.isCollapsed || false;
        
        if (this.isCollapsed) {
          this.widget.classList.add('collapsed');
        }
      }
    } catch (e) {
      console.error('Failed to load status from storage:', e);
    }
  }

  /**
   * 保存到本地存储
   */
  saveToStorage() {
    try {
      const data = {
        lastActive: this.lastActive,
        currentTask: this.currentTask,
        tasks: this.tasks,
        stats: this.stats,
        isCollapsed: this.isCollapsed
      };
      localStorage.setItem('assistant-status', JSON.stringify(data));
    } catch (e) {
      console.error('Failed to save status to storage:', e);
    }
  }

  /**
   * 绑定事件
   */
  bindEvents() {
    const header = this.widget.querySelector('.status-header');
    header.addEventListener('click', () => this.toggle());
  }

  /**
   * 切换收起/展开
   */
  toggle() {
    this.isCollapsed = !this.isCollapsed;
    this.widget.classList.toggle('collapsed');
    this.saveToStorage();
  }

  /**
   * 监听对话消息
   */
  listenToMessages() {
    // 方法 1: 自定义事件（如果你的网站有聊天功能）
    document.addEventListener('message-received', (e) => {
      this.onMessageReceived(e.detail.message);
    });

    // 方法 2: 轮询状态文件（GitHub Pages 方案）
    this.pollStatusFile();
  }

  /**
   * 轮询状态文件
   */
  async pollStatusFile() {
    try {
      const response = await fetch('./assistant-status.json');
      if (response.ok) {
        const data = await response.json();
        this.updateFromRemote(data);
      }
    } catch (e) {
      // 文件不存在是正常的
    }
    
    // 每 10 秒轮询一次
    setTimeout(() => this.pollStatusFile(), 10000);
  }

  /**
   * 从远程数据更新
   */
  updateFromRemote(data) {
    if (data.status === 'working') {
      this.lastActive = Date.now();
      this.tasks = data.tasks || [];
      this.stats = { ...this.stats, ...data.stats };
    }
  }

  /**
   * 收到消息时的处理
   */
  onMessageReceived(message) {
    this.lastActive = Date.now();
    this.stats.totalMessages++;
    this.currentTask = this.extractTask(message);
    
    // 自动添加任务（如果是新任务）
    if (this.currentTask !== '待命中') {
      this.addOrUpdateTask(this.currentTask);
    }
    
    this.saveToStorage();
  }

  /**
   * 从消息中提取任务关键词
   */
  extractTask(message) {
    const keywords = {
      'iCloud': 'iCloud 集成',
      '网站': '网站开发',
      '代码': '代码审查',
      '数据': '数据处理',
      '部署': '部署配置',
      '前端': '前端开发',
      '后端': '后端开发',
      '测试': '测试调试',
      '文档': '文档编写'
    };
    
    for (const [key, task] of Object.entries(keywords)) {
      if (message.includes(key)) return task;
    }
    
    return '日常任务';
  }

  /**
   * 添加或更新任务
   */
  addOrUpdateTask(taskName) {
    const existing = this.tasks.find(t => t.name === taskName);
    
    if (existing) {
      existing.progress = Math.min(existing.progress + 25, 100);
      existing.updatedAt = Date.now();
    } else {
      this.tasks.push({
        id: Date.now(),
        name: taskName,
        progress: 0,
        status: 'in_progress',
        message: '刚开始',
        updatedAt: Date.now()
      });
    }
    
    // 只保留最近 3 个任务
    if (this.tasks.length > 3) {
      this.tasks = this.tasks.slice(-3);
    }
  }

  /**
   * 手动更新任务进度（供 OpenClaw 使用）
   */
  updateTask(taskName, progress, message) {
    const task = this.tasks.find(t => t.name === taskName);
    
    if (task) {
      task.progress = progress;
      task.message = message;
      task.updatedAt = Date.now();
      
      if (progress === 100) {
        task.status = 'completed';
        this.stats.tasksCompleted++;
      }
    } else {
      this.tasks.push({
        id: Date.now(),
        name: taskName,
        progress: progress,
        status: progress === 100 ? 'completed' : 'in_progress',
        message: message,
        updatedAt: Date.now()
      });
    }
    
    this.lastActive = Date.now();
    this.saveToStorage();
  }

  /**
   * 获取当前状态
   */
  getStatus() {
    const minutes = (Date.now() - this.lastActive) / 60000;
    
    if (minutes < 2) {
      return {
        status: 'working',
        label: '工作中',
        color: 'working',
        class: 'working'
      };
    } else if (minutes < 30) {
      return {
        status: 'idle',
        label: '待命中',
        color: 'idle',
        class: 'idle'
      };
    } else {
      return {
        status: 'offline',
        label: `最后在线 ${this.formatTime(minutes)}前`,
        color: 'offline',
        class: 'offline'
      };
    }
  }

  /**
   * 格式化时间
   */
  formatTime(minutes) {
    if (minutes < 60) return `${Math.floor(minutes)}分钟`;
    return `${(minutes / 60).toFixed(1)}小时`;
  }

  /**
   * 更新显示
   */
  update() {
    const status = this.getStatus();
    
    // 更新状态指示器
    const indicator = this.widget.querySelector('.status-indicator');
    if (indicator) {
      indicator.innerHTML = `
        <span class="status-dot ${status.class}"></span>
        <span class="status-label">${status.label}</span>
      `;
    }
    
    // 更新任务列表
    this.updateTaskList();
    
    // 更新统计
    this.updateStats();
    
    // 保存状态
    this.saveToStorage();
  }

  /**
   * 更新任务列表
   */
  updateTaskList() {
    const taskList = this.widget.querySelector('.task-list');
    if (!taskList) return;
    
    const activeTasks = this.tasks.filter(t => t.status !== 'completed');
    
    if (activeTasks.length === 0) {
      taskList.innerHTML = '<div style="color: #9ca3af; font-size: 12px; text-align: center; padding: 20px;">暂无进行中的任务</div>';
      return;
    }
    
    taskList.innerHTML = activeTasks.map(task => `
      <div class="task-item">
        <div class="task-name">
          <span class="task-icon">${this.getTaskIcon(task.name)}</span>
          ${task.name}
        </div>
        <div class="task-progress">
          <div class="task-progress-bar" style="width: ${task.progress}%"></div>
        </div>
        <div class="task-percent">${task.progress}%</div>
        <div class="task-message">${task.message || ''}</div>
      </div>
    `).join('');
  }

  /**
   * 获取任务图标
   */
  getTaskIcon(taskName) {
    const icons = {
      'iCloud': '🍎',
      '网站': '🌐',
      '代码': '💻',
      '数据': '📊',
      '部署': '🚀',
      '前端': '🎨',
      '后端': '⚙️',
      '测试': '🧪',
      '文档': '📝'
    };
    
    for (const [key, icon] of Object.entries(icons)) {
      if (taskName.includes(key)) return icon;
    }
    
    return '📋';
  }

  /**
   * 更新统计信息
   */
  updateStats() {
    const stats = this.widget.querySelector('.status-stats');
    if (!stats) return;
    
    // 计算在线时长
    const uptimeHours = ((Date.now() - this.lastActive) / (1000 * 60 * 60)).toFixed(1);
    
    stats.innerHTML = `
      <div class="stat-item">
        <div class="stat-value">${this.stats.tasksCompleted}</div>
        <div class="stat-label">完成任务</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">${this.stats.totalMessages}</div>
        <div class="stat-label">消息数</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">${uptimeHours}h</div>
        <div class="stat-label">在线时长</div>
      </div>
    `;
  }
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
  window.assistantStatus = new AssistantStatus();
});

// 如果 DOM 已经加载完成
if (document.readyState !== 'loading') {
  window.assistantStatus = new AssistantStatus();
}
