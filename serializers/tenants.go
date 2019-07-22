package serializers

import (
    // "fmt"
    "net/http"
//     "io/ioutil"
    "encoding/json"

    "github.com/nwatchcanada/nwapp-back/models"
)


/**
 *  The tenant list serializer structure. All our functions below are in
 *  relation to this structure.
 */
type TenantListSerializer struct {
    Request *http.Request
}


type TenantListItemResponse struct {
    Name    string `json:"name"`
    Schema  string `json:"schema"`
}

type TenantListResponse struct {
    Page       uint64                    `json:"page"`
    Count      uint64                    `json:"count"`
    Results    []TenantListItemResponse  `json:"results"`
}

func (s *TenantListSerializer) translate(rows []models.Tenant) []TenantListItemResponse {
    results := []TenantListItemResponse{}
    for _, v := range rows {
        item := TenantListItemResponse{
            Name: v.Name.String,
            Schema: v.Schema.String,
        }
        results = append(results, item)
    }
    return results[:]
}


/**
 *  Function will serialize the model `profile` data into a []byte format
 *  ready for output by our API as JSON data.
 */
func (s *TenantListSerializer) Serialize(tenants []models.Tenant, context map[string]interface{}) []byte {
    results := s.translate(tenants)

    page := context["page"].(uint64)
    count := context["count"].(uint64)
    tenantList := TenantListResponse{
        Page: page,
        Count: count,
        Results: results,
    }

    // Serialize our data.
    b, err := json.Marshal(tenantList)
    if err != nil {
        panic(err)
    }

    return b
}
