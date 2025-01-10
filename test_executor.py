import json
import requests
import logging

# Flask server URL
FLASK_URL = "http://127.0.0.1:5000/execute-task"

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def run_test(payload):
    """Send a test payload to the Flask server."""
    response = requests.post(FLASK_URL, json=payload)
    return response.json()

def run_all_tests():
    """Execute all tests and save results."""
    # Load test cases
    with open("test_cases.json", "r") as file:
        test_cases = json.load(file)

    results = []
    for test in test_cases:
        logging.info(f"Running test: {test['description']}")
        result = run_test(test["payload"])
        results.append({
            "description": test["description"],
            "result": result
        })
        logging.info(f"Result: {result}\n")

    # Save results
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=4)
    logging.info("Test results saved to test_results.json.")

if __name__ == "__main__":
    run_all_tests()