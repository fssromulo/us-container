import toCapitalizedWithSpaces from "./toCapitalizedWithSpaces"

const getRouteStatus = (completeRoute) => {
  let v = toCapitalizedWithSpaces(
    completeRoute.currentRoute.value.query["status"]
  )
  return v
}

const currentRouteStatus = (completeRoute) => {
  if (completeRoute.currentRoute.value.query.hasOwnProperty("status")) {
    let routeStatus = getRouteStatus(completeRoute)
    return routeStatus
  } else {
    return null
  }
}

export default currentRouteStatus
