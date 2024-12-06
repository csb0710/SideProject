package main

import (
	"context"
	"fmt"
	"log"
	"net"

	"service2/pb" // services.pb.go 파일이 위치한 패키지
	"google.golang.org/grpc"
)

type Service2Server struct {
	pb.UnimplementedService2Server
}

func (s *Service2Server) ProcessData(ctx context.Context, req *pb.ServiceRequest) (*pb.ServiceResponse, error) {
	input := req.GetMessage()
	fmt.Printf("Received message: %s\n", input)

	// 처리된 결과를 응답으로 반환
	response := &pb.ServiceResponse{
		Result: fmt.Sprintf("Processed: %s", input),
	}

	return response, nil
}

func (s *Service2Server) ExchangeData(ctx context.Context, req *pb.ExchangeRequest) (*pb.ExchangeResponse, error) {
	input := req.GetInput()
	fmt.Printf("Service2 received: %s\n", input)

	// 요청 처리 (예: 간단히 입력을 변형해서 응답)
	output := fmt.Sprintf("service2 generates a response: %s", input)

	return &pb.ExchangeResponse{Output: output}, nil
}

func main() {
	// gRPC 서버 초기화
	listener, err := net.Listen("tcp", ":50052")
	if err != nil {
		log.Fatalf("Failed to listen on port 50052: %v", err)
	}

	grpcServer := grpc.NewServer()
	pb.RegisterService2Server(grpcServer, &Service2Server{})

	fmt.Println("Service2 is running on port 50052...")
	if err := grpcServer.Serve(listener); err != nil {
		log.Fatalf("Failed to serve gRPC server: %v", err)
	}
}
