from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, PostForm, CommentForm, UpdateSettingsForm
from app.models import User, Post, Reaction, Comment, Follow

# Route: Landing Page
@app.route('/')
def index():
    """
    Display the landing page. Redirects to the dashboard if the user is logged in.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# Route: Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login. Redirect to dashboard if already logged in.
    """
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

# Route: Registration Page    
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration. Redirects to dashboard if logged in.
    """
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        #flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    elif form.errors:
        flash('There were errors in the form. Please correct them.', 'danger')
    return render_template('register.html', form=form)


# Route: Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """
    Display posts and handle post and comment creation.
    """
    post_form = PostForm()  # Form for creating posts
    comment_form = CommentForm()  # Form for creating comments
    form_type = request.form.get('form_type')  # Identify submitted form

    # Handle new post creation
    if form_type == "post_form" and post_form.validate_on_submit():
        post = Post(content=post_form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('dashboard'))

    # Handle new comment creation
    if form_type == "comment_form" and comment_form.validate_on_submit():
        post_id = request.form.get('post_id')
        post = Post.query.get_or_404(post_id)
        comment = Comment(content=comment_form.content.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('dashboard'))

    # Filter posts based on user's preference (all or followed users)
    filter_type = request.args.get('filter', 'all')
    if filter_type == 'following':
        followed_user_ids = [follow.followed_id for follow in current_user.followed]
        posts = Post.query.filter(Post.user_id.in_(followed_user_ids)).order_by(Post.timestamp.desc()).all()
    else:
        posts = Post.query.order_by(Post.timestamp.desc()).all()

    # Precompute reaction data for each post
    posts_with_reactions = []
    for post in posts:
        liked = any(reaction.user_id == current_user.id and reaction.reaction_type == 'like' for reaction in post.reactions)
        disliked = any(reaction.user_id == current_user.id and reaction.reaction_type == 'dislike' for reaction in post.reactions)
        posts_with_reactions.append({
            "post": post,
            "likes": Reaction.query.filter_by(post_id=post.id, reaction_type="like").count(),
            "dislikes": Reaction.query.filter_by(post_id=post.id, reaction_type="dislike").count(),
            "liked": liked,
            "disliked": disliked
        })

    # Render dashboard with all posts and reactions
    return render_template('dashboard.html',
                           posts=posts_with_reactions,
                           post_form=post_form,
                           comment_form=comment_form,
                           filter_type=filter_type)

# Route: My Posts and Comments
@app.route('/my_posts', methods=['GET', 'POST'])
@login_required
def my_posts():
    """
    Display the user's posts or posts they have commented on.
    """
    filter_type = request.args.get('filter', 'posts')  # Determine filter type

    if filter_type == 'comments':  # Show posts with user's comments
        commented_posts = Post.query.join(Comment, Comment.post_id == Post.id) \
            .filter(Comment.user_id == current_user.id).order_by(Post.timestamp.desc()).all()
        
        posts_with_comments = [
            {"post": post, "comments": Comment.query.filter_by(post_id=post.id, user_id=current_user.id).all()}
            for post in commented_posts
        ]
        return render_template('my_posts.html', filter_type=filter_type, posts_with_comments=posts_with_comments)
    
    # Show user's own posts
    user_posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.timestamp.desc()).all()
    return render_template('my_posts.html', filter_type=filter_type, user_posts=user_posts)

# Route: Logout
@app.route('/logout')
@login_required
def logout():
    """
    Log the user out and redirect to the index page.
    """
    logout_user()
    return redirect(url_for('index'))

# Route: Like a Post
@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    """
    Add or toggle 'like' reaction on a post.
    """
    post = Post.query.get_or_404(post_id)
    existing_reaction = Reaction.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if existing_reaction:
        if existing_reaction.reaction_type == "like":
            db.session.delete(existing_reaction)
        else:
            existing_reaction.reaction_type = "like"
    else:
        reaction = Reaction(reaction_type="like", user_id=current_user.id, post_id=post_id)
        db.session.add(reaction)

    db.session.commit()

    # Return updated like and dislike counts
    like_count = Reaction.query.filter_by(post_id=post_id, reaction_type="like").count()
    dislike_count = Reaction.query.filter_by(post_id=post_id, reaction_type="dislike").count()
    return jsonify({"likes": like_count, "dislikes": dislike_count}), 200

# Route: Dislike a Post
@app.route('/dislike/<int:post_id>', methods=['POST'])
@login_required
def dislike_post(post_id):
    """
    Add or toggle 'dislike' reaction on a post.
    """
    post = Post.query.get_or_404(post_id)
    existing_reaction = Reaction.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if existing_reaction:
        if existing_reaction.reaction_type == "dislike":
            db.session.delete(existing_reaction)
        else:
            existing_reaction.reaction_type = "dislike"
    else:
        reaction = Reaction(reaction_type="dislike", user_id=current_user.id, post_id=post_id)
        db.session.add(reaction)

    db.session.commit()

    # Return updated like and dislike counts
    like_count = Reaction.query.filter_by(post_id=post_id, reaction_type="like").count()
    dislike_count = Reaction.query.filter_by(post_id=post_id, reaction_type="dislike").count()
    return jsonify({"likes": like_count, "dislikes": dislike_count})

# Route: Delete a Post
@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    """
    Allow users to delete their own posts.
    """
    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('my_posts'))

# Route: User Profile
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Display and update user profile, including account deletion and updating settings.
    """
    form = UpdateSettingsForm()

    if request.method == 'POST':
        if 'delete_account' in request.form:  # Handle account deletion
            db.session.delete(current_user)
            db.session.commit()
            logout_user()
            return redirect(url_for('index'))
        elif form.validate_on_submit():  # Handle updates for username/password
            if form.username.data != current_user.username:  # Update username
                if User.query.filter_by(username=form.username.data).first():
                    flash('Username is already taken.', 'danger')
                    return redirect(url_for('profile'))
                current_user.username = form.username.data

            if form.password.data and form.password.data == form.confirm_password.data:  # Update password
                current_user.password = form.password.data  # Should be hashed in real scenarios
            db.session.commit()
            return redirect(url_for('profile'))

    # Fetch following and follower information
    following = User.query.join(Follow, Follow.followed_id == User.id).filter(Follow.follower_id == current_user.id).all()
    followers = User.query.join(Follow, Follow.follower_id == User.id).filter(Follow.followed_id == current_user.id).all()

    return render_template('profile.html', form=form, following=following, followers=followers)

