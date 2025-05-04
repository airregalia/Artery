from flask import Flask, request, jsonify, render_template
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder



# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# File path options for general_location
file_options = {
    1: "A2-Nadia.xlsx",
    2: "A2-Bhagalpur.xlsx",
    3: "A2-Bahraich.xlsx",
    4: "A2-Ballia_Bhojpur.xlsx",
    5: "A2-N24P.xlsx",
    6: "Z-Ballia.xlsx",
    7: "Z-Bhojpur.xlsx"

}

def feas(lat, long, l):
    if l == 1:
        if lat >= 23.090 and lat <= 23.130 and long >= 88.615 and long <= 88.675:
            return 1
        else:
            return 0
    if l == 2:
        if lat >= 25.325 and lat <= 25.370 and long >= 87.365 and long <= 87.415:
            return 1
        else:
            return 0
    if l == 3:
        if lat >= 27.600 and lat <= 27.640 and long >= 81.510 and long <= 81.565:
            return 1
        else:
            return 0
    if l == 4:
        if ((lat >= 25.745 and lat <= 25.805 and long >= 84.475 and long <= 84.510) or
            (lat >= 25.655 and lat <= 25.700 and long >= 84.610 and long <= 84.660)):
            return 1
        else:
            return 0
    if l == 5:
        if lat >= 22.720 and lat <= 22.770 and long >= 88.665 and long <= 88.720:
            return 1
        else:
            return 0

    
    

# Default route for the root URL
@app.route('/')
def home():
    # Render the form from the index.html template
    return render_template('index.html')

# Route for prediction
@app.route('/predict-depths', methods=['POST'])
def predict_depths():
    try:
        print("Request data:", request.json)  # Debug input data
        # Parse the input JSON
        input_data = request.json
        general_location = input_data.get('general_location')
        latitude = input_data.get('latitude')
        longitude = input_data.get('longitude')
        depth = input_data.get('depth')
        print("Inputs received:", general_location, latitude, longitude,depth)  # Debug parsed inputs

        # Validate inputs
        if not general_location or not latitude or not longitude:
            return jsonify({'error': 'Missing required inputs'}), 400
        if general_location not in file_options:
            return jsonify({'error': f'Invalid general_location: {general_location}'}), 400

        # Load the file
        file_path = file_options[general_location]
        data = pd.read_excel(file_path)

        if depth<40:
            return jsonify({'error': 'Please enter depth greater than 40ft'}), 400
        

        if (feas(latitude,longitude,general_location)==0):
            return jsonify({'error': 'Latitude/Longitude Out of Bounds for the Selected Region'}), 400
        
        # Prepare features and target
        X = data[['Lat', 'Long', 'Depth']]
        y = data['A']
        
        # Encode target variable
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, stratify=y_encoded, random_state=42
        )
        
        # Define the parameter grid for hyperparameter tuning
        param_grid = {
            'n_estimators': [100],       # Number of trees in the forest
            'max_depth': [None],          # Maximum depth of the trees
            'min_samples_split': [2],      # Minimum samples required to split an internal node
            'min_samples_leaf': [1],        # Minimum samples required to be at a leaf node
        }

        # Initialize Random Forest Classifier
        rf = RandomForestClassifier(random_state=42)    

        # Stratified K-Fold for GridSearchCV
        stratified_kf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

        # Initialize GridSearchCV for hyperparameter tuning
        grid_search = GridSearchCV(
            estimator=rf,
            param_grid=param_grid,
            scoring='accuracy',
            cv=stratified_kf,
            n_jobs=-1,  # Use all available CPU cores
            verbose=1
        )

        # Perform grid search on the training data
        grid_search.fit(X_train, y_train)

        # Best parameters from GridSearchCV
        print(f"Best Parameters: {grid_search.best_params_}")

        # Train the model with the best parameters
        best_rf = grid_search.best_estimator_



        # Generate predictions for depths from 30 ft to 200 ft
        predictions = []
        # for depth in range(40, 201, 10):  # Depth increments of 10 ft
        input_features = pd.DataFrame([[latitude, longitude, depth]], columns=['Lat', 'Long', 'Depth'])
        prediction = best_rf.predict(input_features)[0]
        predictions.append({'depth': depth, 'prediction': le.inverse_transform([prediction])[0]})

        # Return predictions as JSON
        return jsonify({'predictions': predictions})

    except Exception as e:
        print("Error:", str(e))  # Print error details
        return jsonify({'error': str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
