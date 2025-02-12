function capitalizeFirstLetter(str) {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

function toCapitalizedWithSpaces(inputString) {
  let v = inputString.replace(/_/g, " ").split(" ")
  v = v.map((el) => {
    return capitalizeFirstLetter(el)
  })
  return v.join(" ")
}
export default toCapitalizedWithSpaces
