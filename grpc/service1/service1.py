from concurrent import futures
import grpc
import services_pb2
import services_pb2_grpc

# gRPC 클라이언트를 통해 Service2와 통신
import grpc

data_list = []

def call_service2(input_data):
    with grpc.insecure_channel('service2:50052') as channel:  # Service2 주소
        stub = services_pb2_grpc.Service2Stub(channel)
        response = stub.ExchangeData(services_pb2.ExchangeRequest(input=input_data))
        return response.output


class Service1Servicer(services_pb2_grpc.Service1Servicer):
    def ProcessData(self, request, context):
        input_data = request.message
        print(f"Service1 received: {input_data}")

        # Service2 호출
        processed_data = call_service2(input_data)

        result = f"Communication with service2 has been completed and a response has been generated. : {processed_data}"
        return services_pb2.ServiceResponse(result=result)

    def GetData(self, request, context):
        return services_pb2.ServiceResponse(result=", ".join(data_list))
    
    def PostData(self, request, context):
        # 리스트에 새 값 추가
        data_list.append(request.message)
        return services_pb2.ServiceResponse(result=", ".join(data_list))

    def DeleteData(self, request, context):
        message = request.message
        print(data_list)
        print(message in data_list)
        if message in data_list:
            data_list.remove(message)
            return services_pb2.ServiceResponse(result=f"Data {message} removed, data: {', '.join(data_list)}")
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"{message} not found in data")
            return services_pb2.ServiceResponse(result=f"Error: {message} not found")


def serve():
    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        services_pb2_grpc.add_Service1Servicer_to_server(Service1Servicer(), server)
        server.add_insecure_port('[::]:50051')
        print("Service1 is running on port 50051...")
        server.start()
        server.wait_for_termination()
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == '__main__':
    serve()
