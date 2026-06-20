# 园区出入申请系统 - 使用说明

## 📋 系统简介

这是一个完整的园区出入申请系统，包含：
- ✅ 前端表单页面（HTML/CSS/JavaScript）
- ✅ 后端API服务（Python Flask）
- ✅ 数据库存储（SQLite，无需安装MySQL）
- ✅ 文件上传功能

---

## 🚀 快速开始

### 步骤1：安装Python依赖

打开命令行，进入项目目录：

```bash
cd e:\林\backend
pip install -r requirements.txt
```

### 步骤2：启动后端服务

```bash
python app.py
```

成功启动后会看到：
```
==================================================
🚀 园区出入申请系统启动中...
==================================================
✅ 数据库初始化完成: parking_system.db
📋 API接口列表:
   • GET  /                    - 前端页面
   • POST /api/submit          - 提交申请
   • GET  /api/applications     - 获取申请列表
   • GET  /api/applications/<id> - 获取申请详情
   • GET  /uploads/<filename>   - 访问上传文件
==================================================
 * Serving Flask app 'app.py'
 * Debug mode: on
 * Running on http://127.0.0.1:5000/
```

### 步骤3：访问系统

打开浏览器访问：
- **前端页面**: http://127.0.0.1:5000/
- **API接口**: http://127.0.0.1:5000/api/applications

---

## 📂 项目文件结构

```
e:\林\
├── 园区出入申请.html          # 前端表单页面
├── backend/
│   ├── app.py                 # Flask后端主程序
│   ├── requirements.txt       # Python依赖包
│   ├── parking_system.db      # SQLite数据库（自动生成）
│   └── uploads/               # 上传文件目录（自动创建）
│       ├── license_xxx.jpg
│       ├── driver_xxx.jpg
│       └── photos_xxx.jpg
└── README.md                  # 本文件
```

---

## 🔧 功能说明

### 前端功能
- ✅ 人员姓名、车牌号、所属单位输入
- ✅ 入园/离园时间选择（自动验证时间逻辑）
- ✅ 车辆行驶证、驾驶证、车辆照片上传
- ✅ 图片预览和删除
- ✅ 实时表单验证
- ✅ 提交成功显示申请编号

### 后端功能
- ✅ 接收表单数据和文件上传
- ✅ 存储到SQLite数据库
- ✅ 生成唯一申请编号
- ✅ 提供API查询接口
- ✅ 自动创建数据库和上传目录

---

## 📡 API接口

### 1. 提交申请
```
POST http://127.0.0.1:5000/api/submit

参数：
- name: 人员姓名
- plateNumber: 车牌号
- company: 所属单位
- entryTime: 入园时间
- exitTime: 离园时间
- vehicleLicense: 车辆行驶证图片文件
- driverLicense: 驾驶证图片文件
- vehiclePhoto: 车辆照片图片文件（可多张）

返回：
{
  "success": true,
  "message": "申请提交成功！",
  "application_id": "APP20240101123045ABCD"
}
```

### 2. 获取申请列表
```
GET http://127.0.0.1:5000/api/applications

返回：
{
  "success": true,
  "applications": [...]
}
```

### 3. 获取申请详情
```
GET http://127.0.0.1:5000/api/applications/<id>

返回：
{
  "success": true,
  "application": {...}
}
```

---

## ⚠️ 常见问题

### Q1: 提示 "pip 不是内部或外部命令"
**解决方法**：重新安装Python，确保勾选 "Add Python to PATH"

### Q2: 提示端口被占用
**解决方法**：关闭占用5000端口的程序，或修改app.py中的端口号

### Q3: 文件上传失败
**解决方法**：检查uploads目录是否有写入权限

### Q4: 数据库错误
**解决方法**：删除parking_system.db文件，重新启动程序会自动创建

---

## 🛠️ 技术栈

- **前端**: HTML5, CSS3, JavaScript (原生)
- **后端**: Python 3.x, Flask
- **数据库**: SQLite (无需安装)
- **文件存储**: 本地文件系统

---

## 📞 注意事项

1. **开发环境**: 代码使用 `debug=True`，适合开发测试
2. **生产环境**: 部署时需要关闭debug模式
3. **文件大小**: 默认限制16MB，可修改app.py中的MAX_CONTENT_LENGTH
4. **数据备份**: 定期备份parking_system.db文件
5. **安全提示**: 仅供本地开发和测试使用

---

## 🎯 下一步建议

1. 添加用户认证功能
2. 添加管理员后台管理界面
3. 添加数据导出功能（Excel/CSV）
4. 添加邮件/短信通知功能
5. 添加数据统计和报表功能
6. 部署到云服务器

---

**有任何问题请随时询问！** 🚀
