import random
import numpy as np

from typing import List
from fastapi import HTTPException
from sqlalchemy import and_, or_

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend_db_lib.models import LPAAudit, Group, Layer, User, LPAAuditDuration
from backend_db_lib.models import AuditQuestionAssociation, LPAQuestion, LPAAnswer, LPAAnswerReason
from backend_db_lib.models import LPAQuestionCategory

from helpers.auth import get_user
from helpers.audit_date_parser import convert_audit_due_date
from helpers.lpa_answer import fill_answer

from dao.lpa_audit import GetAuditDAO
from dao.lpa_answer import LPAAnswerDAO
from dao.lpa_question import CreatedLPAQuestionDAO
from sqlalchemy import func
import pandas as pd
from datetime import datetime

factors_weighted_sum = {
    "global": {
        "low_mean": .1,
        "high_variance": .1,
        "low_answer_count": 0.4,
    },
    "layer": {
        "low_mean": .2,
        "high_variance": .2,
        "low_answer_count": .0,
    },
    "group": {
        "low_mean": .0,
        "high_variance": .0,
        "low_answer_count": .0,
    }
}


def get_questions_of_audit(session, audit_id: int) -> List[LPAQuestion]:
    questions = session.query(AuditQuestionAssociation).filter_by(
        audit_id=audit_id).all()
    question_ids = [question.question_id for question in questions]
    questions = []
    for id in question_ids:
        question = session.query(LPAQuestion).get(id)
        if question is not None:
            question.layer = session.query(Layer).get(question.layer_id)
            question.group = session.query(Group).get(question.group_id)
            question.category = session.query(
                LPAQuestionCategory).get(question.category_id)
            questions.append(question)

    return questions


def get_answers_of_audit(session, audit_id: int) -> List[LPAAnswer]:
    answers = session.query(LPAAnswer).filter_by(audit_id=audit_id).all()
    answer_ids = [answer.id for answer in answers]
    answers = []
    for id in answer_ids:
        answer = session.query(LPAAnswer).get(id)

        answers.append(fill_answer(answer))

    return answers


def get_durations_of_audit(session, audit_id: int) -> List[LPAAuditDuration]:
    durations = session.query(LPAAuditDuration).filter_by(
        audit_id=audit_id).all()
    duration_ids = [duration.id for duration in durations]
    durations = []
    for id in duration_ids:
        duration = session.query(LPAAuditDuration).get(id)
        durations.append(duration)

    return durations


def fill_audit(session, audit: LPAAudit) -> GetAuditDAO:
    """
    Adds assigned group, assigned layer, created by user, auditor, questions, audited user, questions,
    answers and durations to audit object
    :param audit:
    :return:
    """

    response_audit = GetAuditDAO()
    response_audit.id = audit.id
    response_audit.due_date = convert_audit_due_date(audit.due_date)
    if response_audit.complete_datetime is not None:
        response_audit.complete_datetime = convert_audit_due_date(
            audit.complete_datetime)
    response_audit.duration = audit.duration
    response_audit.recurrent_audit = audit.recurrent_audit

    response_audit.assigned_group = session.query(
        Group).get(audit.assigned_group_id)
    response_audit.assigned_layer = session.query(
        Layer).get(audit.assigned_layer_id)

    response_audit.questions = get_questions_of_audit(session, audit.id)
    response_audit.answers = get_answers_of_audit(session, audit.id)

    response_audit.created_by_user = get_user(
        session, audit.created_by_user_id)
    response_audit.auditor = get_user(session, audit.auditor_user_id)
    if audit.audited_user_id is not None:
        response_audit.audited_user = get_user(session, audit.audited_user_id)

    return response_audit


def handle_scoring(df_answers, scores, factors, possible_answers=[0, 1, 2]):
    if sum(factors.values()) == .0 or df_answers.shape[0] == 0:
        return scores  # factors are not used or no elements, don't calculate
    answer_count = len(possible_answers)
    max_answer = possible_answers[-1]

    answers_by_question = df_answers.groupby(["question_id"])["answer"]

    if factors["low_mean"] > .0:
        # low mean
        low_mean_score = factors["low_mean"] * (1 - answers_by_question.mean() / max_answer)
        scores = scores.add(low_mean_score, fill_value=.0)

    if factors["high_variance"] > .0:
        # high var
        variance = answers_by_question.var().fillna(.0)
        max_variance = variance.max()
        if max_variance > .0:
            variance /= (answer_count / 2)  # normalize to max variance possible
            scores = scores.add(variance * factors["high_variance"], fill_value=.0)

    if factors["low_answer_count"] > .0:
        # low count
        answer_count = answers_by_question.count()
        max_answer_count = answer_count.max()
        if max_answer_count > 0:
            # normalize and scale
            answer_count_scaled = (1 - (answer_count / max_answer_count)) * factors["low_answer_count"]
            # add value, if no answers, go with max value
            scores = scores.add(answer_count_scaled, fill_value=factors["low_answer_count"])

    return scores


