"""
园区出入申请系统 - Flask后端
功能：处理表单提交、文件上传、数据存储、管理页面
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import sqlite3
from datetime import datetime
import uuid
import json

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
UPLOAD_FOLDER = 'uploads'
DATABASE = 'parking_system.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB最大文件大小

# 文件分类目录
FILE_CATEGORIES = {
    'vehicle_license': '行驶证',
    'driver_license': '驾驶证',
    'vehicle_photos': '车辆照片',
    'id_card': '身份证'
}

# 确保上传目录存在
for category in FILE_CATEGORIES.keys():
    os.makedirs(os.path.join(UPLOAD_FOLDER, category), exist_ok=True)

# 数据库初始化
def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            plate_number TEXT NOT NULL,
            company TEXT NOT NULL,
            entry_time TEXT NOT NULL,
            exit_time TEXT NOT NULL,
            vehicle_license TEXT,
            driver_license TEXT,
            vehicle_photos TEXT,
            id_card TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    try:
        cursor.execute('ALTER TABLE applications ADD COLUMN id_card TEXT')
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()
    print(f"✅ 数据库初始化完成: {DATABASE}")

# API接口
@app.route('/')
def index():
    """返回前端申请页面"""
    return send_file('园区出入申请.html')

@app.route('/admin')
def admin():
    """返回管理页面"""
    return send_file('admin.html')

@app.route('/api/submit', methods=['POST'])
def submit_application():
    """处理申请表单提交"""
    try:
        application_id = f"APP{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"
        
        name = request.form.get('name')
        plate_number = request.form.get('plateNumber')
        company = request.form.get('company')
        entry_time = request.form.get('entryTime')
        exit_time = request.form.get('exitTime')
        
        vehicle_license_filename = save_file(request.files.get('vehicleLicense'), 'vehicle_license')
        driver_license_filename = save_file(request.files.get('driverLicense'), 'driver_license')
        vehicle_photos_filenames = save_multiple_files(request.files.getlist('vehiclePhoto'), 'vehicle_photos')
        id_card_filename = save_file(request.files.get('idCard'), 'id_card')
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO applications 
            (application_id, name, plate_number, company, entry_time, exit_time,
             vehicle_license, driver_license, vehicle_photos, id_card, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            application_id,
            name,
            plate_number,
            company,
            entry_time,
            exit_time,
            vehicle_license_filename,
            driver_license_filename,
            json.dumps(vehicle_photos_filenames),
            id_card_filename,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ 新申请提交成功: {application_id} - {name}")
        
        return jsonify({
            'success': True,
            'message': '申请提交成功！',
            'application_id': application_id
        })
        
    except Exception as e:
        print(f"❌ 提交失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'提交失败: {str(e)}'
        }), 500

@app.route('/api/applications', methods=['GET'])
def get_applications():
    """获取申请列表（支持分页和搜索）"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('perPage', 10))
        search = request.args.get('search', '')
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        offset = (page - 1) * per_page
        
        if search:
            cursor.execute('''
                SELECT id, application_id, name, plate_number, company, 
                       entry_time, exit_time, status, created_at
                FROM applications 
                WHERE name LIKE ? OR plate_number LIKE ? OR company LIKE ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (f'%{search}%', f'%{search}%', f'%{search}%', per_page, offset))
            
            cursor.execute('''
                SELECT COUNT(*) FROM applications 
                WHERE name LIKE ? OR plate_number LIKE ? OR company LIKE ?
            ''', (f'%{search}%', f'%{search}%', f'%{search}%'))
        else:
            cursor.execute('''
                SELECT id, application_id, name, plate_number, company, 
                       entry_time, exit_time, status, created_at
                FROM applications 
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (per_page, offset))
            
            cursor.execute('SELECT COUNT(*) FROM applications')
        
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM applications WHERE status = "pending"')
        pending = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM applications WHERE status = "approved"')
        approved = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM applications WHERE status = "rejected"')
        rejected = cursor.fetchone()[0]
        
        conn.close()
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        if search:
            cursor.execute('''
                SELECT id, application_id, name, plate_number, company, 
                       entry_time, exit_time, status, created_at
                FROM applications 
                WHERE name LIKE ? OR plate_number LIKE ? OR company LIKE ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (f'%{search}%', f'%{search}%', f'%{search}%', per_page, offset))
        else:
            cursor.execute('''
                SELECT id, application_id, name, plate_number, company, 
                       entry_time, exit_time, status, created_at
                FROM applications 
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (per_page, offset))
        
        applications = []
        for row in cursor.fetchall():
            applications.append({
                'id': row[0],
                'application_id': row[1],
                'name': row[2],
                'plate_number': row[3],
                'company': row[4],
                'entry_time': row[5],
                'exit_time': row[6],
                'status': row[7],
                'created_at': row[8]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'applications': applications,
            'total': total,
            'page': page,
            'perPage': per_page,
            'pending': pending,
            'approved': approved,
            'rejected': rejected
        })
        
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500

