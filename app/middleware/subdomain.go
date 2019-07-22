package middleware

import (
    "context"
    "strings"
	"net/http"
)


/**
 *  Utility middleware which will store the `subdomain` in our context.
 */
func Subdomain(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        domainParts := strings.Split(r.Host, ".")

        // Attach the 'subdomain' parameter value to our context to be used.
		ctx := context.WithValue(r.Context(), "subdomain", domainParts[0])
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
