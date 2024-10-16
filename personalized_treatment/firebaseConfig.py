
# const firebaseConfig = {
#   apiKey: "AIzaSyAjE6aZDkaF04kS15L-_NDqAYNONMaAOwU",
#   authDomain: "personalized-medical-assistant.firebaseapp.com",
#   projectId: "personalized-medical-assistant",
#   storageBucket: "personalized-medical-assistant.appspot.com",
#   messagingSenderId: "617362904745",
#   appId: "1:617362904745:web:4f17cefe5d9365c136bbb8",
#   measurementId: "G-CMCPK6R78W"
# };
import pyrebase

firebaseConfig = {
  "apiKey": "AIzaSyAjE6aZDkaF04kS15L-_NDqAYNONMaAOwU",
  "authDomain": "personalized-medical-assistant.firebaseapp.com",
  "databaseURL": "https://personalized-medical-assistant-default-rtdb.asia-southeast1.firebasedatabase.app/",
  "projectId": "personalized-medical-assistant",
  "storageBucket": "personalized-medical-assistant.appspot.com",
  "messagingSenderId": "617362904745",
  "appId": "1:617362904745:web:4f17cefe5d9365c136bbb8",
  "measurementId": "G-CMCPK6R78W"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()  # Optional, only if you use Realtime DB (can be skipped if using Firestore)
