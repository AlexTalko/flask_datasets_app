from app import db  # Импортируем db из app/__init__.py


class Dataset(db.Model):
    """Хранит информацию о наборе"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class DataPoint(db.Model):
    """Хранит точки данных с индексом для оптимизации запросов по dataset_id и timestamp"""
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    emg1 = db.Column(db.Integer)
    emg2 = db.Column(db.Integer)
    emg3 = db.Column(db.Integer)
    emg4 = db.Column(db.Integer)
    angle = db.Column(db.Integer)
    __table_args__ = (db.Index('idx_dataset_timestamp', 'dataset_id', 'timestamp'),)
