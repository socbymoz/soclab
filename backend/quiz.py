from backend.curriculum import get_module

def check_answer(topic_id, question_idx, selected):
    topic = get_module(topic_id)
    if not topic:
        return None
    q = topic['questions'][question_idx]
    return q['answer'] == selected

def get_correct_answer(topic_id, question_idx):
    topic = get_module(topic_id)
    if not topic:
        return None
    return topic['questions'][question_idx]['answer']
