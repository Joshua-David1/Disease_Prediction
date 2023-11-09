from flask import (
    Flask,
    redirect,
    url_for,
    render_template,
    request,
    session,
    g,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, UserMixin, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import (
    DataRequired,
    ValidationError,
    InputRequired,
    Regexp,
    EqualTo,
)
from datetime import timedelta
from collections import defaultdict

app = Flask(__name__)
app.config["SECRET_KEY"] = "NothingMuch"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user-data-collection.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = "OFF"
db = SQLAlchemy(app)

# classes


class TestNewData(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(25), nullable=False)
    test_value = db.Column(db.Integer, nullable=False)
    tester_email = db.Column(db.Integer, nullable=False)
    patient_id = db.Column(db.Integer, nullable=False)
    patient_name = db.Column(db.String(25), nullable=False)


class AllocatedPatient_Spec(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(25), nullable=False)
    spec_id = db.Column(db.String(25), nullable=False)


class AllocatedPatients_Doc(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=False)
    doctor_id = db.Column(db.Integer, nullable=False)


class HealthCare(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(25), unique=True, nullable=False)
    name = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(25), nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(25), unique=True, nullable=False)
    name = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(25), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    designation = db.Column(db.String(25), nullable=False)
    years_of_exp = db.Column(db.Integer)
    healthcare_id = db.Column(db.Integer, nullable=False)


with app.app_context():
    db.create_all()


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=10)
    session.modified = True
    g.user = current_user


###get value functions


def get_id(email):
    id_ = HealthCare.query.filter_by(email=email).first()
    return id_.id


def check_password(email, password):
    user = User.query.filter_by(email=email).first()
    if password == user.password:
        return True
    return False


def get_healthcare(email):
    hc_id = User.query.filter_by(email=email).first().healthcare_id
    return hc_id


def get_hc_name(id_):
    hc_name = HealthCare.query.filter_by(id=id_).first().name
    return hc_name


def get_designation(email):
    designation = User.query.filter_by(email=email).first().designation
    return designation


def match_pair(doctor, patient):
    new_data = AllocatedPatients_Doc(patient_id=patient, doctor_id=doctor)
    db.session.add(new_data)
    db.session.commit()


def check_unmatched(patients):
    l = []
    for patient in patients:
        if AllocatedPatients_Doc.query.filter_by(patient_id=patient.id).first() is None:
            l.append(patient)
    return l


def get_doc_pair(doc_id):
    patients = AllocatedPatients_Doc.query.filter_by(doctor_id=doc_id).all()
    data_map = {}
    for pat in patients:
        user = User.query.filter_by(id=pat.patient_id).first()
        data_map[user.id] = {"email": user.email, "age": user.age, "name": user.name}
    return data_map


###


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/lifestyle")
def lifestyle_home():
    return "haha"


@app.route("/healthcare")
def healthcare_home():
    return render_template("healthcare_home.html")


###########################################################################SPECIALIST####################


@app.route("/healthcare/view_my_patients_spc")
def healthcare_view_spc():
    email = request.args.get("email")
    id = User.query.filter_by(email=email).first().healthcare_id
    patients = User.query.filter_by(healthcare_id=id, designation="patient").all()
    data_map = {}
    for pat in patients:
        data_map[pat.id] = {"name": pat.name, "email": pat.email, "age": pat.age}

    return data_map


@app.route("/healthcare/smoke", methods=["POST", "GET"])
def healthcare_smoke():
    if request.method == "POST":
        id = request.form["id"]
        email = request.form["email"]
        val = request.form["value"]
        patient_id = request.form["patient_id"]
        data = TestNewData(
            test_name="smoke",
            test_value=int(val),
            tester_email=email,
            patient_id=patient_id,
            patient_name=User.query.filter_by(id=patient_id).first().name,
        )
        db.session.add(data)
        db.session.commit()
    else:
        id = request.args.get("id")
        email = request.args.get("email")
    user = User.query.filter_by(email=email).first()
    data = {
        "spc_name": user.name,
        "hc_id": id,
        "hc_name": HealthCare.query.filter_by(id=id).first().name,
        "email": email,
        "desig": user.designation,
    }
    avail_patients = User.query.filter_by(healthcare_id=id, designation="patient").all()
    display_patients = TestNewData.query.filter_by(
        tester_email=email, test_name="smoke"
    ).all()
    data["display_patients"] = display_patients
    data["available_patients"] = avail_patients
    return render_template("smoke.html", data=data)


