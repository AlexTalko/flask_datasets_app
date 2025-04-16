from flask import jsonify, request
from app.api import api_bp
from app import db
from app.models import Dataset, DataPoint
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
import pandas as pd
import os.path


@api_bp.route('/datasets', methods=['GET'])
def get_datasets():
    datasets = Dataset.query.all()
    return jsonify({"datasets": [{"id": ds.id, "name": ds.name} for ds in datasets]}), 200


@api_bp.route('/datasets/<int:dataset_id>', methods=['GET'])
def get_dataset_data(dataset_id):
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return jsonify({"error": "Dataset does not exist"}), 404
    stats = db.session.query(
        func.avg(DataPoint.emg1).label('emg1_avg'),
        func.max(DataPoint.emg1).label('emg1_max'),
        func.avg(DataPoint.emg2).label('emg2_avg'),
        func.max(DataPoint.emg2).label('emg2_max'),
        func.avg(DataPoint.emg3).label('emg3_avg'),
        func.max(DataPoint.emg3).label('emg3_max'),
        func.avg(DataPoint.emg4).label('emg4_avg'),
        func.max(DataPoint.emg4).label('emg4_max'),
        func.avg(DataPoint.angle).label('angle_avg'),
        func.max(DataPoint.angle).label('angle_max'),
    ).filter(DataPoint.dataset_id == dataset_id).one()
    return jsonify({
        "id": dataset.id,
        "name": dataset.name,
        "stats": {
            "emg1_avg": stats.emg1_avg,
            "emg1_max": stats.emg1_max,
            "emg2_avg": stats.emg2_avg,
            "emg2_max": stats.emg2_max,
            "emg3_avg": stats.emg3_avg,
            "emg3_max": stats.emg3_max,
            "emg4_avg": stats.emg4_avg,
            "emg4_max": stats.emg4_max,
            "angle_avg": stats.angle_avg,
            "angle_max": stats.angle_max
        }
    }), 200


@api_bp.route('/datasets', methods=['POST'])
def upload_dataset():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    name = request.form.get('name', '').strip()  # User-provided name, if any

    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    # Extract filename without extension
    base_name = os.path.splitext(file.filename)[0]
    default_name = base_name if base_name else 'Untitled Dataset'

    # Use user-provided name or filename
    name = name if name else default_name

    # Check for unique name
    existing_dataset = Dataset.query.filter_by(name=name).first()
    counter = 1
    original_name = name
    while existing_dataset:
        name = f"{original_name}_{counter}"
        existing_dataset = Dataset.query.filter_by(name=name).first()
        counter += 1

    try:
        df = pd.read_excel(file)
        dataset = Dataset(name=name)
        db.session.add(dataset)
        db.session.commit()

        # Convert types for PostgreSQL compatibility
        df = df.astype({
            'timestamp': 'int',
            'emg1': 'int',
            'emg2': 'int',
            'emg3': 'int',
            'emg4': 'int',
            'angle': 'int'
        })
        df['dataset_id'] = dataset.id
        df.to_sql('data_point', db.engine, if_exists='append', index=False, method='multi')

        return jsonify({
            "message": f"Dataset '{name}' successfully uploaded",
            "dataset": {"id": dataset.id, "name": dataset.name}
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": f"Dataset with name '{name}' already exists"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to upload dataset: {str(e)}"}), 500


@api_bp.route('/datasets/<int:dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return jsonify({"error": "Dataset not found"}), 404

    try:
        # Delete associated DataPoints first (due to foreign key constraint)
        DataPoint.query.filter_by(dataset_id=dataset_id).delete()
        # Delete the dataset
        db.session.delete(dataset)
        db.session.commit()
        return jsonify({"message": f"Dataset '{dataset.name}' deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete dataset: {str(e)}"}), 500