@app.route('/api/applications/<int:app_id>', methods=['GET'])
def get_application(app_id):
    """获取单个申请详情"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM applications WHERE id = ?
        ''', (app_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            application = {
                'id': row[0],
                'application_id': row[1],
                'name': row[2],
                'plate_number': row[3],
                'company': row[4],
                'entry_time': row[5],
                'exit_time': row[6],
                'vehicle_license': row[7],
                'driver_license': row[8],
                'vehicle_photos': row[9],
                'id_card': row[10] if len(row) > 10 else None,
                'status': row[11] if len(row) > 11 else row[10],
                'created_at': row[12] if len(row) > 12 else row[11],
                'updated_at': row[13] if len(row) > 13 else row[12]
            }
            
            return jsonify({
                'success': True,
                'application': application
            })
        else:
            return jsonify({
                'success': False,
                'message': '申请不存在'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500

@app.route('/api/applications/<int:app_id>/status', methods=['PUT'])
def update_application_status(app_id):
    """更新申请状态"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if status not in ['pending', 'approved', 'rejected']:
            return jsonify({
                'success': False,
                'message': '无效的状态值'
            }), 400
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE applications 
            SET status = ?, updated_at = ?
            WHERE id = ?
        ''', (status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), app_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ 状态更新成功: {app_id} -> {status}")
        
        return jsonify({
            'success': True,
            'message': '状态更新成功'
        })
        
    except Exception as e:
        print(f"❌ 更新失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'更新失败: {str(e)}'
        }), 500

@app.route('/uploads/<category>/<filename>')
def uploaded_file(category, filename):
    """访问上传的文件"""
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], category), filename)

def download_file(category, filename):
    """下载文件"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], category, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'success': False, 'message': '文件不存在'}), 404

@app.route('/api/download/<category>/<filename>')
def api_download_file(category, filename):
    """下载文件API"""
    return download_file(category, filename)

# 辅助函数
def save_file(file, category):
    """保存单个文件到指定分类目录"""
    if file and file.filename:
        ext = file.filename.rsplit('.', 1)[-1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], category, filename)
        file.save(filepath)
        return filename
    return None

def save_multiple_files(files, category):
    """保存多个文件到指定分类目录"""
    filenames = []
    for file in files:
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[-1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], category, filename)
            file.save(filepath)
            filenames.append(filename)
    return filenames

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 园区出入申请系统启动中...")
    print("=" * 50)
    
    init_db()
    
    print("📋 API接口列表:")
    print("   • GET  /                    - 前端页面")
    print("   • GET  /admin               - 管理页面")
    print("   • POST /api/submit           - 提交申请")
    print("   • GET  /api/applications     - 获取申请列表")
    print("   • GET  /api/applications/<id> - 获取申请详情")
    print("   • GET  /uploads/<category>/<filename> - 访问上传文件")
    print("=" * 50)
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.run(debug=debug, host='0.0.0.0', port=port)
