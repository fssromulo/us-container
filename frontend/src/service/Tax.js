export default class Tax {
  calculateTax = async (
    container,
    deliver,
    taxes,
    buyType,
    downPaymentStrategy,
    shipping_revenue,
    destination_state
  ) => {
    let taxableRevenue
    if (buyType === "RENT") {
      console.log("calculating taxable revenue -- RENT")
      if (downPaymentStrategy === "FIRST_MONTH_PLUS_DELIVERY_&_PICKUP") {
        console.log(
          "calculating taxable revenue -- RENT -- FIRST_MONTH_PLUS_DELIVERY_&_PICKUP"
        )
        taxableRevenue = container.monthly_price + shipping_revenue * 2
      } else {
        console.log("calculating taxable revenue -- RENT -- ELSE")
        taxableRevenue = container.monthly_price + shipping_revenue
      }
    }

    if (buyType === "RENT_TO_OWN" || buyType === "PURCHASE") {
      console.log("calculating taxable revenue -- PURCHASE/RTO")
      taxableRevenue = container.price + shipping_revenue
    }

    if (!taxes) {
      return 0
    }

    const containerStateTax = taxes.find((s) => s.state === container.state)

    if (!deliver && containerStateTax) {
      return taxableRevenue * Number(containerStateTax.rate)
    }

    const customerStateTax = taxes.find((s) => s.state === destination_state)
    if (deliver && customerStateTax) {
      return taxableRevenue * Number(customerStateTax.rate)
    }
    return 0
  }

  prepareTaxRequest = (
    productState,
    fromZip,
    customerState,
    customerZip,
    shippingRevenue,
    quantity,
    containerRevenue
  ) => {
    return {
      from_zip: fromZip,
      from_state: productState,
      to_state: customerState,
      to_zip: customerZip,
      shipping: shippingRevenue,
      line_items: [
        {
          quantity: quantity,
          unit_price: containerRevenue
        }
      ]
    }
  }
}