@app.route("/healthcare/cholestrol", methods=["POST", "GET"])
def healthcare_cholestrol():
    if request.method == "POST":
        id = request.form["id"]
        email = request.form["email"]
        val = request.form["value"]
        patient_id = request.form["patient_id"]
        data = TestNewData(
            test_name="cholestrol",
            test_value=int(val),
            tester_email=email,
            patient_id=patient_id,
            patient_name=User.query.filter_by(id=patient_id).first().name,
        )
        db.session.add(data)
        db.session.commit()
    else:
        id = request.args.get("id")
        email = request.args.get("email")
    user = User.query.filter_by(email=email).first()
    data = {
        "spc_name": user.name,
        "hc_id": id,
        "hc_name": HealthCare.query.filter_by(id=id).first().name,
        "email": email,
        "desig": user.designation,
    }
    avail_patients = User.query.filter_by(healthcare_id=id, designation="patient").all()
    display_patients = TestNewData.query.filter_by(
        tester_email=email, test_name="cholestrol"
    ).all()
    data["display_patients"] = display_patients
    data["available_patients"] = avail_patients
    return render_template("cholestrol.html", data=data)


@app.route("/healthcare/height", methods=["POST", "GET"])
def healthcare_height():
    if request.method == "POST":
        id = request.form["id"]
        email = request.form["email"]
        val = request.form["value"]
        patient_id = request.form["patient_id"]
        data = TestNewData(
            test_name="height",
            test_value=int(val),
            tester_email=email,
            patient_id=patient_id,
            patient_name=User.query.filter_by(id=patient_id).first().name,
        )
        db.session.add(data)
        db.session.commit()
    else:
        id = request.args.get("id")
        email = request.args.get("email")
    user = User.query.filter_by(email=email).first()
    data = {
        "spc_name": user.name,
        "hc_id": id,
        "hc_name": HealthCare.query.filter_by(id=id).first().name,
        "email": email,
        "desig": user.designation,
    }
    avail_patients = User.query.filter_by(healthcare_id=id, designation="patient").all()
    display_patients = TestNewData.query.filter_by(
        tester_email=email, test_name="height"
    ).all()
    data["display_patients"] = display_patients
    data["available_patients"] = avail_patients
    return render_template("height.html", data=data)


@app.route("/healthcare/weight", methods=["POST", "GET"])
def healthcare_weight():
    if request.method == "POST":
        id = request.form["id"]
        email = request.form["email"]
        val = request.form["value"]
        patient_id = request.form["patient_id"]
        data = TestNewData(
            test_name="weight",
            test_value=int(val),
            tester_email=email,
            patient_id=patient_id,
            patient_name=User.query.filter_by(id=patient_id).first().name,
        )
        db.session.add(data)
        db.session.commit()
    else:
        id = request.args.get("id")
        email = request.args.get("email")
    user = User.query.filter_by(email=email).first()
    data = {
        "spc_name": user.name,
        "hc_id": id,
        "hc_name": HealthCare.query.filter_by(id=id).first().name,
        "email": email,
        "desig": user.designation,
    }
    avail_patients = User.query.filter_by(healthcare_id=id, designation="patient").all()
    display_patients = TestNewData.query.filter_by(
        tester_email=email, test_name="weight"
    ).all()
    data["display_patients"] = display_patients
    data[
        "available_patients"
    ] = avail_patients  #     return redirect("/healthcare/login")
    return render_template("weight.html", data=data)


