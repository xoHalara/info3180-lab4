import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import LoginForm, UploadForm
from werkzeug.security import check_password_hash


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")

def get_uploaded_images():
    """Returns a list of image filenames in the uploads folder."""
    image_list = []
    upload_folder = os.path.join(os.getcwd(), app.config["UPLOAD_FOLDER"])
    print("DEBUG: Checking files in", upload_folder)  # This will show the folder path

    if not os.path.exists(upload_folder):
        print("DEBUG: Upload folder does not exist.")
    else:
        for filename in os.listdir(upload_folder):
            if filename.endswith((".png", ".jpg", ".jpeg")):
                image_list.append(filename)
    
    return image_list


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    # Instantiate your form class
    form = UploadForm()

    # Validate file upload on submit
    if form.validate_on_submit():
        # Get file data and save to your uploads folder
        photo = form.photo.data
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        flash('File Saved', 'success')
        return redirect(url_for('files')) # Update this to redirect the user to a route that displays all uploaded image files

    return render_template('upload.html', form=form)

@app.route('/uploads/<filename>')
def get_image(filename):
    """Serves an uploaded image from the uploads folder."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route('/files')
@login_required
def files():
    """Displays a list of uploaded image files."""
    images = get_uploaded_images()
    print("DEBUG: Images found:", images)

    if not images:
        flash("No images found. Please upload new files.", "warning")

    return render_template("files.html", images = images)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    
    form = LoginForm()

    # change this to actually validate the entire form submission
    # and not just one field
    if form.validate_on_submit():
        # Get the username and password values from the form.

        username = form.username.data
        password = form.password.data
        user = UserProfile.query.filter_by(username=username).first()

        if user is not None and check_password_hash(user.password, password):
        # Gets user id, load into session
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for("upload"))  # The user should be redirected to the upload form instead
        else:
            flash('Username or Password is incorrect.', 'danger')
            
    return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    """Logs out the current user."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
