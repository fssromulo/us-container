function orderCanUseCreditCard(order) {
  if (order?.applications_overridden == null) return false
  const cc_index = order?.applications_overridden.find(
    (obj) => obj.name == "credit_card"
  )
  if (cc_index && cc_index.overridden) return true
  const cc_response = order?.application_response?.filter(
    (e) =>
      e.customer_application_schema.full_schema_name ==
      "Credit Card Application"
  )
  if (cc_response.length > 0 && cc_response[0].date_accepted) return true
  return false
}
export default orderCanUseCreditCard