@app.route("/healthcare/alco", methods=["GET", "POST"])
def healthcare_alcohol():
    # if current_user.is_authenticated == False:
    #     return redirect("/healthcare/login")
    if request.method == "POST":
        id = request.form["id"]
        email = request.form["email"]
        val = request.form["value"]
        patient_id = request.form["patient_id"]
        data = TestNewData(
            test_name="alco",
            test_value=int(val),
            tester_email=email,
            patient_id=patient_id,
            patient_name=User.query.filter_by(id=patient_id).first().name,
        )
        db.session.add(data)
        db.session.commit()
    else:
        id = request.args.get("id")
        email = request.args.get("email")
    user = User.query.filter_by(email=email).first()
    data = {
        "spc_name": user.name,
        "hc_id": id,
        "hc_name": HealthCare.query.filter_by(id=id).first().name,
        "email": email,
        "desig": user.designation,
    }
    avail_patients = User.query.filter_by(healthcare_id=id, designation="patient").all()
    display_patients = TestNewData.query.filter_by(
        tester_email=email, test_name="alco"
    ).all()
    data["display_patients"] = display_patients
    data["available_patients"] = avail_patients
    return render_template("alco.html", data=data)


@app.route("/healthcare/gluc", methods=["POST", "GET"])
def healthcare_gluc():
    # if current_user.is_authenticated == False:
    #     return redirect("/healthcare/login")
    if request.method == "POST":
        id = request.form["id"]
        email = request.form["email"]
        val = request.form["value"]
        patient_id = request.form["patient_id"]
        data = TestNewData(
            test_name="gluc",
            test_value=int(val),
            tester_email=email,
            patient_id=patient_id,
            patient_name=User.query.filter_by(id=patient_id).first().name,
        )
        db.session.add(data)
        db.session.commit()
    else:
        id = request.args.get("id")
        email = request.args.get("email")
    user = User.query.filter_by(email=email).first()
    data = {
        "spc_name": user.name,
        "hc_id": id,
        "hc_name": HealthCare.query.filter_by(id=id).first().name,
        "email": email,
        "desig": user.designation,
    }
    avail_patients = User.query.filter_by(healthcare_id=id, designation="patient").all()
    display_patients = TestNewData.query.filter_by(
        tester_email=email, test_name="gluc"
    ).all()
    data["display_patients"] = display_patients
    data["available_patients"] = avail_patients
    return render_template("gluc.html", data=data)


@app.route("/healthcare/ap_hi", methods=["POST", "GET"])
def healthcare_ap_hi():
    # if current_user.is_authenticated == False:
    #     return redirect("/healthcare/login")
    if request.method == "POST":
        id = request.form["id"]
        email = request.form["email"]
        val = request.form["value"]
        patient_id = request.form["patient_id"]
        data = TestNewData(
            test_name="ap_hi",
            test_value=int(val),
            tester_email=email,
            patient_id=patient_id,
            patient_name=User.query.filter_by(id=patient_id).first().name,
        )
        db.session.add(data)
        db.session.commit()
    else:
        id = request.args.get("id")
        email = request.args.get("email")
    user = User.query.filter_by(email=email).first()
    data = {
        "spc_name": user.name,
        "hc_id": id,
        "hc_name": HealthCare.query.filter_by(id=id).first().name,
        "email": email,
        "desig": user.designation,
    }
    avail_patients = User.query.filter_by(healthcare_id=id, designation="patient").all()
    display_patients = TestNewData.query.filter_by(
        tester_email=email, test_name="ap_hi"
    ).all()
    data["display_patients"] = display_patients
    data["available_patients"] = avail_patients
    return render_template("ap_hi.html", data=data)


@app.route("/healthcare/ap_lo", methods=["POSt", "GET"])
def healthcare_ap_lo():
    if request.method == "POST":
        id = request.form["id"]
        email = request.form["email"]
        val = request.form["value"]
        patient_id = request.form["patient_id"]
        data = TestNewData(
            test_name="ap_lo",
            test_value=int(val),
            tester_email=email,
            patient_id=patient_id,
            patient_name=User.query.filter_by(id=patient_id).first().name,
        )
        db.session.add(data)
        db.session.commit()
    else:
        id = request.args.get("id")
        email = request.args.get("email")
    user = User.query.filter_by(email=email).first()
    data = {
        "spc_name": user.name,
        "hc_id": id,
        "hc_name": HealthCare.query.filter_by(id=id).first().name,
        "email": email,
        "desig": user.designation,
    }
    avail_patients = User.query.filter_by(healthcare_id=id, designation="patient").all()
    display_patients = TestNewData.query.filter_by(
        tester_email=email, test_name="ap_lo"
    ).all()
    data["display_patients"] = display_patients
    data["available_patients"] = avail_patients
    return render_template("ap_lo.html", data=data)


