package middleware

import (
    "strconv"
    "context"
	"net/http"
)

// Middleware used to extract the `page` paramter from the URL and save it
// in the context.
func PaginatorCtx(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Setup our variables for the paginator.
        pageString := r.FormValue("page")
        pageIndex, err := strconv.ParseUint(pageString, 10, 64)
        if err != nil {
            // DEVELOPERS NOTE: WE ALWAYS START AT ONE AND NOT ZERO!
            pageIndex = 1
        }

        // Attach the 'page' parameter value to our context to be used.
		ctx := context.WithValue(r.Context(), "pageParm", pageIndex)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
