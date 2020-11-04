from psycopg2.extras import RealDictCursor
from psycopg2 import errors
import connection
import util


@connection.connection_handler
def get_questions(cursor, order_by='id', order_direction='ASC', snippet=''):
    query = f"""
        SELECT question.* 
        FROM question 
        WHERE 
            question.message ILIKE %(snippet)s OR 
            question.title ILIKE %(snippet)s OR
            EXISTS(SELECT message FROM answer WHERE question_id=question.id AND message ILIKE %(snippet)s)
        ORDER BY {order_by} {order_direction};
    """
    cursor.execute(query, {'snippet': '%'+snippet+'%'})
    return cursor.fetchall()


@connection.connection_handler
def latest_five(cursor):
    query = """
        SELECT * 
        FROM question 
        ORDER BY submission_time DESC
        LIMIT 5;
    """
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def get_question_by_id(cursor, question_id):
    query = """
        SELECT *
        FROM question
        WHERE id = %(question_id)s
    """
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchone()


@connection.connection_handler
def get_answers_by_id(cursor, answer_id):
    query = """
        SELECT *
        FROM answer
        WHERE id = %(answer_id)s
    """
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchone()


@connection.connection_handler
def get_answers(cursor, question_id):
    query = """
        SELECT *
        FROM answer
        WHERE question_id=%(question_id)s
        ORDER BY submission_time
    """
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()


@connection.connection_handler
def get_last_question_id(cursor: RealDictCursor):
    cursor.execute("""
    SELECT MAX(id)
    FROM question;
    """)
    return cursor.fetchall()[0]['max'] + 1


@connection.connection_handler
def add_new_question(cursor, title, message, user_id):
    query = f"""
        INSERT INTO question (user_id, view_number, vote_number, title, message)
        VALUES (%(user_id)s, %(view)s, %(vote)s, %(title)s, '{message}')
    """
    cursor.execute(query, {'user_id': user_id, 'view': 0, 'vote': 0, 'title': title, 'message': message})
    return get_last_question_id()


@connection.connection_handler
def add_new_answer(cursor, message, question_id, user_id):
    query = """
        INSERT INTO answer (user_id, question_id, vote_number, message)
        VALUES (%(user_id)s, %(question_id)s, %(vote)s, %(message)s);
    """
    cursor.execute(query, {'user_id': user_id, 'vote': 0, 'question_id': question_id, 'message': message})


@connection.connection_handler
def delete_question(cursor, question_id):
    answers = get_answers(question_id)
    for answer in answers:
        delete_answer(answer['id'])
    delete_tag_question_connection(question_id)
    query = """
        DELETE FROM comment 
        WHERE question_id=%(question_id)s;
        DELETE FROM question 
        WHERE id=%(question_id)s;
    """
    cursor.execute(query, {'question_id': question_id})


@connection.connection_handler
def delete_answer(cursor, answer_id):
    query = """
        DELETE FROM comment
        WHERE answer_id=%(answer_id)s;
        DELETE FROM answer 
        WHERE id=%(answer_id)s;
    """
    cursor.execute(query, {'answer_id': answer_id})


@connection.connection_handler
def question_vote(cursor, question_id, vote):
    query = """
        UPDATE question 
        SET vote_number=(vote_number+%(vote)s)
        WHERE id=%(question_id)s
    """
    if vote == '-1':
        reputation_vote_by_question_id(question_id, -2)
    else:
        reputation_vote_by_question_id(question_id, 5)
    cursor.execute(query, {'vote': vote, 'question_id' :question_id})


@connection.connection_handler
def answer_vote(cursor, answer_id, vote):
    query = """
        UPDATE answer
        SET vote_number=(vote_number+%(vote)s)
        WHERE id=%(answer_id)s;
    """
    if vote == '-1':
        reputation_vote_by_answer_id(answer_id, -2)
    else:
        reputation_vote_by_answer_id(answer_id, 10)
    cursor.execute(query, {'vote': vote, 'answer_id': answer_id})


@connection.connection_handler
def get_user_by_answer_id(cursor, answer_id):
    query = """
    SELECT user_id from answer
    WHERE id = %(answer_id)s; 
    """
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchone()


@connection.connection_handler
def get_user_by_question_id(cursor, question_id):
    query = """
    SELECT user_id from question
    WHERE id = %(question_id)s;
    """
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchone()


@connection.connection_handler
def get_user_by_comment_id(cursor, comment_id):
    query = """
    SELECT user_id from comment
    WHERE id = %(comment_id)s;
    """
    cursor.execute(query, {'comment_id': comment_id})
    return cursor.fetchone()


@connection.connection_handler
def reputation_vote_by_answer_id(cursor, answer_id, vote):
    user_id = get_user_by_answer_id(answer_id)['user_id']
    query = """
    UPDATE users
    SET reputation=(reputation+%(vote)s)
    WHERE user_id = %(user_id)s;
    """
    cursor.execute(query, {'vote': vote, 'user_id': user_id})


@connection.connection_handler
def reputation_vote_by_question_id(cursor, question_id, vote):
    user_id = get_user_by_question_id(question_id)['user_id']
    query = """
    UPDATE users
    SET reputation=(reputation+%(vote)s)
    WHERE user_id = %(user_id)s;
    """
    cursor.execute(query, {'vote': vote, 'user_id': user_id})


@connection.connection_handler
def get_question_id_to_answer(cursor, answer_id):
    cursor.execute("""
    SELECT question_id
    FROM answer
    WHERE id=%(answer_id)s
    """, {'answer_id': answer_id})
    return cursor.fetchone()


