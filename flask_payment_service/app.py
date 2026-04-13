"""
flask_payment_service/app.py

Microservicio de Pagos — CellHub
Patrón Estrangulador: reemplaza /api/v1/payments/ (Django) con /api/v2/payments/ (Flask)

Expone:
  POST /api/v2/payments/process/   — Procesa un pago
  GET  /api/v2/payments/methods/   — Lista métodos disponibles
  GET  /api/v2/payments/health/    — Health check
"""

from flask import Flask, jsonify, request
from processors import PaymentProcessor, PaymentFactory

app = Flask(__name__)


# ── Health check ─────────────────────────────────────────────────────────────

@app.route("/api/v2/payments/health/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "flask-payment-service"}), 200


# ── Métodos disponibles ───────────────────────────────────────────────────────

@app.route("/api/v2/payments/methods/", methods=["GET"])
def available_methods():
    return jsonify({"methods": PaymentFactory.available_methods()}), 200


# ── Procesar pago ─────────────────────────────────────────────────────────────

@app.route("/api/v2/payments/process/", methods=["POST"])
def process_payment():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "El cuerpo de la petición debe ser JSON válido"}), 400

    payment_method = body.get("payment_method")
    amount = body.get("amount")
    payment_data = body.get("payment_data", {})

    # Validaciones de campos requeridos
    if not payment_method:
        return jsonify({"error": "El campo 'payment_method' es requerido"}), 400
    if amount is None:
        return jsonify({"error": "El campo 'amount' es requerido"}), 400
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"error": "'amount' debe ser un número mayor a 0"}), 400

    # Obtener procesador via Factory
    try:
        processor = PaymentFactory.get_processor(payment_method)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Validar datos del método de pago
    if not processor.validate(payment_data):
        return jsonify({
            "error": f"Datos insuficientes para el método '{payment_method}'",
            "hint": processor.required_fields()
        }), 400

    # Procesar
    try:
        result = processor.process(amount=amount, data=payment_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "Error interno al procesar el pago", "detail": str(e)}), 500


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
