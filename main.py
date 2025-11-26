import asyncio
from flask import Flask, jsonify, render_template
from controller import AppController

app = Flask(__name__)
controller = AppController()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/start")
def start_app():
    try:
        controller.start()
        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/toggle_ai")
def toggle_ai():
    status = controller.toggle_ai()
    return jsonify({"ai_enabled": status})

@app.route("/status")
def status():
    return jsonify(controller.get_status())

@app.route("/set_agent_type", methods=["POST"])
def set_agent_type():
    try:
        from flask import request
        data = request.get_json()
        agent_type = data.get("agent_type", "default")
        result = controller.set_agent_type(agent_type)
        return jsonify({"status": "success", "agent_type": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/stop")
def stop_app():
    try:
        controller.stop()
        return jsonify({"status": "stopped"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
