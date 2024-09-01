from flask import Flask, request, jsonify, make_response
import requests

app = Flask(__name__)

# Configuration de l'URL de base de votre instance Apache NiFi
NIFI_URL = "http://localhost:8080"  # Remplacez par l'URL et le port de votre instance NiFi

# Afficher toute la table reservations
@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    try:
        response = requests.get(f"{NIFI_URL}/api/reservations")
        response.raise_for_status()
        return make_response(response.json(), response.status_code)
    except requests.exceptions.RequestException as e:
        return make_response(str(e), 500)

# Afficher une ligne par l'ID
@app.route('/api/reservations/<int:id>', methods=['GET'])
def get_reservation_by_id(id):
    try:
        response = requests.get(f"{NIFI_URL}/api/reservations/{id}")
        
        # Assurez-vous que NiFi renvoie des codes de statut corrects
        if response.status_code == 404:
            return make_response({"error": "Reservation not found"}, 404)
        elif response.status_code == 500:
            return make_response({"error": "Internal Server Error"}, 500)
        else:
            response.raise_for_status()
        
        data = response.json()
        if not data:  # Si la réponse est une liste vide
            return make_response({"error": "Reservation not found"}, 404)
        
        return make_response(data, 200)
    except requests.exceptions.RequestException as e:
        return make_response({"error": str(e)}, 500)


# Insérer des données
@app.route('/api/reservations', methods=['POST'])
def create_reservation():
    try:
        json_data = request.json
        response = requests.post(f"{NIFI_URL}/api/reservations", json=json_data)
        response.raise_for_status()
        return make_response(response.json(), response.status_code)
    except requests.exceptions.RequestException as e:
        return make_response(str(e), 400)

# Modifier des données
@app.route('/api/reservations/<int:id>', methods=['PUT'])
def update_reservation(id):
    valid_fields = ['numero_de_chambre', 'type_de_chambre', 'nom_du_client', 'date_d_entree', 'date_de_sortie', 'statut']
    json_data = request.json
    
    if json_data is None:
        return make_response(jsonify({"error": "No data provided"}), 400)

    # Vérifiez que les champs présents dans json_data sont tous valides
    invalid_fields = [field for field in json_data if field not in valid_fields]
    if invalid_fields:
        return make_response(jsonify({"error": f"Invalid fields: {', '.join(invalid_fields)}"}), 400)

    try:
        # Ajouter l'ID au corps du JSON
        json_data['id'] = id
        
        # Envoyer les données à NiFi
        response = requests.put(f"{NIFI_URL}/api/reservations/{id}", json=json_data)
        
        if response.status_code == 404:
            return make_response(jsonify({"error": "Reservation not found"}), 404)
        
        response.raise_for_status()
        return make_response(response.json(), response.status_code)
    except requests.exceptions.RequestException as e:
        return make_response(jsonify({"error": str(e)}), 400)

# Supprimer des données
@app.route('/api/reservations/<int:id>', methods=['DELETE'])
def delete_reservation(id):
    try:
        # Vérifiez si le corps de la requête contient des données JSON
        if request.data:  # S'assure qu'il y a des données à décoder
            json_data = request.json  # Tente de décoder le JSON
        else:
            json_data = {}  # Si le corps est vide, initialiser un dictionnaire vide

        json_data['id'] = id  # Ajouter l'ID au corps du JSON
        response = requests.delete(f"{NIFI_URL}/api/reservations/{id}", json=json_data)
        response.raise_for_status()
        return make_response(response.json(), response.status_code)
    except requests.exceptions.RequestException as e:
        return make_response(str(e), 500)
    except ValueError:  # Si le JSON n'est pas décodable
        return make_response("Invalid JSON format", 400)



if __name__ == '__main__':
    app.run(debug=True)
