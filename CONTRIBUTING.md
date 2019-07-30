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
go get -u github.com/lib/pq               # Postgres DB Driver for Golang
go get -u github.com/jmoiron/sqlx         # General purpose extensions to golang's database/sql
go get -u golang.org/x/crypto/bcrypt      # Bycrypt Hashing Algorithm
go get -u github.com/spf13/cobra/cobra    # Modern Go CLI interactions
go get -u github.com/dgrijalva/jwt-go     # JWT Library

go get -u github.com/go-chi/docgen
```

## What conventions do we use?

### Code Style

Follow the [golang](https://golang.org/doc/effective_go.html) coding style as specified by [golang.org](https://golang.org).

Please run the ``gofmt`` application on all your code submissions.

```
gofmt -w -s nwapp-back
```

### Quality Standards

Please run the [GoReportCard](https://goreportcard.com/) on this project.

### Database Pagination
We do not delete any record, we simply set the state to be **deleted, archived, inactive, etc** state. We keep the data for auditing purposes and because we are implementing our offset as our ID for to do pagination. This decision was from [this article](https://developer.wordpress.com/2014/02/14/an-efficient-alternative-to-paging-with-sql-offsets/).


### API Design

(1) https://cloud.google.com/apis/design/design_patterns#list_pagination
