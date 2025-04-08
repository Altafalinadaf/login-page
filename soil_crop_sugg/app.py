from flask import Flask, render_template, request, jsonify
import sqlite3
from database import create_connection

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_soil_types')
def get_soil_types():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM soil_properties")
    soil_types = cursor.fetchall()
    conn.close()
    return jsonify([{'id': st[0], 'name': st[1]} for st in soil_types])

@app.route('/get_crop_recommendations', methods=['POST'])
def get_crop_recommendations():
    data = request.json
    soil_type_id = data.get('soil_type_id')
    ph = float(data.get('ph'))
    nitrogen = float(data.get('nitrogen'))
    phosphorus = float(data.get('phosphorus'))
    potassium = float(data.get('potassium'))
    
    conn = create_connection()
    cursor = conn.cursor()
    
    # Get soil properties
    cursor.execute("""
    SELECT ph_min, ph_max, nitrogen_min, nitrogen_max, 
           phosphorus_min, phosphorus_max, potassium_min, potassium_max, drainage
    FROM soil_properties WHERE id = ?
    """, (soil_type_id,))
    soil_props = cursor.fetchone()
    
    if not soil_props:
        return jsonify({"error": "Soil type not found"}), 404
    
    # Get all crops for this soil type
    cursor.execute("""
    SELECT crop_name, optimal_ph_min, optimal_ph_max, nitrogen_needs, 
           phosphorus_needs, potassium_needs, water_requirements
    FROM crop_recommendations WHERE soil_type_id = ?
    """, (soil_type_id,))
    crops = cursor.fetchall()
    
    # Score crops based on suitability
    recommendations = []
    for crop in crops:
        score = 0
        
        # PH compatibility (30% of total score)
        optimal_ph = (crop[1] + crop[2]) / 2
        ph_diff = abs(ph - optimal_ph)
        
        if ph >= crop[1] and ph <= crop[2]:
            score += 30  # Perfect pH match
        elif ph_diff <= 0.5:
            score += 25  # Very close to optimal
        elif ph_diff <= 1.0:
            score += 20  # Moderately close
        elif ph_diff <= 1.5:
            score += 10  # Somewhat close
        else:
            score += 5   # Not ideal but still possible
            
        # Nitrogen needs (20% of total score)
        nitrogen_score = 0
        if crop[3] == 'Low':
            if nitrogen < soil_props[2]:  # Below soil's min nitrogen
                nitrogen_score = 20
            elif nitrogen < soil_props[3]:  # Below soil's max nitrogen
                nitrogen_score = 15
            else:
                nitrogen_score = 5
        elif crop[3] == 'Medium':
            if nitrogen >= soil_props[2] and nitrogen <= soil_props[3]:
                nitrogen_score = 20
            elif (nitrogen >= soil_props[2] - 10 and nitrogen <= soil_props[3] + 10):
                nitrogen_score = 15
            else:
                nitrogen_score = 5
        elif crop[3] == 'High':
            if nitrogen > soil_props[3]:  # Above soil's max nitrogen
                nitrogen_score = 20
            elif nitrogen > soil_props[2]:  # Above soil's min nitrogen
                nitrogen_score = 15
            else:
                nitrogen_score = 5
        score += nitrogen_score
        
        # Phosphorus needs (20% of total score)
        phosphorus_score = 0
        if crop[4] == 'Low':
            if phosphorus < soil_props[4]:  # Below soil's min phosphorus
                phosphorus_score = 20
            elif phosphorus < soil_props[5]:  # Below soil's max phosphorus
                phosphorus_score = 15
            else:
                phosphorus_score = 5
        elif crop[4] == 'Medium':
            if phosphorus >= soil_props[4] and phosphorus <= soil_props[5]:
                phosphorus_score = 20
            elif (phosphorus >= soil_props[4] - 5 and phosphorus <= soil_props[5] + 5):
                phosphorus_score = 15
            else:
                phosphorus_score = 5
        elif crop[4] == 'High':
            if phosphorus > soil_props[5]:  # Above soil's max phosphorus
                phosphorus_score = 20
            elif phosphorus > soil_props[4]:  # Above soil's min phosphorus
                phosphorus_score = 15
            else:
                phosphorus_score = 5
        score += phosphorus_score
        
        # Potassium needs (20% of total score)
        potassium_score = 0
        if crop[5] == 'Low':
            if potassium < soil_props[6]:  # Below soil's min potassium
                potassium_score = 20
            elif potassium < soil_props[7]:  # Below soil's max potassium
                potassium_score = 15
            else:
                potassium_score = 5
        elif crop[5] == 'Medium':
            if potassium >= soil_props[6] and potassium <= soil_props[7]:
                potassium_score = 20
            elif (potassium >= soil_props[6] - 10 and potassium <= soil_props[7] + 10):
                potassium_score = 15
            else:
                potassium_score = 5
        elif crop[5] == 'High':
            if potassium > soil_props[7]:  # Above soil's max potassium
                potassium_score = 20
            elif potassium > soil_props[6]:  # Above soil's min potassium
                potassium_score = 15
            else:
                potassium_score = 5
        score += potassium_score
        
        # Water requirements (10% of total score)
        soil_drainage = soil_props[8]
        if (crop[6] == 'Low' and soil_drainage == 'Fast') or \
           (crop[6] == 'Moderate' and soil_drainage == 'Moderate') or \
           (crop[6] == 'High' and soil_drainage == 'Slow'):
            score += 10
        elif (crop[6] == 'Low' and soil_drainage == 'Moderate') or \
             (crop[6] == 'High' and soil_drainage == 'Moderate'):
            score += 5
        else:
            score += 2
        
        # Ensure score is between 0 and 100
        score = max(0, min(100, score))
        
        recommendations.append({
            'crop_name': crop[0],
            'score': score,
            'ph_range': f"{crop[1]} - {crop[2]}",
            'nitrogen_needs': crop[3],
            'phosphorus_needs': crop[4],
            'potassium_needs': crop[5],
            'water_requirements': crop[6],
            'ph_compatibility': "Good" if (ph >= crop[1] and ph <= crop[2]) else "Marginal",
            'nitrogen_status': get_nutrient_status(nitrogen, soil_props[2], soil_props[3], crop[3]),
            'phosphorus_status': get_nutrient_status(phosphorus, soil_props[4], soil_props[5], crop[4]),
            'potassium_status': get_nutrient_status(potassium, soil_props[6], soil_props[7], crop[5])
        })
    
    # Sort by score
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    conn.close()
    
    return jsonify(recommendations[:5])

def get_nutrient_status(value, soil_min, soil_max, crop_need):
    """Helper function to get nutrient status description"""
    if crop_need == 'Low':
        if value < soil_min:
            return "Ideal (low)"
        elif value < soil_max:
            return "Adequate"
        else:
            return "Potentially excessive"
    elif crop_need == 'Medium':
        if value >= soil_min and value <= soil_max:
            return "Ideal (medium)"
        elif value < soil_min:
            return "Potentially deficient"
        else:
            return "Potentially excessive"
    elif crop_need == 'High':
        if value > soil_max:
            return "Ideal (high)"
        elif value > soil_min:
            return "Adequate"
        else:
            return "Potentially deficient"
    return "Unknown"

if __name__ == '__main__':
    app.run(debug=True)