@connection.connection_handler
def question_edit(cursor, question_id, title, message):
    query = """
        UPDATE question
        SET title= %(title)s, message= %(message)s
        WHERE id=%(question_id)s;
    """
    cursor.execute(query, {'title': title, 'message': message, 'question_id': question_id})


@connection.connection_handler
def answer_edit(cursor, answer_id, message):
    query = """
        UPDATE answer
        SET message= %(message)s
        WHERE id=%(answer_id)s;
    """
    cursor.execute(query, {'message': message, 'answer_id': answer_id})


@connection.connection_handler
def add_to_view(cursor, question_id):
    query = """
        UPDATE question
        SET view_number=view_number+1
        WHERE id=%(question_id)s;
    """
    cursor.execute(query, {'question_id': question_id})


@connection.connection_handler
def add_new_comment(cursor, message, user_id, question_id=None, answer_id=None):
    query = """
        INSERT INTO comment (user_id, question_id, answer_id, message)
        VALUES (%(user_id)s, %(question_id)s, %(answer_id)s, %(message)s)
    """
    cursor.execute(query, {'user_id': user_id, 'question_id': question_id, 'answer_id': answer_id, 'message': message})


@connection.connection_handler
def get_question_comment(cursor, question_id):
    query = """
    SELECT * 
    FROM comment
    WHERE question_id = %(question_id)s
    ORDER BY submission_time
    """
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()


@connection.connection_handler
def get_answer_comment(cursor):
    query = """
    SELECT * 
    FROM comment
    ORDER BY submission_time
    """
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def comment_edit(cursor, id, message):
    query = """
        UPDATE comment
        SET message= %(message)s, submission_time= %(time)s, edited_count=edited_count+1
        WHERE id=%(id)s;
    """
    cursor.execute(query, {'id': id, 'message': message, 'time': util.current_date()})


@connection.connection_handler
def get_comment_by_id(cursor, comment_id):
    query = """
        SELECT *
        FROM comment
        WHERE id = %(comment_id)s;
    """
    cursor.execute(query, {'comment_id': comment_id})
    return cursor.fetchone()


@connection.connection_handler
def delete_comment(cursor, comment_id):
    query = """
    DELETE FROM comment
    WHERE id = %(comment_id)s;
    """
    cursor.execute(query, {'comment_id': comment_id})


@connection.connection_handler
def registration(cursor, email, password):
    try:
        query = """
        INSERT INTO users (email, hashed_password, reputation) VALUES (%(email)s, %(password)s, %(reputation)s)
        """
        cursor.execute(query, {'email': email, 'password': util.hash_password(password), 'reputation': 0})
    except errors.UniqueViolation:
        return 'The e-mail is already used!'


@connection.connection_handler
def login(cursor, email, password):
    query = """
    SELECT hashed_password FROM users WHERE email = %(email)s;
    """

    cursor.execute(query, {'email': email})
    try:
        hashed_password = cursor.fetchone()['hashed_password']
        return util.verify_password(password, hashed_password)
    except TypeError:
        return False


@connection.connection_handler
def get_user_id(cursor, email):
    query = """
    SELECT user_id FROM users WHERE email = %(email)s;
    """
    cursor.execute(query, {'email': email})
    return cursor.fetchone()['user_id']


@connection.connection_handler
def get_user_info(cursor, user_id):
    query = """
    SELECT user_id, email, reputation, registration_time FROM users
    WHERE user_id = %(user_id)s;
    """
    cursor.execute(query, {'user_id': user_id})
    user_data = cursor.fetchone()
    user_data.update(count_asked_questions(user_id))
    user_data.update(count_answers(user_id))
    user_data.update(count_comments(user_id))
    return user_data


@connection.connection_handler
def get_all_user(cursor):
    query = """
    SELECT 
        user_id, 
        email, 
        reputation, 
        registration_time, 
    (SELECT COUNT(*) FROM question WHERE question.user_id = users.user_id) as Asked_Questions, 
    (SELECT COUNT(*) FROM answer WHERE answer.user_id = users.user_id) as Answers,
    (SELECT COUNT(*) FROM comment WHERE comment.user_id = users.user_id) as Comments
    FROM users;
    """
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def count_asked_questions(cursor, user_id):
    query = """
    SELECT COUNT(*) as Asked_Questions FROM question
    WHERE user_id = %(user_id)s;
    """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchone()


@connection.connection_handler
def count_answers(cursor, user_id):
    query = """
    SELECT COUNT(*) as Answers FROM answer
    WHERE user_id = %(user_id)s;
    """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchone()


@connection.connection_handler
def count_comments(cursor, user_id):
    query = """
    SELECT COUNT(*) as Comments FROM comment
    WHERE user_id = %(user_id)s;
    """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchone()


@connection.connection_handler
def get_user_name(cursor, user_id):
    query = """
    SELECT email FROM users
    WHERE user_id = %(user_id)s;
    """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchone()


@connection.connection_handler
def delete_tag_question_connection(cursor, question_id):
    query = """
    DELETE FROM question_tag
    WHERE question_id = %(question_id)s;
    """
    cursor.execute(query, {'question_id': question_id})


@connection.connection_handler
def questions_by_user_id(cursor, user_id):
    query = """
    SELECT title, message FROM question
    WHERE user_id = %(user_id)s;
    """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()


@connection.connection_handler
def answers_by_user_id(cursor, user_id):
    query = """
    SELECT question.title, question.message, answer.message FROM answer
    INNER JOIN question ON question.id = answer.question_id
    WHERE answer.user_id = %(user_id)s
    GROUP BY question.title, question.message, answer.message;
    """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()


@connection.connection_handler
def comments_by_user_id(cursor, user_id):
    query = """
    SELECT comment.message FROM comment
    WHERE user_id = %(user_id)s;
    """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()


if __name__ == '__main__':
    pass
