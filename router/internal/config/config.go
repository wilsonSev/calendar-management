package config

import (
	"flag"
	"os"
	"time"

	"github.com/ilyakaznacheev/cleanenv"
)

type Config struct {
	Env            string        `yaml:"env" env-default:"local"`
	DatabaseURL    string        `yaml:"database_url" env-required:"true"`
	StorageTimeout time.Duration `yaml:"storage_timeout" env-default:"5s"`
	TokenTTL       time.Duration `yaml:"token_ttl" env-default:"1h"`
	GRPC           GRPCConfig    `yaml:"grpc" env-required:"true"`
	Google         GoogleConfig  `yaml:"google" env-required:"true"`
}

type GRPCConfig struct {
	Port    int           `yaml:"port" env-required:"true"`
	Timeout time.Duration `yaml:"timeout" env-required:"true"`
}

type GoogleConfig struct {
	ClientID     string `yaml:"client_id" env-required:"true"`
	ClientSecret string `yaml:"client_secret" env-required:"true"`
}

func MustLoad() *Config {
	path := fetchConfigPath()

	if path == "" {
		panic("config file path is empty")
	}

	if _, err := os.Stat(path); os.IsNotExist(err) {
		panic("config file not found")
	}

	var cfg Config

	if err := cleanenv.ReadConfig(path, &cfg); err != nil {
		panic(err)
	}

	return &cfg
}

func fetchConfigPath() string {
	var res string
	flag.StringVar(&res, "config", "config.yaml", "config file path")
	flag.Parse()

	if res == "" {
		res = os.Getenv("CONFIG_PATH")
	}

	return res
}
