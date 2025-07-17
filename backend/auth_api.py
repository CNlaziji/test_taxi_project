from flask import Blueprint, jsonify, request
from functools import wraps
import jwt
import datetime
import bcrypt

auth_bp = Blueprint('auth', __name__)

_db = None
_Users = None
_token_required = None
_app = None

def get_app_and_db_models():
    if _app is None or _db is None or _Users is None or _token_required is None:
        raise RuntimeError("Auth models or app not properly initialized.")
    return _app, _db, _Users, _token_required

@auth_bp.route('/auth/register', methods=['POST'])
def register_user():
    app, db, Users, _ = get_app_and_db_models()
    print(f"Received request: {request.method} {request.url} {request.json}")  # 调试日志
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400
        
        phone = data.get('phone')
        password = data.get('password')

        if not phone or not password:
            return jsonify({'success': False, 'message': '缺少手机号或密码'}), 400

        # 验证手机号格式
        import re
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return jsonify({'success': False, 'message': '手机号格式错误'}), 400

        # 检查注册频率
        one_minute_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
        recent_user = db.session.query(Users).filter_by(phone=phone)\
            .filter(Users.created_at >= one_minute_ago).first()
        if recent_user:
            return jsonify({'success': False, 'message': '注册过于频繁，请稍后重试'}), 429

        # 检查手机号是否已注册
        if db.session.query(Users).filter_by(phone=phone).first():
            return jsonify({'success': False, 'message': '手机号已注册'}), 409

        # 加密密码并保存用户
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = Users(phone=phone, password=hashed_password, created_at=datetime.datetime.utcnow())
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True, 'message': '注册成功'}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error in register_user: {str(e)}")  # 调试日志
        return jsonify({'success': False, 'message': f'服务器内部错误: {str(e)}'}), 500

@auth_bp.route('/auth/login', methods=['POST'])
def login_user():
    app, db, Users, _ = get_app_and_db_models()
    print(f"Received request: {request.method} {request.url} {request.json}")  # 调试日志
    try:
        data = request.get_json()
        phone = data.get('phone')
        password = data.get('password')
        if not phone or not password:
            return jsonify({'success': False, 'message': '缺少手机号或密码'}), 400
        user = db.session.query(Users).filter_by(phone=phone).first()
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({'success': False, 'message': '手机号或密码错误'}), 401
        token = jwt.encode({
            'phone': user.phone,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'success': True, 'message': '登录成功', 'token': token}), 200
    except Exception as e:
        print(f"Error in login_user: {str(e)}")  # 调试日志
        return jsonify({'success': False, 'message': f'服务器内部错误: {str(e)}'}), 500

@auth_bp.route('/auth/protected', methods=['GET'])
def protected_route():
    app, db, Users, token_required_decorator = get_app_and_db_models()
    print(f"Received request: {request.method} {request.url}")  # 调试日志
    @token_required_decorator
    def inner_func(current_user):
        return jsonify({'message': f'你好，{current_user.phone}！这是受保护的数据。'}), 200
    return inner_func()

def set_db_models(database, UserModel, VerificationCodeModel, token_decorator, flask_app):
    global _db, _Users, _token_required, _app
    _db = database
    _Users = UserModel
    _token_required = token_decorator
    _app = flask_app