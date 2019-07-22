package account

import (
    // "fmt"
    "net/http"
    // "io/ioutil"
    // "encoding/json"

    // "github.com/nwatchcanada/nwapp-back/utils"
    // "github.com/nwatchcanada/nwapp-back/serializers"
)



func GetProfile(w http.ResponseWriter, r *http.Request) {
    // Set our header.
    w.Header().Set("Content-Type", "application/json")

    w.WriteHeader(http.StatusInternalServerError)
}

//https://stackoverflow.com/questions/3316762/what-is-deserialize-and-serialize-in-json
