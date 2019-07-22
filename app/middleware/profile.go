package middleware

import (
    // "fmt"
    "context"
	"net/http"
	"github.com/nwatchcanada/nwapp-back/utils"
)


/**
 * Middleware takes the `claim` data from our `JWT Token` and sets this claims
 * data to our context for every request call.
 */
func ProfileCtx(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        email, schema, groupId := utils.GetJWTClaimsFromContext(r.Context())

        ctx := context.WithValue(r.Context(), "userEmail", email)
        ctx = context.WithValue(ctx, "userSchema", schema)
        ctx = context.WithValue(ctx, "userGroupId", groupId)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
