from flask import Flask, request, jsonify
import grpc
import services_pb2
import services_pb2_grpc

app = Flask(__name__)

ACCESS_TOKENS = {
    "service1": "token_service1",
    "service2": "token_service2",
}

def authenticate_service(service_name, token):
    return ACCESS_TOKENS.get(service_name) == token


@app.route("/service1/process", methods=["POST"])
def call_service1_process():
    token = request.headers.get("Authorization")
    if not authenticate_service("service1", token):
        return jsonify({"error": "Unauthorized"}), 403

    message = request.json.get("message")
    channel = grpc.insecure_channel("service1:50051")
    stub = services_pb2_grpc.Service1Stub(channel)
    response = stub.ProcessData(services_pb2.ServiceRequest(message=message))
    return jsonify({"result": response.result})

@app.route("/service1", methods=["GET"])
def call_service1_get():
    token = request.headers.get("Authorization")
    if not authenticate_service("service1", token):
        return jsonify({"error": "Unauthorized"}), 403

    channel = grpc.insecure_channel("service1:50051")
    stub = services_pb2_grpc.Service1Stub(channel)
    response = stub.GetData(services_pb2.ServiceRequest(message=""))
    return jsonify({"result": response.result})

@app.route("/service1/<message>", methods=["DELETE"])
def call_service1_delete(message):
    token = request.headers.get("Authorization")
    if not authenticate_service("service1", token):
        return jsonify({"error": "Unauthorized"}), 403

    channel = grpc.insecure_channel("service1:50051")
    stub = services_pb2_grpc.Service1Stub(channel)
    response = stub.DeleteData(services_pb2.ServiceRequest(message=message))
    return jsonify({"result": response.result})

@app.route("/service1", methods=["POST"])
def call_service1_post():
    token = request.headers.get("Authorization")
    if not authenticate_service("service1", token):
        return jsonify({"error": "Unauthorized"}), 403

    message = request.json.get("message")
    channel = grpc.insecure_channel("service1:50051")
    stub = services_pb2_grpc.Service1Stub(channel)
    response = stub.PostData(services_pb2.ServiceRequest(message=message))
    return jsonify({"result": response.result})

@app.route("/service2", methods=["POST"])
def call_service2():
    token = request.headers.get("Authorization")
    if not authenticate_service("service2", token):
        return jsonify({"error": "Unauthorized"}), 403

    message = request.json.get("message")
    channel = grpc.insecure_channel("service2:50052")
    stub = services_pb2_grpc.Service2Stub(channel)
    response = stub.ExchangeData(services_pb2.ExchangeRequest(input=message))
    return jsonify({"result": response.output})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)