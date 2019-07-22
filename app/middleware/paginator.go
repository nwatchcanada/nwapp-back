package middleware

import (
    "strconv"
    "context"
	"net/http"
)

/**
 *  Middleware which checks to see if the URL has a `page` and or `page_size`
 *  parameter in it and extracts the value.
 */
func Paginator(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Setup our variables for the paginator.
        pageString := r.FormValue("page")
        pageIndex, err := strconv.ParseUint(pageString, 10, 64)
        if err != nil {
            // DEVELOPERS NOTE: WE ALWAYS START AT ONE AND NOT ZERO!
            pageIndex = 1
        }

        pageSizeString := r.FormValue("page_size")
        pageSize, err2 := strconv.ParseUint(pageSizeString, 10, 64)
        if err2 != nil {
            // DEVELOPERS NOTE: ALWAYS DEFINE 100 IF NOT SPECIFIED.
            pageSize = 100
        }

        // Attach the 'page' parameter value to our context to be used.
		ctx := context.WithValue(r.Context(), "pageParm", pageIndex)
        ctx = context.WithValue(ctx, "pageSizeParam", pageSize)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
