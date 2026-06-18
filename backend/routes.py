from flask import Blueprint, render_template, request, jsonify, abort
from backend.curriculum import MODULES, get_module, get_prev_module, get_next_module

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html', greeting='Good Day')

@main_bp.route('/topic/<int:topic_id>')
def topic_page(topic_id):
    topic = get_module(topic_id)
    if not topic:
        abort(404)
    prev_topic = get_prev_module(topic_id)
    next_topic = get_next_module(topic_id)
    return render_template('topic.html', topic=topic, topic_idx=topic_id - 1, prev_topic=prev_topic, next_topic=next_topic)

@main_bp.route('/readme')
def readme():
    return render_template('readme.html')

@main_bp.route('/check-quiz', methods=['POST'])
def check_quiz():
    data = request.get_json()
    topic = get_module(data['topic_id'])
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404
    q = topic['questions'][data['question_idx']]
    correct = q['answer'] == data['selected']
    return jsonify({'correct': correct, 'correct_option': q['answer']})


