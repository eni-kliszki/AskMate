from flask import Flask, render_template, redirect, request, url_for, session, flash
import data_manager

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route("/")
def main():
    questions = data_manager.latest_five()
    return render_template('index.html', questions=questions)


@app.route('/search')
@app.route("/list")
def route_list():
    snippet = request.args.get('q', '')
    order_by = request.args.get('order_by', 'id')
    order_direction = request.args.get('order_direction', 'ASC')

    questions = data_manager.get_questions(order_by, order_direction, snippet)
    return render_template('list.html', questions=questions, snippet=snippet)


@app.route('/question/<question_id>', methods=['GET', 'POST'])
def route_question_answer(question_id):
    if request.method == 'POST':
        data_manager.add_to_view(question_id)
        return redirect('/question/' + question_id)
    question = data_manager.get_question_by_id(question_id)
    if question:
        answers = data_manager.get_answers(question_id)
        question_comment = data_manager.get_question_comment(question_id)
        answer_comment = data_manager.get_answer_comment()
        return render_template('questions.html', question=question, answers=answers, id=question_id,
                               question_comment=question_comment, answer_comment=answer_comment)
    return redirect(url_for('route_list'))


@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    if 'user' in session:
        if request.method == 'POST':
            title = request.form["title"]
            message = request.form["message"]
            id = data_manager.add_new_question(title, message, session['user_id'])
            return redirect('/question/' + str(id))
        return render_template('add_question.html')
    else:
        flash("You are not logged in. Sign in, or register!")
        return redirect(url_for('login'))


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def add_answer(question_id):
    if 'user' in session:
        if request.method == 'POST':
            message = request.form["message"]
            data_manager.add_new_answer(message, question_id, session['user_id'])
            return redirect('/question/' + question_id)
        return render_template('add_answer.html', question_id=question_id)
    else:
        flash("You are not logged in! Sign in, or register!")
        return redirect(url_for('login'))


@app.route('/question/<question_id>/delete')
def delete_question(question_id):
    if session.get('user_id', '')  == data_manager.get_user_by_question_id(question_id)['user_id']:
        data_manager.delete_question(question_id)
    else:
        flash("You are not the owner of this question!")
    return redirect('/question/' + question_id)


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    if session.get('user_id', '') == data_manager.get_user_by_question_id(question_id)['user_id']:
        if request.method == 'POST':
            data_manager.question_edit(question_id, request.form['title'], request.form['message'])
            return redirect('/question/' + question_id)
        questions = data_manager.get_questions()
        return render_template("add_question.html", title=questions[int(question_id)]['title'],
                               message=questions[int(question_id)]['message'], question_id=question_id)
    flash("You are not the owner of this question!")
    return redirect('/question/' + question_id)


@app.route('/answer/<answer_id>/delete')
def delete_answer(answer_id):
    question_id = str(data_manager.get_question_id_to_answer(answer_id)['question_id'])
    if session.get('user_id', '') == data_manager.get_user_by_answer_id(answer_id)['user_id']:
        data_manager.delete_answer(answer_id)
    else:
        flash("You are not the owner of this answer!")
    return redirect('/question/' + question_id)


@app.route('/answer/<answer_id>/edit', methods=['POST', 'GET'])
def edit_answer(answer_id):
    question_id = str(data_manager.get_question_id_to_answer(answer_id)['question_id'])
    if session.get('user_id', '')  == data_manager.get_user_by_answer_id(answer_id)['user_id']:
        if request.method == 'POST':
            data_manager.answer_edit(answer_id, request.form['message'])
            return redirect('/question/' + question_id)
        answer = data_manager.get_answers_by_id(answer_id)
        return render_template("add_answer.html", question_id=question_id, message=answer['message'], answer_id=answer_id)
    flash("You are not the owner of this answer!")
    return redirect('/question/' + question_id)


@app.route('/question/<question_id>/vote', methods=['GET', 'POST'])
def question_vote(question_id):
    if 'user' in session:
        if request.method == 'POST':
            if 'vote' in request.form.keys():
                user_data = data_manager.get_all_user()
                data_manager.question_vote(question_id, request.form['vote'])
                user_data = data_manager.get_all_user()
                return redirect('/list')
            else:
                data_manager.question_vote(question_id, request.form['vote_in_questions'])
                return redirect('/question/' + question_id)
    else:
        flash("You are not logged in!")
        return redirect(url_for('login'))


