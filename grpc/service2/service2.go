package main

import (
	"context"
	"fmt"
	"log"
	"net"

	"service2/pb"
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

	output := fmt.Sprintf("service2 generates a response: %s", input)

	return &pb.ExchangeResponse{Output: output}, nil
}

func main() {
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
