# API Server 完整代码分层分析文档

## 一、代码分层结构

### 第1层：核心导入和配置
- **文件**：`api_server.py` 第9-56行
- **包含**：
  - 标准库导入（os, json, time, random, threading, re, logging）
  - 第三方库（flask, flask_cors）
  - 自定义配置（RATE_LIMIT, DANGEROUS_TAGS, DANGEROUS_ATTRIBUTES）
  - 文件锁初始化（file_locks）

### 第2层：数据模型层
- **文件**：`api_server.py` 第178-216行
- **包含**：
  - `Project` 数据类
  - `Issue` 数据类
  - `TestCase` 数据类
- **边界条件**：
  - `Project.created_at` 默认值为当前时间
  - 字段验证：id/name/path 不能为空，status 只能是 "idle" | "analyzing" | "completed" | "error"

### 第3层：数据存储层
- **文件**：`api_server.py` 第221-531行
- **核心类**：`DataStore`
- **关键方法**：
  - `load_projects()` / `save_projects()`
  - `load_issues()` / `save_issues()`
  - `load_tests()` / `save_tests()`
  - `load_settings()` / `save_settings()`
  - `_safe_save_json()` - 原子性保存
- **安全机制**：
  - 线程锁保护（file_locks）
  - 原子性写入（临时文件 + os.replace）
  - JSON解析错误捕获

### 第4层：业务逻辑层
- **文件**：`api_server.py` 第539-752行
- **核心类**：`CodeAnalyzer`
- **关键方法**：
  - `analyze_file()` - 文件分析
  - `calculate_score()` - 分数计算
  - `count_lines_of_code()` - 代码行数统计
