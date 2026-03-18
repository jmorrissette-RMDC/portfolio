import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# A common function that combines and optimizes logic from multiple submissions
def process_data(input_data):
    try:
        # Assume logic from submissions that provide both efficiency and clarity
        processed_data = complex_business_logic(input_data)
        logging.info("Processing successful")
        return processed_data
    except Exception as e:
        logging.error(f"Error processing data: {e}")
        raise

def complex_business_logic(input_data):
    # Example of utilizing an optimized algorithm from a junior submission
    # Simulated placeholder logic
    return {"processed": input_data}

@app.route('/process', methods=['POST'])
def process_endpoint():
    try:
        data = request.json
        result = process_data(data)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Endpoint error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True)