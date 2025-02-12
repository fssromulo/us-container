export let country = "USA"

export function changeCountry(newVal) {
  country = newVal
}

export function roundHalfUp(num) {
  return Math.round((num + Number.EPSILON) * 100) / 100
}

const formatCurrency = (value, agent_commission = false) => {
  if (value) {
    if (typeof value !== "number") {
      value = parseFloat(value)
    }
    if (country == null || country == "" || country == "USA") {
      return value.toLocaleString("en-US", {
        style: "currency",
        currency: "USD"
      })
    } else if (country == "Canada") {
      const formatter = new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "CAD",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })

      let formattedValue = formatter.format(value)
      formattedValue = formattedValue.replace("CA$", "$")

      return `${formattedValue} CAD`
    }
  } else if (agent_commission && !value) {
    return "N/A" // written for the commission refactoring to see if this will help with old order_commission records that do not have a manager or agent commission owed column
  }
  return 0
}

export default formatCurrency
