package app

import (
    "context"
    "fmt"
    "net/http"
    "runtime"
    "os"
	"os/signal"
    "time"

    _ "github.com/lib/pq"
    "github.com/jmoiron/sqlx"

    "github.com/go-chi/chi"
    "github.com/go-chi/chi/middleware"
    "github.com/go-chi/render"
	"github.com/go-chi/jwtauth"
	"github.com/go-chi/valve"
	"github.com/go-chi/cors"

    "github.com/nwatchcanada/nwapp-back/models"
    "github.com/nwatchcanada/nwapp-back/controllers"
    "github.com/nwatchcanada/nwapp-back/controllers/account"
    "github.com/nwatchcanada/nwapp-back/utils"
    app_mw "github.com/nwatchcanada/nwapp-back/app/middleware"
)

/**
 * Initialize our applications shared functions.
 */
func init() {
	runtime.GOMAXPROCS(runtime.NumCPU())  // Use all CPU cores
}


/**
 *  Class used to store our web-application.
 */
type App struct {
    DB *sqlx.DB
}

/**
 *  Initialize the web-application with the database credentials.
 */
func (a *App) Initialize(dbHost, dbPort, dbUser, dbPassword, dbName string) {
    // Initialize and connect our database layer for the entire application.
    a.DB = models.InitDB(dbHost, dbPort, dbUser, dbPassword, dbName)

    // Create our models
    models.CreateTenantTable(false)
    models.CreateUserTable(false)
}

/**
 *  Run the server.
 */
func (a *App) Run(addr string) {

    // Our graceful valve shut-off package to manage code preemption and
	// shutdown signaling.
	valv := valve.New()
	baseCtx := valv.Context()
	r := chi.NewRouter()

    //--------------------------------//
	// Load up our global middleware. //
	//--------------------------------//
    r.Use(middleware.RequestID)
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.URLFormat)
	r.Use(render.SetContentType(render.ContentTypeJSON))

    // Basic CORS
    // for more ideas, see: https://developer.github.com/v3/#cross-origin-resource-sharing
    cors := cors.New(cors.Options{
        AllowedOrigins:   []string{"*"},
        AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
        AllowedHeaders:   []string{"Accept", "Authorization", "Content-Type", "X-CSRF-Token"},
        ExposedHeaders:   []string{"Link"},
        AllowCredentials: true,
        MaxAge:           300, // Maximum value not ignored by any of major browsers
    })
    r.Use(cors.Handler)

    //------------------------------------------------------------------------//
    // Load up our non-protected API endpoints. The following API endpoints   //
    // can be accessed regardless of whether a JWT token was provided or not. //
    //------------------------------------------------------------------------//
    r.Get("/version", controllers.GetVersion)
    r.Get("/hello", controllers.PostHello)
    // r.Post("/api/v1/public/register", controllers.RegisterFunc)
    r.Post("/api/v1/public/login", account.PostLogin)

    //------------------------------------------------------------------------//
	// Load up our protected API endpoints. The following API endpoints can   //
	// only be accessed with submission of a JWT token in the header.         //
	//------------------------------------------------------------------------//
	r.Group(func(r chi.Router) {
		//--------------------------------------------------------------------//
		//                             Middleware                             //
		//--------------------------------------------------------------------//
		// Seek, verify and validate JWT tokens
		r.Use(jwtauth.Verifier(utils.GetJWTTokenAuthority()))

		// Handle valid / invalid tokens. In the following API endpoints, we use
		// the provided authenticator middleware, but you can write your
		// own very easily, look at the Authenticator method in jwtauth.go
		// and tweak it, its not scary.
		r.Use(jwtauth.Authenticator)

        // This is the comics cantina authenticated user middleware which will
		// lookup the verified JWT token and attach as a context to the request.
		r.Use(app_mw.ProfileCtx)

		//--------------------------------------------------------------------//
		//                           API endpoints                            //
		//--------------------------------------------------------------------//

		// User
		r.Get("/api/v1/profile", account.GetProfile)
    })

    //------------------------------------------------------------------------//
    //                         HTTP Running Server                            //
    //------------------------------------------------------------------------//

    // Attach database closing when the app terminates.
    defer a.DB.Close()

    // Integrate our server with our base context.
	srv := http.Server{Addr: addr, Handler: chi.ServerBaseContext(baseCtx, r)}

    // The following code was taken from the following repo:
	// https://github.com/go-chi/chi/blob/0c5e7abb4e562fa14dd2548cb57b28f979a7dcd9/_examples/graceful/main.go#L88
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt)
	go func() {
		for range c {
			// sig is a ^C, handle it
			fmt.Println("shutting down..")

			// first valv
			valv.Shutdown(20 * time.Second)

			// create context with timeout
			ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
			defer cancel()

			// start http shutdown
			srv.Shutdown(ctx)

			// verify, in worst case call cancel via defer
			select {
			case <-time.After(21 * time.Second):
				fmt.Println("not all connections done")
			case <-ctx.Done():

			}
		}
	}()
	srv.ListenAndServe()

    // // Start our web-server.
	// http.ListenAndServe(":8080", r)
}
