package analyzer

import (
	"context"
	"fmt"
	"time"

	pb "github.com/andrepribavkin/calendar-management/proto/analyzer/v1"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type Client struct {
	conn   *grpc.ClientConn
	client pb.AnalyzerServiceClient
}

func New(target string) (*Client, error) {
	// Connect to the gRPC server
	conn, err := grpc.NewClient(target, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return nil, fmt.Errorf("grpc connect: %w", err)
	}

	return &Client{
		conn:   conn,
		client: pb.NewAnalyzerServiceClient(conn),
	}, nil
}

func (c *Client) Close() error {
	return c.conn.Close()
}

func (c *Client) Analyze(ctx context.Context, tgUserID int64, text string) (*pb.AnalyzeTextResponse, error) {
	ctx, cancel := context.WithTimeout(ctx, 10*time.Second)
	defer cancel()

	req := &pb.AnalyzeTextRequest{
		TgUserId: tgUserID,
		Text:     text,
		Timezone: "UTC", // TODO: Get from user settings
	}

	resp, err := c.client.AnalyzeText(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("analyze text: %w", err)
	}

	return resp, nil
}
