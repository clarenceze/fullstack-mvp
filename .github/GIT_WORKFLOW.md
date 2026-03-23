# Git 工作流规范

## ⚠️ 核心规则（必须遵守）

1. **一个需求一个分支** - 每个开发需求创建独立 branch
2. **PR 前必须 pull main** - 确保与 main 最新代码无冲突
3. **解决冲突后测试** - 验证功能正常才能提交
4. **禁止在 staging 直接操作** - 不 commit/pull

---

## 📋 分支管理规则

### 1. 一个需求一个分支

每个开发需求都创建独立的功能分支：

```bash
# 基于最新的 main 创建分支
git checkout main
git pull origin main
git checkout -b feature/功能名称
```

**分支命名：**
- `feature/xxx` - 新功能
- `fix/xxx` - Bug 修复
- `docs/xxx` - 文档更新
- `chore/xxx` - 配置/工具

---

### 2. 创建 PR 前的必要步骤

**⚠️ 重要：创建 PR 前必须执行**

```bash
# 1. 切换到功能分支
git checkout feature/功能名称

# 2. 拉取 main 最新代码
git fetch origin main
git pull origin main

# 3. 合并 main 到当前分支
git merge origin/main

# 4. 解决冲突（如果有）
# 编辑冲突文件 → git add → git commit

# 5. 测试验证
# 确保功能正常

# 6. 推送到远程
git push origin feature/功能名称

# 7. 创建 PR
# 使用 GitHub API 或手动创建
```

---

### 3. 禁止行为

❌ **禁止在 main 分支直接 commit**
```bash
# 错误示例
git checkout main
git add .
git commit -m "fix: xxx"  # ❌ 禁止！
```

❌ **禁止在 staging 分支直接 commit/pull**
```bash
# 错误示例
git checkout staging
git pull origin main  # ❌ 禁止！
git commit -m "xxx"   # ❌ 禁止！
```

❌ **禁止多个需求混在一个分支**
```bash
# 错误示例
git checkout -b feature/mix  # ❌ 包含多个功能
```

---

### 4. PR 合并流程

```
1. 创建 PR (feature → main)
2. Code Review
3. CI/CD 检查通过
4. 合并到 main
5. 删除功能分支
```

---

## 🤖 AI 助手自动化

### 自主创建 PR 脚本

```bash
#!/bin/bash
# 自动创建 PR 脚本

BRANCH_NAME=$(git branch --show-current)
MAIN_BRANCH="main"

# 1. 确保是功能分支
if [ "$BRANCH_NAME" == "$MAIN_BRANCH" ]; then
    echo "❌ 不能在 main 分支创建 PR"
    exit 1
fi

# 2. 拉取最新代码
git fetch origin $MAIN_BRANCH
git pull origin $MAIN_BRANCH

# 3. 合并 main
git merge origin/$MAIN_BRANCH

# 4. 检查冲突
if [ $? -ne 0 ]; then
    echo "❌ 存在冲突，请先解决"
    exit 1
fi

# 5. 推送
git push origin $BRANCH_NAME

# 6. 创建 PR (使用 GitHub API)
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/clarenceze/fullstack-mvp/pulls \
  -d "{
    \"title\": \"feat: 功能名称\",
    \"head\": \"$BRANCH_NAME\",
    \"base\": \"$MAIN_BRANCH\",
    \"body\": \"PR 描述\"
  }"

echo "✅ PR 创建成功"
```

---

## 📊 分支状态检查

### 检查分支是否落后 main

```bash
# 查看当前分支落后 main 多少 commits
git rev-list --count HEAD..origin/main
```

### 检查是否有冲突

```bash
# 尝试合并，看是否有冲突
git merge --no-commit --no-ff origin/main
git merge --abort  # 如果有冲突，取消合并
```

---

## 🎯 最佳实践

1. **小步快跑** - 每个分支只做一个功能
2. **及时同步** - 开发过程中定期 pull main
3. **早建 PR** - 功能完成立即创建 PR
4. **清理分支** - 合并后删除已合并的分支

---

## 📝 检查清单

创建 PR 前自查：

- [ ] 基于最新的 main 创建分支
- [ ] 一个分支一个功能
- [ ] 已 pull 最新 main 代码
- [ ] 已解决所有冲突
- [ ] 本地测试通过
- [ ] 代码已推送
- [ ] PR 描述清晰

---

**最后更新：** 2026-03-23
**维护者：** OpenClaw Assistant 🦞
