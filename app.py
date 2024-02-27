import os
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app
import re
app = Flask(__name__)

# Initialize Firebase Admin
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred, {
    # If you're using Firebase Storage, specify your bucket name here
    # 'storageBucket': 'your-bucket-name.appspot.com'
})
db = firestore.client()

@app.route('/profile', methods=['POST'])
def create_profile():
    # Expecting JSON data now
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.json
    name = data.get('name')
    if not name:
        return jsonify({"error": "Name is required"}), 400

    # Directly using the provided JSON data
    profile_data = {
        "name": name,
        "date_of_birth": data.get("date_of_birth"),
        "place_of_birth": data.get("place_of_birth"),
        "complexion": data.get("complexion"),
        "height": data.get("height"),
        "gotra": data.get("gotra"),
        "kshatriya": data.get("kshatriya"),
        "education_details": data.get("education_details", []),
        "work": data.get("work"),
        "family_details": data.get("family_details", {}),
        "contact_details": data.get("contact_details", {})
       # This can be a direct URL to an image
    }

    # Add profile data to Firestore
    db.collection('profiles').document(data.get("email", {})).set(profile_data)

    return jsonify({"message": "Profile created successfully", "profile": profile_data}), 201


def validate_email(email):
    # Regular expression for validating an email
    pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    if pattern.match(email):
        return True
    else:
        return False

@app.route('/signup',methods=['POST'])
def signup():
    if not request.json:
        return jsonify({"status:":"error","message":"Request must be JSON"}), 400
    
    email=request.json.get('email')
    password=request.json.get('password')
    
    doc_ref=db.collection('user').document(email)
    if doc_ref.get().exists:
        return jsonify({"status":"error","message":"User already exists"}), 400
    
    if validate_email(email)==False:
        return jsonify({"status":"error","message":"Invalid email"}), 400
    
    if check_password(password)==False:
        return jsonify({"status":"error","message":"Invalid password"}), 400
    
    
    doc_ref.set({
        'password':password
    })
    return jsonify({"status":"success","message":"User created successfully"}), 201
        
def check_password(password):
    # Regular expression to check if password is strong
    # ^(?=.*[a-z])      : Ensure string has one lowercase letter.
    # (?=.*[A-Z])       : Ensure string has one uppercase letter.
    # (?=.*\d)          : Ensure string has one digit.
    # (?=.*[!@#$%^&*])  : Ensure string has one special character.
    # .{8,}             : Ensure string is of length 8.
    pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}$')

    if pattern.match(password):
        return True
    else:
        return False
    
    
@app.route('/login',methods=['GET'])
def login():
    
    email=request.args.get('email')
    password=request.args.get('password')
    
    
    doc_ref=db.collection('user').document(email)
    if not doc_ref.get().exists:
        return jsonify({"status":"error","message":"User does not exist"}), 400
    
    doc=doc_ref.get()
    if doc.to_dict()['password']!=password:
        return jsonify({"status":"error","message":"Invalid password"}), 400
    
    return jsonify({"status":"success","message":"User logged in successfully"}), 200    
        
 
@app.route('/get-profile', methods=['GET'])
def get_profile():
    email = request.args.get('email')
    if email is None:
        return jsonify({"error": "Missing email query parameter"}), 400

    try:
        # Fetch the document with ID equal to email
        doc_ref = db.collection('profiles').document(email)
        doc = doc_ref.get()
        if doc.exists:
            return jsonify(doc.to_dict()), 200
        else:
            return jsonify({"error": "Profile not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
