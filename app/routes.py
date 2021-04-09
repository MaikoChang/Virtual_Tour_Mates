from app import app, db, mail, Message
from flask import render_template, request, flash, redirect, url_for
from app.forms import UserInfoForm, PostForm, LoginForm
from app.models import User, Post
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

@app.route('/')
@app.route('/index')
def index():
    context = {
        'title': 'Virtual Tour Mates | HOME',
        'posts': Post.query.order_by(Post.date_created.desc()).all()
    }
    return render_template('index.html', **context)


@app.route('/register', methods=['GET', 'POST'])
def register():
    title = "Virtual Tour Mates | REGISTER"
    form = UserInfoForm()
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        # print(username, email, password)
        
        # create a new instance of User
        new_user = User(username, email, password)
        # add new instance to our database
        db.session.add(new_user)
        # commit database
        db.session.commit()

        # Send email to new user
        msg = Message(f'Welcome, {username}', [email])
        msg.body = "Thank you for signing up for the Virtual Tour Mates. I hope you enjoy our app!"
        msg.html = "<p>Thank you so much for signing up for the Virtual Tour Mates. I hope you enjoy our app!</p>"

        mail.send(msg)

        flash("You have succesfully signed up!", "success")
        return redirect(url_for('index'))
    return render_template('register.html', title=title, form=form)


@app.route('/requestpost', methods=['GET', 'POST'])
@login_required
def requestpost():
    title = "Virtual Tour Mates | CREATE POST"
    post = PostForm()
    if request.method == 'POST' and post.validate():
        post_title = post.title.data
        content = post.content.data
        user_id = current_user.id
        
        new_post = Post(post_title, content, user_id)
        
        db.session.add(new_post)
        
        db.session.commit()
        
        flash("You have successfully created a post!", 'success')
        
        return redirect(url_for('requestpost'))
    return render_template('request_post.html', post=post, title=title)


@app.route('/login', methods=['GET', 'POST'])
def login():
    title = "Virtual Tour Mates | LOGIN"
    form = LoginForm()
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user is None or not check_password_hash(user.password, password):
            flash("Incorrect Email/Password. Please try again", 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        flash("You have successfully logged in!", 'success')
        next_page = request.args.get('next')
        if next_page:
            return redirect(url_for(next_page.lstrip('/')))
        return redirect(url_for('index'))

    return render_template('login.html', title=title, form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("You have succesfully logged out", 'primary')
    return redirect(url_for('index'))


@app.route('/myinfo')
@login_required
def myinfo():
    title = "Virtual Tour Mates | MY INFO"
    return render_template('my_info.html', title=title)


@app.route('/jmap')
def jmap():
    title = "Virtual Tour Mates | MAP"
    return render_template('jmap.html', title=title)


@app.route('/about')
def about():
    title = "Virtual Tour Mates | About us"
    return render_template('about.html', title=title)


@app.route('/ref')
def ref():
    title = "Virtual Tour Mates | Reference"
    return render_template('ref.html', title=title)


@app.route('/placetogo')
def placetogo():
    title = "Virtual Tour Mates | places to go"
    return render_template('placetogo.html', title=title)

@app.route('/myposts')
@login_required
def myposts():
    title = "Virtual Tour Mates | MY POSTS"
    posts = current_user.posts
    return render_template('my_posts.html', title=title, posts=posts)


@app.route('/myposts/<int:post_id>')
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    title = f"Virtual Tour Mates | {post.title.upper()}"
    return render_template('post_detail.html', post=post, title=title)


@app.route('/myposts/update/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_update(post_id):
    post = Post.query.get_or_404(post_id)
    update_form = PostForm()
    if post.author.id != current_user.id:
        flash("You cannot update another user's post", 'danger')
        return redirect(url_for('myposts'))
    if request.method == 'POST' and update_form.validate():
        post_title = update_form.title.data
        content = update_form.content.data

        post.title = post_title
        post.content = content

        db.session.commit()
        flash("Your post has been updated.", 'info')
        return redirect(url_for('post_detail', post_id=post.id))

    return render_template('post_update.html', form=update_form, post=post)


@app.route('/myposts/delete/<int:post_id>', methods=['POST'])
@login_required
def post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author.id != current_user.id:
        flash("You cannot delete another user's post", 'danger')
        return redirect(url_for('myposts'))
    db.session.delete(post)
    db.session.commit()
    flash("This post has been deleted", 'info')
    return redirect(url_for('index'))