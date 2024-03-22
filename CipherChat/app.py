import os
import uuid
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_cors import CORS
from flask_login import (
    LoginManager,
    login_required,
    logout_user,
    UserMixin,
    current_user,
    login_user,
)
from flask_migrate import Migrate
from flask_socketio import SocketIO, join_room, emit
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='/static')
socketio = SocketIO(app, logger=True, cors_allowed_origins="*")
CORS(app, resources={r"/static/*": {"origins": "*"}})
app.config["SECRET_KEY"] = "7841"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://cipherchat_db_user:FT0uWXBJicl634HLavOijeFEPxV4inPB@dpg-cnukjvcf7o1s739ogfdg-a/cipherchat_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join('static', 'uploads'))
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.init_app(app)


# Define the User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(255), nullable=False, default='')
    email = db.Column(db.String(50), unique=True, nullable=False)
    date_of_birth = db.Column(db.String(50), unique=False, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    profile_picture = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    sent_messages = db.relationship("Message", back_populates="sender", lazy=True, foreign_keys="Message.sender_id")
    received_messages = db.relationship("Message", back_populates="receiver", lazy=True, foreign_keys="Message.receiver_id")
    receiver = db.relationship("User", foreign_keys=[receiver_id])
    sender = db.relationship("User", foreign_keys=[sender_id])

    def __init__(self, username, password, name, email, date_of_birth, profile_picture, sender_id, receiver_id, content=''):
        self.username = username
        self.password = password  # Store password as plain text
        self.name = name
        self.email = email
        self.date_of_birth = date_of_birth
        self.profile_picture = profile_picture
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content

    def check_password(self, entered_password):
        return self.password == entered_password

    @staticmethod
    def search_users(term):
        matching_users = User.query.filter(User.username.ilike(f"%{term}%")).all()
        usernames = [user.username for user in matching_users]
        return usernames


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    sender = db.relationship('User', back_populates='sent_messages', foreign_keys=[receiver_id], overlaps="received_messages")
    receiver = db.relationship('User', back_populates='received_messages', foreign_keys=[receiver_id], overlaps="sender")

    def __repr__(self):
        return f"<Message {self.id}>"

    def messages_with(self, other_user):
        return Message.query.filter(
            ((Message.sender_id == self.sender_id) & (Message.receiver_id == other_user.id)) |
            ((Message.sender_id == other_user.id) & (Message.receiver_id == self.sender_id))
        ).order_by(Message.timestamp)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/profile")
@login_required
def profile():
    user = current_user
    return render_template("profile.html", user=user)


@app.route("/save_settings", methods=["POST"])
@login_required
def save_settings():
    if request.method == "POST":
        # Get the current user
        user = current_user

        # Update user information based on the form data
        user.username = request.form.get("username")

        if "profile_picture" in request.files:
            profile_picture = request.files["profile_picture"]
            if profile_picture.filename != "":
                filename = secure_filename(f"{uuid.uuid4().hex}.png")
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                profile_picture.save(file_path)
                user.profile_picture = file_path

        new_password = request.form.get("password")
        if new_password:
            user.password = new_password

        # Commit changes to the database
        db.session.commit()

        # Optionally, you can flash a message to indicate success
        flash("Settings updated successfully!", "success")

        # Redirect to the updated settings or profile page
        return redirect(url_for("profile"))

    # Handle other HTTP methods, if needed
    return render_template("settings.html")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        # Get the username entered in the search form
        search_username = request.form.get("search_username")

        # Search for the user in the database
        user = User.query.filter_by(username=search_username).first()

        if user:
            # Redirect to the dynamically created chat endpoint
            return redirect(url_for("chat", receiver_username=user.username))
        else:
            flash("User not found. Please try again.", "warning")

    # Render the search page template
    return render_template("search.html")


@login_required
@app.route("/search_users", methods=["GET"])
def search_users():
    term = request.args.get("term", "").lower()
    matching_users = User.search_users(term)
    return jsonify(matching_users)


@login_required
@app.route("/chat/<receiver_username>")
def chat(receiver_username):
    # Check if the user is logged in
    if current_user.is_authenticated:
        # Fetch the current user from the database based on the logged-in user
        user = current_user

        # Fetch the receiver user from the database based on the provided username
        receiver_user = User.query.filter_by(username=receiver_username).first()

        # Check if both users exist before proceeding
        if user and receiver_user:
            # Fetch messages from the database based on the current user and receiver user
            messages = Message.query.filter(
                ((Message.sender_id == user.id) & (Message.receiver_id == receiver_user.id))
                | (
                    (Message.sender_id == receiver_user.id)
                    & (Message.receiver_id == user.id)
                )
            ).all()

            # Fetch a list of users involved in the chat for the sidebar
            users = [user, receiver_user]

            return render_template(
                "chat.html",
                user=user,
                receiver=receiver_user,
                messages=messages,
                users=users,
            )
        else:
            # Handle the case where either the current user or receiver user is not found
            flash("User not found. Please try again.", "warning")
            return redirect(url_for("index"))

    # If the user is not authenticated, you can redirect them to the login page
    flash("Please log in to access the chat.", "warning")
    return redirect(url_for("login"))


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)
    print(f"User joined room: {room}")


