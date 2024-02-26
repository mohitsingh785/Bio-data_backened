from flask import Flask, request, jsonify
import os
from firebase_admin import credentials, firestore, initialize_app

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
