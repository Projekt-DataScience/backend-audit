from backend_db_lib.models import LPAAnswer, LPAAnswerReason

from dao.lpa_answer import LPAAnswerDAO, LPAAnswerReasonDAO

def fill_answer(answer: LPAAnswer) -> LPAAnswerDAO:
    """
    This function converts the LPAAnswer model to LPAAnswerDAO for a response.
    It is mandatory, that the session, which was used to retrieve the LPAAnswer
    is still active.

    :param answer: The LPAAnswer model
    :return: LPAAnswerDAO, which can be used in a response
    """
    answers = ["green", "yellow", "red"]

    description = ""
    if answer.lpa_answer_reason is not None:
        description = answer.lpa_answer_reason.description

    return LPAAnswerDAO(
        id=answer.id,
        answer=answers[answer.answer],
        comment=answer.comment,
        reason=LPAAnswerReasonDAO(description=description),
        audit_id=answer.audit_id,
        question_id=answer.question_id,
    )
