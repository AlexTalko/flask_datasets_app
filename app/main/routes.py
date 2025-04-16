from flask import render_template, request, redirect, url_for, flash
from app.main import main_bp
from app import db
from app.models import Dataset, DataPoint
from app.utils import count_special_peaks
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
import pandas as pd
import plotly.express as px
import os.path


@main_bp.route('/')
def index():
    datasets = Dataset.query.all()
    return render_template('index.html', datasets=datasets)


@main_bp.route('/dataset/<int:dataset_id>')
def dataset_page(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    datasets = Dataset.query.all()
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

    data_points = DataPoint.query.filter_by(dataset_id=dataset_id).order_by(DataPoint.timestamp).all()
    angle_data = [dp.angle for dp in data_points]
    special_peaks_count = count_special_peaks(angle_data)

    # Выборка данных для графика
    total_points = len(data_points)
    step = max(total_points // 1000, 1)
    sampled_data = data_points[::step]
    df = pd.DataFrame([{
        'timestamp': dp.timestamp,
        'angle': dp.angle,
        'emg1': dp.emg1,
        'emg2': dp.emg2,
        'emg3': dp.emg3,
        'emg4': dp.emg4
    } for dp in sampled_data])
    fig = px.line(df, x='timestamp', y=['emg1', 'emg2', 'emg3', 'emg4', 'angle'], title=f'График набора {dataset.name}')
    plot_div = fig.to_html(full_html=False)

    return render_template('dataset.html', dataset=dataset, datasets=datasets, stats=stats, plot_div=plot_div,
                           special_peaks_count=special_peaks_count)


@main_bp.route('/add_dataset', methods=['GET', 'POST'])
def add_dataset():
    if request.method == 'POST':
        file = request.files['file']
        name = request.form.get('name', '').strip()  # Пользовательское имя, если указано

        if not file:
            flash('Пожалуйста, выберите файл Excel.', 'error')
            return render_template('add_dataset.html')

        # Извлекаем имя файла без расширения
        filename = file.filename
        if filename:
            base_name = os.path.splitext(filename)[0]  # Удаляем .xlsx
            default_name = base_name if base_name else 'Untitled Dataset'
        else:
            default_name = 'Untitled Dataset'

        # Используем пользовательское имя или имя файла
        name = name if name else default_name

        # Проверка уникальности имени
        existing_dataset = Dataset.query.filter_by(name=name).first()
        counter = 1
        original_name = name
        while existing_dataset:
            # Добавляем суффикс, если имя уже существует
            name = f"{original_name}_{counter}"
            existing_dataset = Dataset.query.filter_by(name=name).first()
            counter += 1

        try:
            df = pd.read_excel(file)
            dataset = Dataset(name=name)
            db.session.add(dataset)
            db.session.commit()

            # Преобразование типов для совместимости с PostgreSQL
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
            flash(f'Набор данных "{name}" успешно добавлен.', 'success')
            return redirect(url_for('main.index'))
        except IntegrityError as e:
            db.session.rollback()
            flash(f'Ошибка: Набор данных с именем "{name}" уже существует.', 'error')
            return render_template('add_dataset.html')
        except Exception as e:
            db.session.rollback()
            flash(f'Произошла ошибка при добавлении набора: {str(e)}', 'error')
            return render_template('add_dataset.html')

    return render_template('add_dataset.html')
