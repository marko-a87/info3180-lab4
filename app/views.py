import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import UploadForm
from app.forms import LoginForm
from werkzeug.security import check_password_hash
from flask import send_from_directory

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


@app.route('/upload',  methods=['POST', 'GET'])
@login_required
def upload():
    # Instantiate your form class
    form = UploadForm()
    # Validate file upload on submit
    if request.method == 'GET':
        return render_template('upload.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            # Get file data and save to your uploads folder
            photo = form.file_upload.data
            photoname = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photoname))
        
            flash('File Saved', 'success')
            return redirect(url_for('files'))

@app.route('/uploads/<filename>')
@login_required
def get_image(filename):
    image = send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)
    return image
    

@app.route("/files")
@login_required
def files():
    images = get_uploadedimages()
    return render_template("files.html", images=images)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    # change this to actually validate the entire form submission
    # and not just one field
    if form.validate_on_submit():
        # Get the username and password values from the form.
        form_login_name = form.username.data
        form_login_password = form.password.data

        # Using your model, query database for a user based on the username
        # and password submitted. Remember you need to compare the password hash.
        # You will need to import the appropriate function to do so.
        # Then store the result of that query to a `user` variable so it can be
        # passed to the login_user() method below.
        user_Profile =db.session.execute(db.select(UserProfile).filter_by(username=form_login_name)).scalar()
        print(user_Profile)
        if user_Profile.username == form_login_name:
            if check_password_hash(user_Profile.password, form_login_password):
                # Gets user id, load into session
                login_user(user_Profile)
                flash('Logged in successfully.', 'success')
                return redirect(url_for("upload"))
        else:
            flash('Incorrect username or password.', 'danger')
    return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for("home"))


# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()


##
#helper function
##

def get_uploadedimages():
    list_of_images=[]
    rootdir = os.getcwd()
    directory = rootdir + "/" + app.config['UPLOAD_FOLDER']
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith(".gitkeep"):
                list_of_images.append(file)
    return list_of_images




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
