package server

import "fmt"

// Config holds server configuration.
type Config struct {
	Host    string
	Port    int
	Verbose bool
}

// Handler defines the request handling interface.
type Handler interface {
	ServeHTTP(path string) string
	Middleware(next Handler) Handler
}

// NewConfig creates a Config with sensible defaults.
func NewConfig(host string, port int) Config {
	return Config{
		Host:    host,
		Port:    port,
		Verbose: false,
	}
}

// Address returns the host:port string.
func (c Config) Address() string {
	return fmt.Sprintf("%s:%d", c.Host, c.Port)
}

// SetVerbose enables verbose logging.
func (c *Config) SetVerbose(enabled bool) {
	c.Verbose = enabled
}