##################LOG REG#######################


@app.route("/healthcare/login", methods=["POST", "GET"])
def healthcare_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        print(email, password)
        if check_password(email, password):
            user = User.query.filter_by(email=email).first()
            login_user(user)
            print(
                user.name,
                user.email,
                user.password,
                user.designation,
                user.healthcare_id,
                user.age,
            )
            health_care_id = get_healthcare(email=email)
            hc_name = get_hc_name(health_care_id)
            designation = get_designation(email=email)
            if designation == "admin":
                return redirect(f"/healthcare/admin?id={health_care_id}")
            elif designation == "doctor":
                return redirect(f"/healthcare/doctor?id={health_care_id}&email={email}")
            elif designation == "smoke":
                return redirect(f"/healthcare/smoke?id={health_care_id}&email={email}")
            elif designation == "cholestrol":
                return redirect(
                    f"/healthcare/cholestrol?id={health_care_id}&email={email}"
                )
            elif designation == "height":
                return redirect(f"/healthcare/height?id={health_care_id}&email={email}")
            elif designation == "weight":
                return redirect(f"/healthcare/weight?id={health_care_id}&email={email}")
            elif designation == "alco":
                return redirect(f"/healthcare/alco?id={health_care_id}&email={email}")
            elif designation == "gluc":
                return redirect(f"/healthcare/gluc?id={health_care_id}&email={email}")
            elif designation == "ap_lo":
                return redirect(f"/healthcare/ap_lo?id={health_care_id}&email={email}")
            elif designation == "ap_hi":
                return redirect(f"/healthcare/ap_hi?id={health_care_id}&email={email}")
            elif designation == "patient":
                return redirect(
                    f"/healthcare/patient?id={health_care_id}&email={email}"
                )
    return render_template("healthcare_login.html")


