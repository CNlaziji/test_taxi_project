from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from functools import wraps
import jwt
from sqlalchemy import text
import traceback
from flask_cors import CORS
import pymysql

app = Flask(__name__)

DB_USER = "remoteuser"
DB_PASS = "Taxi123."
DB_HOST = "114.67.156.124"
DB_PORT = "3306"
DB_NAME = "test_data"

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'a-very-secure-secret-key'

db = SQLAlchemy(app)

Base = automap_base()

Users = None
JNHotspot = None
JNTimeO1Hour = None
JNTimeO15Min = None
JNLuc = None
JNOnumber = None
TripRecordsData = None
PredictedGriddedHotspotsData = None
PredictedHotspotsWithLocation = None
JNHotspotsWithLocation = None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return jsonify({'success': False, 'message': 'Token format is invalid!'}), 401

        if not token:
            return jsonify({'success': False, 'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            if Users is None:
                return jsonify({'success': False, 'message': 'User model not initialized!'}), 500
            current_user = Users.query.get(data['phone'])
            if not current_user:
                return jsonify({'success': False, 'message': 'Token is invalid!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token has expired!'}), 401
        except Exception as e:
            return jsonify({'success': False, 'message': 'Token is invalid!', 'error': str(e)}), 401

        return f(current_user, *args, **kwargs)
    return decorated

def create_app():
    global Users, JNHotspot, JNTimeO1Hour, JNTimeO15Min, JNLuc, JNOnumber, TripRecordsData, PredictedGriddedHotspotsData
    global PredictedHotspotsWithLocation, JNHotspotsWithLocation

    with app.app_context():
        try:
            Base.prepare(autoload_with=db.engine)
            print(f"成功反射的表: {Base.classes.keys()}")
        except Exception as e:
            print(f"表反射失败: {str(e)}")
            traceback.print_exc()

        try:
            if 'users' in Base.classes:
                Users = Base.classes.users
                print("Users table mapped successfully.")
            else:
                print("Error: 'users' table not found during reflection.")
                raise RuntimeError("Users table not found in database.")
        except AttributeError as e:
            print(f"用户表映射失败: {str(e)}")
            traceback.print_exc()
            raise

        try:
            print(f"数据库中可用的表: {Base.classes.keys()}")
            required_tables = [
                'jn_hotspots', 'jn_time_o_1hour', 'jn_time_o_15min', 'jn_luc',
                'jn_o_number', 'trip_records_data', 'predicted_gridded_hotspots_data',
                'predicted_hotspots_with_location', 'jn_hotspots_with_location'
            ]
            missing_tables = [table for table in required_tables if table not in Base.classes.keys()]
            if missing_tables:
                print(f"警告: 以下必要表不存在于数据库中: {missing_tables}")
                class PlaceholderTable:
                    pass
                JNHotspot = PlaceholderTable()
                JNTimeO1Hour = PlaceholderTable()
                JNTimeO15Min = PlaceholderTable()
                JNLuc = PlaceholderTable()
                JNOnumber = PlaceholderTable()
                TripRecordsData = PlaceholderTable()
                PredictedGriddedHotspotsData = PlaceholderTable()
                PredictedHotspotsWithLocation = PlaceholderTable()
                JNHotspotsWithLocation = PlaceholderTable()
            else:
                print("所有必要表均存在")
                JNHotspot = Base.classes.jn_hotspots
                JNTimeO1Hour = Base.classes.jn_time_o_1hour
                JNTimeO15Min = Base.classes.jn_time_o_15min
                JNLuc = Base.classes.jn_luc
                JNOnumber = Base.classes.jn_o_number
                TripRecordsData = Base.classes.trip_records_data
                PredictedGriddedHotspotsData = Base.classes.predicted_gridded_hotspots_data
                PredictedHotspotsWithLocation = Base.classes.predicted_hotspots_with_location
                JNHotspotsWithLocation = Base.classes.jn_hotspots_with_location
                print("所有表映射成功")
        except AttributeError as e:
            print(f"数据表映射失败: {str(e)}")
            traceback.print_exc()

        try:
            db.session.execute(text('SELECT 1'))
            print("数据库连接成功！")
        except Exception as e:
            print(f"数据库连接失败: {str(e)}")
            traceback.print_exc()

    # CORS 配置
    CORS(app, resources={
        r"/auth/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Range", "X-Content-Range"],
            "max_age": 86400,
            "supports_credentials": True
        },
        r"/api/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Range", "X-Content-Range"],
            "max_age": 86400
        }
    })

    # 注册蓝图
    try:
        from auth_api import auth_bp, set_db_models as set_auth_models
        set_auth_models(db, Users, None, token_required, app)  # VerificationCodes 传 None
        app.register_blueprint(auth_bp)
        print('auth_bp 蓝图注册成功')
    except ImportError as e:
        print(f"auth_bp 蓝图导入失败: {str(e)}")
        traceback.print_exc()
    except Exception as e:
        print(f"auth_bp 蓝图设置失败: {str(e)}")
        traceback.print_exc()

    try:
        from data_api import data_bp, set_db_models as set_data_models
        set_data_models(
            db, JNHotspot, JNTimeO1Hour, JNTimeO15Min, JNLuc, JNOnumber,
            TripRecordsData, PredictedGriddedHotspotsData, PredictedHotspotsWithLocation, JNHotspotsWithLocation
        )
        app.register_blueprint(data_bp)
        print('data_bp 蓝图注册成功')
    except ImportError as e:
        print(f"data_bp 蓝图导入失败: {str(e)}")
        traceback.print_exc()
    except Exception as e:
        print(f"data_bp 蓝图设置失败: {str(e)}")
        traceback.print_exc()

    return app

if __name__ == '__main__':
    app_instance = create_app()
    app_instance.run(host='0.0.0.0', port=5000, debug=True)