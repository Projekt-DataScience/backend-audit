from backend_db_lib.models import LPAQuestion, LPAQuestionCategory, Layer, Group


def fill_question(session, question: LPAQuestion) -> LPAQuestion:
    question.category = session.query(LPAQuestionCategory).get(question.category_id)

    # TODO: Change with request to user-managment service
    question.layer = session.query(Layer).get(question.layer_id)
    question.group = session.query(Group).get(question.group_id)

    return question


