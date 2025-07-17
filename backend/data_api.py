# data_api.py
from flask import Blueprint, jsonify, request
from functools import wraps
import jwt
import datetime
from sqlalchemy import func

# 创建蓝图实例
data_bp = Blueprint('data', __name__)

# 全局变量来存储注入的模型
_db = None
_jn_hotspots_model = None
_jn_time_o_1hour_model = None
_jn_luc_model = None
_jn_o_number_model = None
_trip_records_data_model = None
_predicted_gridded_hotspots_data_model = None
_jn_time_o_15min_model = None
_predicted_hotspots_with_location_model = None
_jn_hotspots_with_location_model = None

# 从app导入需要的对象和函数（使用延迟导入避免循环引用）
def get_db_models_and_app():
    # Return the globally injected models
    if _db is None:
        raise RuntimeError("Data models not properly initialized. Call set_db_models first.")
    return (_db, _jn_hotspots_model, _jn_time_o_1hour_model, _jn_luc_model, _jn_o_number_model,
            _trip_records_data_model, _predicted_gridded_hotspots_data_model, _jn_time_o_15min_model,_predicted_hotspots_with_location_model, _jn_hotspots_with_location_model)

# 修改所有路由函数的解包操作

# 易打车指数接口
@data_bp.route('/api/ride-hailing-index', methods=['GET'])
def get_ride_hailing_index():
    try:
        db, _, _, _, _, _, _, _, PredictedHotspotsWithLocationModel, _ = get_db_models_and_app()

        # 使用 SQLAlchemy 的 group_by 和 func.avg 来计算每个 location 的平均 value
        # 并按平均 value 降序排列，取前N个，这里默认取前20个，可根据需求调整
        data = db.session.query(
            PredictedHotspotsWithLocationModel.location,
            func.avg(PredictedHotspotsWithLocationModel.value).label('average_value')
        ).group_by(PredictedHotspotsWithLocationModel.location)\
         .order_by(func.avg(PredictedHotspotsWithLocationModel.value).desc())\
         .limit(20).all() # 可以设置一个限制，例如前20名

        result = []
        for item in data:
            result.append({
                'location': item.location,
                'value': round(item.average_value) # 四舍五入取整
            })
        return jsonify({'ride_hailing_index': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 拥堵指数接口
@data_bp.route('/api/congestion-index', methods=['GET'])
def get_congestion_index():
    try:
        db, _, _, _, _, _, _, _, _, JNHotspotsWithLocationModel = get_db_models_and_app()

        # 使用 SQLAlchemy 的 group_by 和 func.avg 来计算每个 location 的平均 value
        # 并按平均 value 降序排列，取前N个，这里默认取前20个
        data = db.session.query(
            JNHotspotsWithLocationModel.location,
            func.avg(JNHotspotsWithLocationModel.value).label('average_value')
        ).group_by(JNHotspotsWithLocationModel.location)\
         .order_by(func.avg(JNHotspotsWithLocationModel.value).desc())\
         .limit(20).all() # 可以设置一个限制，例如前20名

        result = []
        for item in data:
            result.append({
                'location': item.location,
                'value': round(item.average_value) # 四舍五入取整
            })
        return jsonify({'congestion_index': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 行程数据接口
@data_bp.route('/api/trip-records', methods=['GET'])
def get_trip_records():
    try:
        db, _, _, _, _, TripRecordsDataModel, _, _, _, _ = get_db_models_and_app()
        limit = request.args.get('limit', type=int, default=100)

        # 修正：通过 db.session.query(Model) 来执行查询
        records = db.session.query(TripRecordsDataModel).limit(limit).all()
        result = []
        for record in records:
            result.append({
                'id': record.id,
                'trip_distance_km': record.trip_distance_km,
                'trip_duration_min': record.trip_duration_min,
                'trip_hour': record.trip_hour
            })
        return jsonify({'trip_records': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 网格热点数据接口
@data_bp.route('/api/gridded-hotspots', methods=['GET'])
def get_gridded_hotspots():
    try:
        db, _, _, _, _, _, PredictedGriddedHotspotsDataModel, _, _, _ = get_db_models_and_app()

        # 修正：通过 db.session.query(Model) 来执行查询
        hotspots = db.session.query(PredictedGriddedHotspotsDataModel).all()
        result = []
        for hotspot in hotspots:
            result.append({
                'grid_id': hotspot.grid_id,
                'hotspot_count': hotspot.hotspot_count,
                'center_lat': hotspot.center_lat,
                'center_lng': hotspot.center_lng,
                'predicted_hotspot_count': hotspot.predicted_hotspot_count
            })
        return jsonify({'gridded_hotspots': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 热点区域数据接口
@data_bp.route('/api/hotspots', methods=['GET'])
def get_hotspots():
    try:
        db, JnHotspotsModel, _, _, _, _, _, _, _, _ = get_db_models_and_app()
        # 修正：通过 db.session.query(Model) 来执行查询
        hotspots = db.session.query(JnHotspotsModel).all()
        result = []
        for spot in hotspots:
            result.append({
                'lat': spot.lat,
                'lng': spot.lng,
                'count': spot.count,
                'time': spot.time.isoformat() if spot.time else None, # 转换为ISO格式字符串
                'date_prefix': spot.date_prefix
            })
        return jsonify({'hotspots': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 15分钟粒度上客量数据接口
@data_bp.route('/api/jn-time-o-15min', methods=['GET'])
def get_jn_time_o_15min():
    try:
        db, _, _, _, _, _, _, JnTimeO15MinModel, _, _ = get_db_models_and_app()
        # 修正：通过 db.session.query(Model) 来执行查询
        data = db.session.query(JnTimeO15MinModel).all()
        result = []
        for item in data:
            result.append({
                'O_time': item.O_time.isoformat() if item.O_time else None,
                'count': item.count
            })
        return jsonify({'jn_time_o_15min': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 1小时粒度上客量数据接口
@data_bp.route('/api/jn-time-o-1hour', methods=['GET'])
def get_jn_time_o_1hour():
    try:
        db, _, JnTimeO1HourModel, _, _, _, _, _, _, _ = get_db_models_and_app()
        # 修正：通过 db.session.query(Model) 来执行查询
        data = db.session.query(JnTimeO1HourModel).all()
        result = []
        for item in data:
            result.append({
                'O_time': item.O_time.isoformat() if item.O_time else None,
                'count': item.count
            })
        return jsonify({'jn_time_o_1hour': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 载客车辆数量/上客事件数量接口
@data_bp.route('/api/jn-o-number', methods=['GET'])
def get_jn_o_number():
    try:
        db, _, _, _, JnONumberModel, _, _, _, _, _ = get_db_models_and_app()
        # 修正：通过 db.session.query(Model) 来执行查询
        data = db.session.query(JnONumberModel).all()
        result = []
        for item in data:
            result.append({
                'time': item.TIME.isoformat() if item.TIME else None,
                'number': item.number,
            })
        return jsonify({'jn_o_number': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 运客路程分布数据接口
@data_bp.route('/api/jn-luc', methods=['GET'])
def get_jn_luc():
    try:
        db, _, _, JnLucModel, _, _, _, _, _, _ = get_db_models_and_app()
        # 修正：通过 db.session.query(Model) 来执行查询
        data = db.session.query(JnLucModel).all()
        result = []
        for item in data:
            result.append({
                'day': item.day,
                'near': item.near,
                'middle': item.middle,
                'far': item.far
            })
        return jsonify({'jn_luc': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 用于 app.py 注入模型（无 token）
def set_db_models(database, jn_hotspots_model, jn_time_o_1hour_model, jn_time_o_15min_model,
                  jn_luc_model, jn_o_number_model, trip_records_model, predicted_gridded_hotspots_model,predicted_hotspots_with_location_model, jn_hotspots_with_location_model):
    global _db, _jn_hotspots_model, _jn_time_o_1hour_model, _jn_time_o_15min_model
    global _jn_luc_model, _jn_o_number_model, _trip_records_data_model, _predicted_gridded_hotspots_data_model
    global _predicted_hotspots_with_location_model, _jn_hotspots_with_location_model

    _db = database
    _jn_hotspots_model = jn_hotspots_model
    _jn_time_o_1hour_model = jn_time_o_1hour_model
    _jn_time_o_15min_model = jn_time_o_15min_model
    _jn_luc_model = jn_luc_model
    _jn_o_number_model = jn_o_number_model
    _trip_records_data_model = trip_records_model
    _predicted_gridded_hotspots_data_model = predicted_gridded_hotspots_model
    _predicted_hotspots_with_location_model = predicted_hotspots_with_location_model
    _jn_hotspots_with_location_model = jn_hotspots_with_location_model