@socketio.on('send_message')
def handle_message(data):
    app.logger.info(f"Received message: {data}")
    # Extracting data from the received message
    receiver = data.get('receiver')
    content = data.get('content')
    sender_username = data.get('sender')

    # Checking for missing information
    if not all([receiver, content, sender_username]):
        # If any required information is missing, return an error response
        return {'error': 'Receiver, content, or sender missing'}, 400

    # Ensure the sender exists in the database
    sender = User.query.filter_by(username=sender_username).first()

    if sender:
        # Fetch the receiver user from the database based on the provided username
        receiver_user = User.query.filter_by(username=receiver).first()

        if receiver_user:
            # Create a new message and add it to the database
            new_message = Message(sender=sender, receiver=receiver_user, content=content)
            db.session.add(new_message)
            db.session.commit()

            # Broadcast the received message to all connected clients in the 'receiver' room
            sender_room = receiver
            receiver_room = sender
            # Example for sender
            socketio.emit('receive_message', {'sender': sender_username, 'content': content}, room=sender_room)
            # Example for receiver
            socketio.emit('receive_message', {'sender': sender_username, 'content': content}, room=receiver_room)

            # Return a success response
            return {'success': True}

    # If the sender or receiver doesn't exist, return an error response
    return {'error': 'Sender or receiver not found in the database'}, 400


# Socket.io event handlers
@app.route("/fetch_messages", methods=["GET"])
@login_required
def fetch_messages():
    if request.method == "GET":
        # Fetch new messages from the database
        receiver_username = request.args.get('receiver')
        messages = Message.query.filter_by(receiver=receiver_username).all()
        message_data = [{'sender': message.sender.username, 'content': message.content} for message in messages]
        print("Fetched messages:", message_data)
        return jsonify({'messages': message_data})


@socketio.on('error')
def handle_error(event):
    print('WebSocket Error:', event)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        # Handle form submissions
        new_password = request.form.get("new_password")
        new_username = request.form.get("new_username")

        # Update user information in the database
        if new_password:
            current_user.password = new_password  # Store new password as plain text
        if new_username:
            current_user.username = new_username

        db.session.commit()

        # Optionally, you can flash a message to indicate success
        flash("Settings updated successfully!", "success")

        # Redirect to the updated settings or profile page
        return redirect(url_for("settings"))

    # Render the settings page with the current user's information
    return render_template("profile.html", user=current_user)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]
        name = request.form["name"]
        date_of_birth = request.form["date_of_birth"]
        email = request.form["email"]
        profile_picture = request.files["profile_picture"]

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for("register"))

        # Ensure a file is selected for profile_picture
        if profile_picture.filename == "":
            flash("Profile picture is required.", "danger")
            return redirect(url_for("register"))

        # Save the uploaded file to a secure location
        filename = secure_filename(profile_picture.filename)
        filename = os.path.basename(filename)  # Remove relative path
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_picture.save(file_path)

        new_user = User(
            username=username,
            password=password,
            name=name,
            email=email,
            date_of_birth=date_of_birth,
            content='',
            profile_picture=filename,
            sender_id=User.id,
            receiver_id=User.id
        )

        db.session.add(new_user)
        db.session.commit()

        new_user.sender_id = new_user.id
        new_user.content = "Welcome to CipherChat! Feel free to start chatting."
        new_user.receiver_id = new_user.id

        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        entered_password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(entered_password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(
                url_for("search")
            )

        else:
            flash("Invalid username or password, please try again!", "error")
            return redirect(url_for("login"))

    if current_user.is_authenticated:
        return redirect(url_for("search"))

    return render_template("login.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    if request.method == "POST":
        logout_user()
        flash("Logout successful!", "success")
        return redirect(url_for("login"))
    else:
        # Handle GET request, if needed
        return render_template("logout.html")


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form.get("username")
        date_of_birth = request.form.get("date_of_birth")

        # Check if date_of_birth is None or empty
        if not date_of_birth:
            flash("Please provide your date of birth for password recovery.", "danger")
            return redirect(url_for("forgot_password"))

        try:
            date_of_birth = datetime.strptime(date_of_birth, "%m-%d-%Y")

            user = User.query.filter_by(
                username=username,
                date_of_birth=date_of_birth,
            ).first()

            if user:
                flash(
                    "Password changes successfully, you can login with new password :).",
                    "info",
                )
            else:
                flash("Invalid username or date of birth. Please try again.", "danger")

            return redirect(url_for("login"))

        except ValueError:
            flash("Invalid date of birth format. Please use MM-DD-YYYY.", "danger")
            return redirect(url_for("forgot_password"))

    return render_template("forgot_password.html")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, host="0.0.0.0", debug=False)
