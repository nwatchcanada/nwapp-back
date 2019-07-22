# Contributing to Neigbhourhood Watch Canada App

## Do you have questions about the source code?

* Ask any question about how to use Neigbhourhood Watch App in the [mailing list](https://groups.google.com/forum/#!forum/nwl-app).

## Do you intend to add a new feature or change an existing one?
* Suggest your change in the [mailing list](https://groups.google.com/forum/#!forum/nwl-app). and start writing code.

* Do not open an issue on GitHub until you have collected positive feedback about the change. GitHub issues are primarily intended for bug reports and fixes.

## What libraries does this project use?
Here are the libraries that this project utilizes, please update this list as
new libraries get added.

```bash
go get -u github.com/go-chi/chi
go get -u github.com/go-chi/chi/middleware
go get -u github.com/go-chi/render
go get -u github.com/go-chi/jwtauth
go get -u github.com/go-chi/valve
go get -u github.com/joho/godotenv        # Environment Variable Loader
go get -u github.com/lib/pq               # Postgres DB Driver for Golang
go get -u github.com/jmoiron/sqlx         # General purpose extensions to golang's database/sql
go get -u golang.org/x/crypto/bcrypt      # Bycrypt Hashing Algorithm
go get -u github.com/spf13/cobra/cobra    # Modern Go CLI interactions
go get -u github.com/dgrijalva/jwt-go     # JWT Library

go get -u github.com/go-chi/docgen
```