@app.route("/healthcare/register", methods=["GET", "POST"])
def healthcare_register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        new_user = HealthCare(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        id_ = get_id(email)
        new_user = User(
            name=name,
            email=email,
            password=password,
            designation="admin",
            age=30,
            healthcare_id=id_,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(f"/healthcare/admin?id={id_}")
    return render_template("healthcare_register.html")


#############ADMIN ONLY###################


@app.route("/healthcare/admin")
def healthcare_admin():
    print(current_user.is_authenticated)
    # if current_user.is_authenticated == False:
    #     return redirect("/healthcare/login")
    hc_id = request.args.get("id")
    hc_name = HealthCare.query.filter_by(id=hc_id).first()
    if hc_name == None:
        hc_name = "Default"
    else:
        hc_name = hc_name.name
    data = {"hc_id": hc_id, "hc_name": hc_name}
    return render_template("admin.html", data=data)


@app.route("/healthcare/create_profile", methods=["GET", "POST"])
def create_profile():
    # if current_user.is_authenticated == False:
    #     return redirect("/healthcare/login")
    hc_id = request.args.get("id")
    # if hc_id == None:
    #     return redirect("/healthcare/login")
    if request.method == "POST":
        email = request.form["email"]
        name = request.form["name"]
        password = request.form["password"]
        age = int(request.form["age"])
        designation = request.form["designation"]
        hc_id = request.form["hc_id"]
        new_user = User(
            email=email,
            password=password,
            name=name,
            designation=designation,
            age=age,
            healthcare_id=int(hc_id),
        )
        db.session.add(new_user)
        db.session.commit()

    return render_template("creat_profile.html", hc_id=hc_id)


@app.route("/healthcare/view_doctors")
def healthcare_view_doctors():
    # if current_user.is_authenticated == False:
    #     return redirect("/healthcare/login")
    hc_id = request.args.get("id")
    doctors = User.query.filter_by(healthcare_id=hc_id, designation="doctor").all()
    data_map = {}
    for doctor in doctors:
        data_map[doctor.id] = {
            "email": doctor.email,
            "name": doctor.name,
            "age": doctor.age,
        }
    return jsonify({"Doctors": data_map})


@app.route("/healthcare/view_patients")
def healthcare_view_patients():
    # if current_user.is_authenticated == False:
    #     return redirect("/healthcare/login")
    hc_id = request.args.get("id")
    patients = User.query.filter_by(healthcare_id=hc_id, designation="patient").all()
    data_map = {}
    for patient in patients:
        data_map[patient.id] = {
            "email": patient.email,
            "name": patient.name,
            "age": patient.age,
        }
    return jsonify({"Patients": data_map})


@app.route("/healthcare/<specialist>")
def healthcare_view_specialists(specialist):
    # if current_user.is_authenticated == False:
    #     return redirect("/healthcare/login")
    hc_id = request.args.get("id")
    specialists = User.query.filter_by(
        healthcare_id=hc_id, designation=specialist
    ).all()
    data_map = {}
    for specia in specialists:
        data_map[specia.id] = {
            "email": specia.email,
            "name": specia.name,
            "age": specia.age,
        }
    return jsonify({specialist: data_map})


@app.route("/healthcare/pair", methods=["POST", "GET"])
def healthcare_pair():
    # if current_user.is_authenticated == False:
    #     return redirect("/healthcare/login")

    if request.method == "POST":
        doctor = int(request.form["doctor"])
        patient = int(request.form["patient"])
        id = int(request.form["id"])
        match_pair(doctor=doctor, patient=patient)
        return redirect(f"/healthcare/admin?id={id}")

    hc_id = request.args.get("id")
    patients = User.query.filter_by(
        healthcare_id=int(hc_id), designation="patient"
    ).all()
    patients = check_unmatched(patients)
    doctors = User.query.filter_by(healthcare_id=int(hc_id), designation="doctor").all()
    data = {"doctors": doctors, "patients": patients, "id": int(hc_id)}
    return render_template("pair_doc.html", data=data)


#######DOCTOR############


@app.route("/healthcare/doctor")
def healthcare_doctor():
    # if current_user.is_authenticated == False:
    #     return redirect("/healthcare/login")
    hc_id = request.args.get("id")
    email = request.args.get("email")
    hc_name = HealthCare.query.filter_by(id=hc_id).first().name
    data = {
        "hc_id": hc_id,
        "hc_name": hc_name,
        "doc_name": User.query.filter_by(email=email).first().name,
        "email": email,
    }
    return render_template("doctor.html", data=data)


@app.route("/healthcare/view_my_patients")
def healthcare_view_my_patients():
    email = request.args.get("email")
    id = User.query.filter_by(email=email).first().id
    data_map = get_doc_pair(id)
    return jsonify({"Patient": data_map})


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/healthcare/login")


#######################PATIENT#################


@app.route("/healthcare/patient")
def healthcare_patient():
    hc_id = request.args.get("id")
    email = request.args.get("email")
    cols = defaultdict(list)
    user = User.query.filter_by(email=email).first()
    patient_id = user.id
    print(patient_id)
    name = user.name
    datas = TestNewData.query.filter_by(patient_id=patient_id).all()
    for data in datas:
        cols[data.test_name].append(data.test_value)
    cols["name"] = name
    cols["hc_name"] = HealthCare.query.filter_by(id=hc_id).first().name
    doc_id = AllocatedPatients_Doc.query.filter_by(patient_id=patient_id).first()
    if doc_id != None:
        doc_id = doc_id.doctor_id
    cols["doctor_id"] = doc_id
    cols["doctor_name"] = (
        User.query.filter_by(
            id=AllocatedPatients_Doc.query.filter_by(patient_id=patient_id)
            .first()
            .doctor_id
        )
        .first()
        .name
        if doc_id is not None
        else None
    )
    return render_template("patient.html", data=cols)


#########################SECRET#############


@app.route("/healthcare/all")
def healthcare_all():
    user = User.query.filter_by().all()
    data_map = {}
    for u in user:
        data_map[u.id] = {
            "name": u.name,
            "email": u.email,
            "password": u.password,
            "designation": u.designation,
            "age": u.age,
            "health_care": u.healthcare_id,
        }
    return jsonify({"Data": data_map})


if __name__ == "__main__":
    app.run(debug=True)
