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
    // Set our header.
    w.Header().Set("Content-Type", "application/json")

    // Take our request and validate the credentials inputted by the user.
    s := serializers.LoginSerializer{Request: r}
    user, err := s.Deserialize()
    if err != nil {
        fmt.Println(err)
        fmt.Printf("%+v\n", user)
        w.WriteHeader(http.StatusBadRequest)
        return
    }

    // If we get to this line of code then we will be serializing our `User`
    // and returning our data.
    profileSerializer := serializers.ProfileSerializer{Request: r,}
    b, e := profileSerializer.Serialize(user)
    if e != nil {
        fmt.Println(e)
        w.WriteHeader(http.StatusBadRequest)
        return
    }
    w.Write(b) // Return our `[]byte` data.
}

//https://stackoverflow.com/questions/3316762/what-is-deserialize-and-serialize-in-json