@app.route('/answer/<answer_id>/vote', methods=['GET', 'POST'])
def answer_vote(answer_id):
    if 'user' in session:
        if request.method == 'POST':
            data_manager.answer_vote(answer_id, request.form['vote'])
            question_id = str(data_manager.get_question_id_to_answer(answer_id)['question_id'])
            return redirect('/question/' + question_id)
    else:
        flash("You are not logged in!")
        return redirect(url_for('login'))


@app.route("/question/<question_id>/new-comment", methods=["GET", "POST"])
def add_new_question_comment(question_id):
    if 'user' in session:
        if request.method == "POST":
            data_manager.add_new_comment(message=request.form['comment'], question_id=question_id,
                                         user_id=session['user_id'])
            return redirect("/question/" + question_id)
        return render_template('comment.html', id=question_id, table_name='question')
    else:
        flash("You are not logged in!")
        return redirect(url_for('login'))


@app.route("/answer/<answer_id>/new-comment", methods=["GET", "POST"])
def add_new_answer_comment(answer_id):
    if 'user' in session:
        if request.method == "POST":
            question_id = str(data_manager.get_question_id_to_answer(answer_id)['question_id'])
            data_manager.add_new_comment(message=request.form['comment'], answer_id=answer_id, user_id=session['user_id'])
            return redirect("/question/" + question_id)
        return render_template('comment.html', id=answer_id, table_name='answer')
    else:
        flash("You are not logged in!")
        return redirect(url_for('login'))


@app.route('/comment/<comment_id>/edit', methods=["GET", "POST"])
def edit_comment(comment_id):
    comment = data_manager.get_comment_by_id(comment_id)
    if comment['question_id'] is not None:
        question_id = str(comment['question_id'])
    else:
        question_id = str(data_manager.get_question_id_to_answer(comment['answer_id'])['question_id'])
    if session.get('user_id', '')  == data_manager.get_user_by_comment_id(comment_id)['user_id']:
        if request.method == 'POST':
            data_manager.comment_edit(comment_id, request.form['comment'])
            return redirect('/question/' + question_id)
        return render_template("comment.html", comment_id=comment['id'], message=comment['message'])
    flash("You are not the owner of this comment!")
    return redirect('/question/' + question_id)


@app.route('/comment/<comment_id>/delete')
def delete_comment(comment_id):
    comment = data_manager.get_comment_by_id(comment_id)
    if comment['question_id'] is not None:
        question_id = str(comment['question_id'])
    else:
        question_id = str(data_manager.get_question_id_to_answer(comment['answer_id'])['question_id'])
    if session.get('user_id', '')  == data_manager.get_user_by_comment_id(comment_id)['user_id']:
        data_manager.delete_comment(comment_id)
        return redirect('/question/' + question_id)
    flash("You are not the owner of this comment!")
    return redirect('/question/' + question_id)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        registration_error = data_manager.registration(request.form['email'], request.form['password'])
        if registration_error:
            flash(registration_error)
            return redirect(url_for('registration'))
        return redirect(url_for('main'))
    return render_template('registration.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if data_manager.login(request.form['email'], request.form['password']):
            if 'user' not in session:
                session['user'] = request.form['email']
                session['user_id'] = data_manager.get_user_id(session['user'])
                user_data = data_manager.get_user_info(session['user_id'])
                all_user = data_manager.get_all_user()
        else:
            flash("Wrong password or e-mail!")
            return redirect(url_for('login'))
        return redirect(url_for('main'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    return redirect(url_for('main'))


@app.route('/users')
def list_all_users():
    users = data_manager.get_all_user()
    return render_template('users.html', users=users)


@app.route('/users/<user_id>', methods=['GET', 'POST'])
def display_user(user_id):
    user = data_manager.get_user_info(user_id)
    questions=data_manager.questions_by_user_id(user_id)
    answers=data_manager.answers_by_user_id(user_id)
    comments=data_manager.comments_by_user_id(user_id)
    return render_template('user.html', user=user, questions=questions, answers=answers, comments=comments)



if __name__ == '__main__':
    main()