# Route: Search Users (API)
@app.route('/api/search_users', methods=['GET'])
@login_required
def api_search_users():
    """
    Search for users excluding the current user. 
    Returns follow status as part of the API response.
    """
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({'results': []})

    users = User.query.filter(User.username.ilike(f"%{query}%"), User.id != current_user.id).all()
    results = [{'username': user.username, 'is_followed': bool(Follow.query.filter_by(
        follower_id=current_user.id, followed_id=user.id).first())} for user in users]

    return jsonify({'results': results})

# Route: Follow a User (API)
@app.route('/api/follow/<string:username>', methods=['POST'])
@login_required
def follow_user(username):
    """
    Follow a user by username.
    """
    user_to_follow = User.query.filter_by(username=username).first()
    if not user_to_follow:
        return jsonify({'error': 'User not found'}), 404

    if user_to_follow == current_user:  # Prevent self-follow
        return jsonify({'error': 'You cannot follow yourself'}), 400

    if Follow.query.filter_by(follower_id=current_user.id, followed_id=user_to_follow.id).first():
        return jsonify({'message': f'Already following {username}'}), 200

    # Add follow record
    new_follow = Follow(follower_id=current_user.id, followed_id=user_to_follow.id)
    db.session.add(new_follow)
    db.session.commit()
    return jsonify({'message': f'Now following {username}'}), 200

# Route: Unfollow a User (API)
@app.route('/api/unfollow/<string:username>', methods=['POST'])
@login_required
def unfollow_user(username):
    """
    Unfollow a user by username.
    """
    user_to_unfollow = User.query.filter_by(username=username).first()
    if not user_to_unfollow:
        return jsonify({'error': 'User not found'}), 404

    follow = Follow.query.filter_by(follower_id=current_user.id, followed_id=user_to_unfollow.id).first()
    if follow:
        db.session.delete(follow)
        db.session.commit()
        return jsonify({'message': f'Unfollowed {username}'}), 200

    return jsonify({'message': f'Not following {username}'}), 400

# Route: Delete a Comment
@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """
    Allow users to delete their own comments.
    """
    comment = Comment.query.get_or_404(comment_id)

    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('my_posts', filter='comments'))

# Route: Remove a Follower (API)
@app.route('/api/remove_follower/<string:username>', methods=['POST'])
@login_required
def remove_follower(username):
    """
    Remove a follower from the user's followers list.
    """
    follower_to_remove = User.query.filter_by(username=username).first()
    if not follower_to_remove:
        return jsonify({'error': 'User not found'}), 404

    follow_relationship = Follow.query.filter_by(follower_id=follower_to_remove.id, followed_id=current_user.id).first()
    if not follow_relationship:
        return jsonify({'error': 'This user is not your follower'}), 400

    db.session.delete(follow_relationship)
    db.session.commit()
    return jsonify({'message': f'{username} has been removed from your followers'}), 200