def choose_questions_for_audit(session, questions: List[LPAQuestion], question_count: int, audit: LPAAudit,
                               algorithm: str):
    return_questions = []

    if algorithm == "random":
        unique = False
        while not unique:
            random_questions = random.choices(
                questions, k=question_count)

            question_titles = [q.question for q in random_questions]
            unique = len(question_titles) == len(set(question_titles))

        for question in random_questions:
            question_dao = CreatedLPAQuestionDAO(
                id=question.id,
                question=question.question,
                description=question.description,
                category_id=question.category_id,
                layer_id=question.layer_id,
                group_id=question.group_id,
            )
            return_questions.append(question_dao)

            aq = AuditQuestionAssociation(
                audit_id=audit.id,
                question_id=question.id,
            )
            session.add(aq)
    elif algorithm == "weighted_sum_extended":
        with dbm.create_session() as session:
            # get audits that are already completed
            audits = {x.id: x.__dict__ for x in session.query(LPAAudit).filter(LPAAudit.complete_datetime != None)}

            # combine audits with answers to have one dataframe later
            df_answers = pd.DataFrame([
                {
                    "question_id": x.question_id,
                    "answer": x.answer,
                    "complete_datetime": audits[x.audit_id]["complete_datetime"],
                    "assigned_layer_id": audits[x.audit_id]["assigned_layer_id"],
                    "assigned_group_id": audits[x.audit_id]["assigned_group_id"],
                }
                for x in session.query(LPAAnswer).all() if x.audit_id in audits.keys()
            ])

            scores = pd.Series({x[0]: .0 for x in session.query(LPAQuestion.id).all()})
            score_parts = {
                "global": handle_scoring(df_answers, scores, factors_weighted_sum["global"]),
                "layer": handle_scoring(df_answers[df_answers['assigned_layer_id'] == audit.assigned_layer_id], scores,
                                        factors_weighted_sum["layer"]),
                "group": handle_scoring(df_answers[df_answers['assigned_group_id'] == audit.assigned_group_id], scores,
                                        factors_weighted_sum["group"]),
            }
            scores_overall = pd.DataFrame(score_parts).sum(axis=1)

            # weighted random sample
            scores_dict = scores_overall.to_dict()
            if sum(scores_dict.values() > .0):
                indexes = random.choices(
                    population=list(scores_dict.keys()),
                    weights=scores_dict.values(),
                    k=question_count,
                )
            else:
                indexes = random.choices(
                    population=list(scores_dict.keys()),
                    k=question_count,
                )

            for idx in indexes:
                question = list(questions)[idx]

                question_dao = CreatedLPAQuestionDAO(
                    id=question.id,
                    question=question.question,
                    description=question.description,
                    category_id=question.category_id,
                    layer_id=question.layer_id,
                    group_id=question.group_id,
                )
                return_questions.append(question_dao)

                aq = AuditQuestionAssociation(
                    audit_id=audit.id,
                    question_id=question.id,
                )
                session.add(aq)




    elif algorithm == "weighted_sum":
        question_answers_sum = [0] * len(questions)
        question_used_count = [1] * len(questions)
        weighted_sum = []

        for i, q in enumerate(questions):
            answers = session.query(LPAAnswer).filter_by(question_id=q.id).all()

            for a in answers:
                question_answers_sum[i] += a.answer

            question_used_count[i] += session.query(AuditQuestionAssociation).filter(
                AuditQuestionAssociation.question_id == q.id).count()

            weighted_sum.append(
                question_answers_sum[i] * 1 + (1 / question_used_count[i]) * 10
            )

        # print(question_answers_sum)
        # print(question_used_count)
        # print(weighted_sum)

        # Getting the maximum values from weighted sum, to choose which questions should be in the audit
        indexes = []
        for i in range(question_count):
            max_index = np.argmax(weighted_sum)
            indexes.append(max_index)
            weighted_sum[max_index] = -1

        # print(indexes)

        for idx in indexes:
            question = list(questions)[idx]

            question_dao = CreatedLPAQuestionDAO(
                id=question.id,
                question=question.question,
                description=question.description,
                category_id=question.category_id,
                layer_id=question.layer_id,
                group_id=question.group_id,
            )
            return_questions.append(question_dao)

            aq = AuditQuestionAssociation(
                audit_id=audit.id,
                question_id=question.id,
            )
            session.add(aq)

    elif algorithm == "non_similarity":
        question_titles = [q.question for q in questions]

        # Vectorizing question titles for similarity calculation
        vectorizer = TfidfVectorizer()
        feature_vector = vectorizer.fit_transform(question_titles)

        # Calculating similarity for question titles
        similarity = cosine_similarity(feature_vector)

        # Randomly picking one question
        index = random.randint(0, len(questions) - 1)

        # Picking questions that are not similar to the randomly picked question
        similarity_score = list(enumerate(similarity[index]))
        sorted_similarity_score = sorted(similarity_score, key=lambda x: x[1], reverse=False)
        non_similar_questions = sorted_similarity_score[:question_count - 1]

        # getting question indexes 
        indexes = [index]
        indexes.extend([i[0] for i in non_similar_questions])

        print("Indexes:", indexes)

        for i in indexes:
            question = list(questions)[i]

            question_dao = CreatedLPAQuestionDAO(
                id=question.id,
                question=question.question,
                description=question.description,
                category_id=question.category_id,
                layer_id=question.layer_id,
                group_id=question.group_id,
            )
            return_questions.append(question_dao)

            aq = AuditQuestionAssociation(
                audit_id=audit.id,
                question_id=question.id,
            )
            session.add(aq)

    else:
        raise HTTPException(status_code=400, detail="Invalid algorithm")

    print("Algorithm:", algorithm)

    return return_questions
