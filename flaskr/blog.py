from flask import (
	Blueprint,
	flash,
	g,
	redirect,
	render_template,
	request,
	url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
@login_required
def index():
	db = get_db()
	posts = db.execute(
		'SELECT p.id, amount, created, attendant_id, username'
		' FROM today_income p JOIN user u ON p.attendant_id = u.id'
		' ORDER BY created DESC LIMIT 5'
	).fetchall()

	sum1 = db.execute(
		'SELECT SUM(amount) FROM today_income'
	).fetchone()

	return render_template('blog/index.html', posts=posts, sum1=sum1)



@bp.route('/', methods=('GET', 'POST'))
@login_required
def create():
	if request.method == 'POST':
		amount = request.form['amount']
		# body = request.form['body']
		error = None

		if not amount:
			error = 'Title is required'

		if error is not None:
			flash(error)
		else:
			db = get_db()
			db.execute(
				'INSERT INTO today_income (amount, attendant_id)'
				' VALUES (?, ?)',
				(amount, g.user['id'])
			)
			db.commit()
			return redirect(url_for('blog.index'))

	# return render_template('blog/index.html')


def get_post(id, check_author=True):
	post = get_db().execute(
		'SELECT p.id, amount, created, attendant_id, username'
		' FROM today_income p JOIN user u ON p.attendant_id = u.id'
		' WHERE p.id = ?',
		(id,)
	).fetchone()

	if post is None:
		abort(404, 'Post id {0} doesnt exist'.format(id))

	if check_author and post['attendant_id'] != g.user['id']:
		abort(403)	

	return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        amount = request.form['amount']
        # body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE today_income SET amount = ?,'
                ' WHERE id = ?',
                (title, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)	

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM today_income WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))