- **检测规则**：
  - 敏感信息：API_KEY, password, secret, token, sk_live_, private_key
  - SQL注入：f"INSERT/SELECT/UPDATE/DELETE", execute(f", .format(
  - 危险函数：eval(), exec(), __import__(), os.system(), subprocess.Popen(), pickle.load()
  - 弱哈希：hashlib.md5(), hashlib.sha1(), md5()
  - 代码风格：TODO/FIXME, 过长行（>120字符）, 过多导入（>15行）

### 第5层：API路由层
- **文件**：`api_server.py` 第759-1318行
- **所有端点**：

| 端点 | 方法 | 功能 | 入参 |
|------|------|------|------|
| `/api/health` | GET | 健康检查 | 无 |
| `/api/projects` | GET | 获取项目列表 | 无 |
| `/api/projects` | POST | 创建项目 | name, path, description?, language? |
| `/api/projects/<id>` | PUT | 更新项目 | name?, path?, description?, language? |
| `/api/projects/<id>` | DELETE | 删除项目 | 无 |
| `/api/analyze` | POST | 开始分析 | projectId |
| `/api/issues` | GET | 获取问题列表 | 无 |
| `/api/tests` | GET | 获取测试列表 | 无 |
| `/api/tests` | POST | 创建测试 | name, file, description? |
| `/api/tests/<id>` | DELETE | 删除测试 | 无 |
| `/api/run-tests` | POST | 运行测试 | 无 |
| `/api/settings` | GET | 获取设置 | 无 |
| `/api/settings` | POST | 保存设置 | theme?, autoSave?, maxFileSize?, analysisDepth?, notifications?, soundEffects? |
| `/api/files/browse` | GET | 浏览目录 | path (query param) |
| `/api/files/read` | GET | 读取文件 | path (query param) |

### 第6层：安全防护层
- **XSS防护**：`sanitize_input()` 函数
- **速率限制**：`@rate_limiter` 装饰器
- **路径安全**：`is_safe_path()` 函数，限制在 `/workspace` 目录
- **安全响应头**：`@app.after_request` 添加安全头

---

## 二、所有边界条件和阈值

### 项目名称验证
- ✅ 不能为空
- ✅ 最大长度：200字符
- ✅ 必须去除首尾空格

### 项目路径验证
- ✅ 不能为空
- ✅ 最大长度：500字符
- ✅ 禁止包含 `..`（防止路径遍历）
- ✅ 必须存在

### 代码行数计算
- ✅ 只统计非空行
- ✅ 支持多语言：.py, .ts, .js, .java, .go, .rs, .cpp, .c

### 问题检测阈值
- ✅ 过长行：>120字符
- ✅ 过多导入：>15行
- ✅ 函数过多：>20个

### 分数计算
- ✅ 基础分：100分
- ✅ 最高扣分：70分
- ✅ 最低保底：30分
- ✅ 扣分权重：critical(5), high(3), medium(1.5), low(0.5)

---

## 三、隐藏逻辑和默认行为

### 1. 自动数据修复
- **位置**：`DataStore._init_defaults()` 第260-277行
- **逻辑**：
  - 自动修复状态为 "analyzing" 的卡住项目 → "idle"
  - 自动修复空项目名 → "Untitled Project {i+1}"
  - 自动修复不存在的路径 → "/workspace/path_test_system"

### 2. 智能问题去重
- **位置**：`start_analysis()` 第974-995行
- **逻辑**：
  - 同一行只保留最严重的问题
  - 按严重程度排序
  - 限制最多12个问题

### 3. 设置验证
- **位置**：`load_settings()` 第491-519行
- **逻辑**：
  - theme 最大50字符
  - maxFileSize 范围 1-1000
  - analysisDepth 范围 1-100
  - 其他字段自动转为布尔值

---

## 四、异常处理覆盖

### 文件操作异常
- ✅ `JSONDecodeError` → 返回空列表/字典
- ✅ `KeyError` → 返回空列表/字典
- ✅ 文件不存在 → 创建默认文件

### API请求异常
- ✅ 400 Bad Request → 缺少必需参数
- ✅ 404 Not Found → 资源不存在
- ✅ 403 Forbidden → 访问受限
- ✅ 409 Conflict → 资源冲突（如正在分析）
- ✅ 429 Too Many Requests → 速率限制
- ✅ 500 Internal Server Error → 服务器错误

### 分析过程异常
- ✅ `FileNotFoundError` → 状态设为 "error"
- ✅ 其他异常 → 状态设为 "error"，返回错误信息

---

## 五、数据流和状态变更

### 项目状态流转
```
idle → analyzing → completed
                    ↓
                  error
```

### 分析流程
1. 创建项目（status="idle"）
2. 开始分析（status="analyzing"）
3. 加载文件
4. 执行分析（analyzer.analyze_file()）
5. 计算分数（analyzer.calculate_score()）
6. 更新项目（status="completed"）
7. 保存问题（store.save_issues()）

---

## 六、线程安全和并发控制

### 文件锁
- ✅ 每个数据文件独立锁（projects, issues, tests, settings）
- ✅ 使用 `threading.Lock()`
- ✅ 读写都在锁保护下

### 速率限制
- ✅ 每个IP独立计数
- ✅ 每60秒重置
- ✅ 线程安全的锁保护

---

## 七、安全机制

### XSS防护
- ✅ 移除危险标签（script, iframe, object, embed等）
- ✅ 移除危险属性（onclick, onerror等）
- ✅ 转义特殊字符（< > " '）

### 路径安全
- ✅ 只能访问 `/workspace` 目录
- ✅ 使用 `os.path.abspath()` 和 `Path.resolve()` 验证

### 响应头
- ✅ X-Frame-Options: DENY
- ✅ X-Content-Type-Options: nosniff
- ✅ X-XSS-Protection: 1; mode=block
- ✅ Content-Security-Policy: default-src 'self'
- ✅ Referrer-Policy: strict-origin-when-cross-origin

---

## 八、性能优化

### 原子性写入
- ✅ 先写临时文件
- ✅ 再原子重命名
- ✅ 防止数据损坏

### 数据缓存
- ⚠️ 未实现（每次都读文件）
- 建议：可以添加内存缓存

---

## 九、测试覆盖要点

### 1. 单元测试覆盖
- [ ] sanitize_input() - 所有XSS模式
- [ ] validate_project_name() - 空/超长/正常
- [ ] validate_project_path() - 空/超长/非法/不存在/正常
- [ ] is_safe_path() - 合法/非法路径
- [ ] calculate_score() - 无问题/各种严重程度

### 2. 集成测试覆盖
- [ ] 项目CRUD完整流程
- [ ] 分析完整流程（创建→分析→获取结果）
- [ ] 文件浏览器安全检查
- [ ] 设置读取和保存

### 3. 异常测试覆盖
- [ ] 网络超时
- [ ] JSON解析失败
- [ ] 文件损坏
- [ ] 并发冲突

### 4. 压力测试覆盖
- [ ] 100+并发线程
- [ ] 长时间运行（1小时+）
- [ ] 快速连续请求
- [ ] 混合操作（读/写/删除）

---

## 十、已发现的问题和修复

### 问题1：重复导入
- **修复**：已清理

### 问题2：API方法错误
- **问题**：`/api/files/browse` 和 `/api/files/read` 使用 POST
- **修复**：改为 GET

### 问题3：日志覆盖不全
- **问题**：部分方法缺少日志
- **修复**：添加完整日志（所有load/save方法）

---

## 十一、待验证的复杂场景

1. **复杂并发竞争**
   - 同时创建同名项目
   - 同时更新和删除同一项目
   - 快速创建后立即删除

2. **复杂数据分析**
   - 分析包含所有类型问题的文件
   - 分析空文件
   - 分析超大文件

3. **复杂边界条件**
   - 路径包含特殊字符
   - 名称包含Unicode
   - 描述包含HTML标签

4. **复杂故障恢复**
   - 保存过程中强制中断
   - 文件损坏后自动恢复
   - 状态卡住后的自动修复

5. **长时间稳定性**
   - 持续24小时运行
   - 内存泄漏检测
   - 资源泄漏检测
