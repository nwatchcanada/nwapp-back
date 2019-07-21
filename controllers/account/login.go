package account

import (
    "fmt"
    "net/http"
    // "io/ioutil"
    // "encoding/json"

    // "github.com/nwatchcanada/nwapp-back/models"
    "github.com/nwatchcanada/nwapp-back/serializers"
)



func PostLogin(w http.ResponseWriter, r *http.Request) {
    s := serializers.LoginSerializer{Request: r}
    user, err := s.Deserialize()
    if err != nil {
        fmt.Println(err)
        fmt.Printf("%+v\n", user)
        w.WriteHeader(http.StatusBadRequest)
        return
    }

    fmt.Printf("%+v\n", user)

    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusBadRequest)

    // //
    // // READ FROM REQUEST
    // //
    // // STEP 1: Get our binary data from the request.
    // buf, err := ioutil.ReadAll(r.Body)
    // if err!=nil {
    //     fmt.Println(err)
    //     w.WriteHeader(http.StatusBadRequest)
    //     return
    // }
    //
    // var data LoginData
    //
    // // De-serialize bytes into our struct object.
    // err = json.Unmarshal(buf, &data)
    // if err != nil {
    //     fmt.Println(err)
    //     fmt.Printf("%+v\n", data)
    //     w.WriteHeader(http.StatusBadRequest)
    //     return
    // }
    //
    // fmt.Printf("%+v\n", data.Email)
    // fmt.Printf("%+v\n", data.Password)
//
    // w.WriteHeader(http.StatusBadRequest)
}

//https://stackoverflow.com/questions/3316762/what-is-deserialize-and-serialize-in-json
