import { createAuth0 } from "@auth0/auth0-vue"

// if window.location conains localhost, use dev auth0 tenant
// else use container-crm tenant
let selectedTenant

const devTenants = ["localhost:5173"]

if (devTenants.find((t) => t === window.location.host)) {
  selectedTenant = createAuth0({
    domain: "dev-q7gskrpgi0lqzizg.us.auth0.com",
    client_id: "O7F5B4s8FMceEdOAwtyCeQxIPdJa2wKt",
    cacheLocation: "localstorage",
    redirect_uri: window.location.origin,
    audience: "containerCrmApi"
  })
}

export const auth0 = selectedTenant
