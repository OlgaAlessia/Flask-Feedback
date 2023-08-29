from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "secret40"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config["WTF_CSRF_ENABLED"] = False

app.app_context().push()

connect_db(app)
toolbar = DebugToolbarExtension(app)


# Page 404
@app.errorhandler(404)
def not_found(e):
  
  return render_template("404.html")

@app.route('/')
def home_page():
    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
    
        new_user = User.registration(username, password, email, first_name, last_name)

        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username already exists. Select another.')
            
        session['username'] = new_user.username
        flash('Welcome! Your account has been created successfully.', "success")
        return redirect(f'/users/{new_user.username}')
        
    return render_template('user/register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            flash(f"Welcome Back, {user.username}!", "primary")
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.']
        
    return render_template('user/login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop('username')
    flash("Goodbye!", "info")
    return redirect('/')


@app.route('/users/<username>')
def show_user(username):
    if "username" not in session or username != session['username']:
        flash("Sign in to access to your account.", "danger")
        return redirect('/login')
        
    user = User.query.get(username)
    return render_template('user/show.html', user=user)


@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):    
    if 'username' not in session:
        flash("Please login first!", "danger") #raise Unauthorized()
        return redirect('/login')
    
    user = User.query.get(username)
    if user.username == session['username']:
        db.session.delete(user)
        db.session.commit()
        flash("The user was deleted with success!", "info")
        return redirect('/')
    
    flash("You don't have permission!", "danger")
    return redirect('/login')


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    if "username" not in session or username != session['username']:
        flash("Sign in to access to your account.", "danger")
        return redirect('/login')
    
    form = FeedbackForm()
    user = User.query.get(username)
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(title=title, content=content, username = user.username )
        db.session.add(new_feedback)
        db.session.commit()
        flash('Feedback Created!', 'success')
        return redirect(f'/users/{username}')
            
    return render_template("feedback/add.html", form=form, user=user)    
    
    
@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    
    feedback = Feedback.query.get(feedback_id)
    
    if "username" not in session or feedback.username != session['username']:
        flash("Sign in to access to your account.", "danger")
        return redirect('/login')
    
    form = FeedbackForm(obj=feedback)
    
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        
        flash("The feedback was updated")
        return redirect(f'/users/{feedback.username}')
    
    return render_template("feedback/edit.html", form=form, feedback=feedback)
    
        
@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    
    if 'username' not in session or feedback.username != session['username']:
        flash("Please login first!", "danger") #raise Unauthorized()
        return redirect('/login')
    
    feedback = Feedback.query.get(feedback_id)
    if feedback.username == session['username']:
        db.session.delete(feedback)
        db.session.commit()
        flash("The feedback was deleted with success!", "info")
        return redirect(f'/users/{feedback.username}')
    
    flash("You don't have permission!", "danger")
    return redirect(f'/users/{feedback.username}')