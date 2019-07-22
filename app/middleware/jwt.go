package middleware

import (
    "log"
    // "context"
	"net/http"
)

func JWTMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Do stuff here
        log.Println(">>>", r.RequestURI)
        // Call the next handler, which can be another middleware in the chain, or the final handler.
        next.ServeHTTP(w, r)

        // user_id := service.GetUserIDFromContext(r.Context())
    	// if user_id == 0 {
    	// 	http.Error(w, "User ID not inputted.", http.StatusUnauthorized)
    	// 	return
    	// }
        // user, count := model_manager.UserManagerInstance().GetByID(user_id)
        // if count == 0  {
    	// 	http.Error(w, "No User found with ID.", http.StatusUnauthorized)
    	// 	return
    	// }
		// ctx := context.WithValue(r.Context(), "user", user)
		// next.ServeHTTP(w, r.WithContext(ctx))
	})
}
