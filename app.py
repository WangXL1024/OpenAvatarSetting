from flask import Flask, render_template, jsonify, request
import os
import json
from flask_cors import CORS

app = Flask(
    __name__,
    #static_folder="static",  # 静态文件根目录（默认就是static，可省略）
    #static_url_path="/static"  # 静态文件访问URL前缀（默认是/static，可省略）
)
CORS(app)

# 配置
app.config['STATIC_FOLDER'] = 'static'
app.config['SOUND_DATA_FILE'] = 'sound_data.json'
app.config['USER_SETTINGS_FILE'] = 'user_settings.json'


def get_sound_list():
    """获取声音列表数据"""
    with open(app.config['SOUND_DATA_FILE'], 'r', encoding='utf-8') as f:
        return json.load(f)

def save_user_setting(user_id, sound_id):
    """保存用户的声音设置"""
    with open(app.config['USER_SETTINGS_FILE'], 'r+', encoding='utf-8') as f:
        settings = json.load(f)
        settings[str(user_id)] = sound_id
        f.seek(0)
        f.truncate()
        json.dump(settings, f, ensure_ascii=False, indent=2)
    return True

def get_user_setting(user_id):
    """获取用户的声音设置"""
    with open(app.config['USER_SETTINGS_FILE'], 'r', encoding='utf-8') as f:
        settings = json.load(f)
        return settings.get(str(user_id), None)

# 路由
@app.route('/')
def index():
    """显示声音选择页面"""
    return render_template('voice_select.html')

@app.route('/api/sound-list')
def api_sound_list():
    """API接口：获取声音列表"""
    try:
        sounds = get_sound_list()
        return jsonify({
            'success': True,
            'data': sounds
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/save-sound-setting', methods=['POST'])
def api_save_sound_setting():
    """API接口：保存声音设置"""
    try:
        data = request.get_json()
        # 在实际应用中，应该从认证系统获取真实的user_id
        user_id = data.get('userId', 'default_user')  # 默认用户ID
        sound_id = data.get('soundId')
        
        if not sound_id:
            return jsonify({
                'success': False,
                'error': 'Sound ID is required'
            }), 400
            
        # 验证声音ID是否存在
        sounds = get_sound_list()
        sound_ids = [s['id'] for s in sounds]
        if sound_id not in sound_ids:
            return jsonify({
                'success': False,
                'error': 'Invalid sound ID'
            }), 400
        
        # 保存设置
        save_user_setting(user_id, sound_id)
        
        return jsonify({
            'success': True,
            'message': 'Settings saved successfully',
            'data': {
                'userId': user_id,
                'soundId': sound_id
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user-sound-setting')
def api_user_sound_setting():
    """API接口：获取用户的声音设置"""
    try:
        # 在实际应用中，应该从认证系统获取真实的user_id
        user_id = request.args.get('userId', 'default_user')
        sound_id = get_user_setting(user_id)
        
        return jsonify({
            'success': True,
            'data': {
                'userId': user_id,
                'soundId': sound_id
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # 创建static目录（如果不存在）
    if not os.path.exists(app.config['STATIC_FOLDER']):
        os.makedirs(app.config['STATIC_FOLDER'])
    
    # 运行服务器
    app.run(host='0.0.0.0', port=5100, debug=True)