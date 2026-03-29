from flask import Flask,render_template,redirect, url_for, request, flash
from forms import RegistrationForm, LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, bcrypt, User
from config import Config
from flask_migrate import Migrate
import numpy as np
import pandas as pd
import pickle

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    bcrypt.init_app(app)
    Migrate(app, db)
    
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()



@app.route("/")
def index():
    return render_template('index.html')

@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        User.create_user(
            fullname=form.fullname.data,
            username=form.username.data,
            email=form.email.data,
            mobile_number=form.mobile_number.data,
            password=form.password.data
        )
        db.session.commit()
        flash('Account created successfully! You can now login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main'))
        else:
            flash('Login failed. Check username and password', 'danger')
    return render_template('login.html', form=form)


@app.route("/main")
@login_required
def main():
    return render_template('main.html',title='main')

@app.route("/about")
def about():
      return render_template('about.html')


@app.route("/termscondition")
def TermsCondition():
      return render_template('termscondition.html')


@app.route("/predict")
def predict():
    return render_template('predict.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))



#loading ML Model.
filename = 'heart_disease_model.pkl'
# model = pickle.load(open(filename, 'rb'))
model = pickle.load(open(filename, 'rb'))



@app.route('/predict', methods=['GET','POST'])
def predict_heartdisease():
      if request.method == 'POST':
            age = int(request.form['age'])
            sex = int(request.form.get('sex'))
            cp = int(request.form.get('cp'))
            trestbps = int(request.form['trestbps'])
            chol = int(request.form['chol'])
            fbs = int(request.form.get('fbs'))
            restecg = int(request.form['restecg'])
            thalach = int(request.form['thalach'])
            exang = int(request.form.get('exang'))
            oldpeak = float(request.form['oldpeak'])
            slope = int(request.form.get('slope'))
            ca = int(request.form['ca'])
            thal = int(request.form.get('thal'))
        
            data = np.array([[age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal]])
            my_prediction = model.predict(data)
            input_data_reshaped = data.reshape(1,-1)

            #Get Prediction probability
            prediction_proba = model.predict_proba(data)
            heart_disease_probability = prediction_proba[0][1]*100
            formated_probability = f"{int(heart_disease_probability)}%"


            return render_template('result.html', prediction = my_prediction, probability = formated_probability)
        


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0',port=8080)