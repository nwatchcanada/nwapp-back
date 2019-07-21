package utils

import (
    // "fmt"
    "net/http"
    "io/ioutil"
    // "log"
    "github.com/ugorji/go/codec"
)

// https://golang.org/src/net/http/status.go


func GetJSONFromMessagePackRequest(r *http.Request) (string, error) {
    // Get our binary data from the request.
    buf, err := ioutil.ReadAll(r.Body)
    if err !=nil {
        return "", err
    }
    // fmt.Println("BUF", buf) // For debugging purposes only.

    // STEP 2: Create the string output.
    var jsonString string

    // STEP 3: Convert our binary data to string and error if anything bad happens.
    dec := codec.NewDecoderBytes(buf, new(codec.MsgpackHandle))
    if err := dec.Decode(&jsonString); err != nil {
        return "", err
    }
    return jsonString, nil
}
