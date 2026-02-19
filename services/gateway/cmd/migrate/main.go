package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/joho/godotenv"
)

func main() {
	var migrationsDir string
	flag.StringVar(&migrationsDir, "dir", "supabase/migrations", "path to migrations directory")
	flag.Parse()

	loadEnv()

	dbURL := strings.TrimSpace(os.Getenv("DATABASE_URL"))
	if dbURL == "" {
		log.Fatal("DATABASE_URL must be set")
	}

	resolvedDir, err := resolveMigrationsDir(migrationsDir)
	if err != nil {
		log.Fatal(err)
	}

	files, err := migrationFiles(resolvedDir)
	if err != nil {
		log.Fatal(err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()

	db, err := pgxpool.New(ctx, dbURL)
	if err != nil {
		log.Fatalf("db connect: %v", err)
	}
	defer db.Close()

	if err := db.Ping(ctx); err != nil {
		log.Fatalf("db ping: %v", err)
	}

	for _, file := range files {
		sqlBytes, err := os.ReadFile(file)
		if err != nil {
			log.Fatalf("read migration %s: %v", file, err)
		}

		if strings.TrimSpace(string(sqlBytes)) == "" {
			continue
		}

		log.Printf("applying migration: %s", file)
		if _, err := db.Exec(ctx, string(sqlBytes)); err != nil {
			log.Fatalf("apply migration %s: %v", file, err)
		}
	}

	log.Printf("migrations applied successfully (%d files)", len(files))
}

func loadEnv() {
	if p := strings.TrimSpace(os.Getenv("ENV_FILE")); p != "" {
		if err := godotenv.Load(p); err != nil {
			log.Fatalf("failed to load env file %s: %v", p, err)
		}
		return
	}

	_ = godotenv.Load()
}

func resolveMigrationsDir(dir string) (string, error) {
	candidates := []string{
		dir,
		filepath.Join("..", "..", "..", dir),
	}

	for _, candidate := range candidates {
		if candidate == "" {
			continue
		}

		info, err := os.Stat(candidate)
		if err != nil {
			continue
		}

		if info.IsDir() {
			return candidate, nil
		}
	}

	return "", fmt.Errorf("migrations directory not found: %s", dir)
}

func migrationFiles(dir string) ([]string, error) {
	files, err := filepath.Glob(filepath.Join(dir, "*.sql"))
	if err != nil {
		return nil, fmt.Errorf("glob migrations: %w", err)
	}
	if len(files) == 0 {
		return nil, fmt.Errorf("no migrations found in %s", dir)
	}

	sort.Strings(files)
	return files, nil
}
