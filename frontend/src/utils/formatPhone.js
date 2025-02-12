const formatPhoneNumber = (phoneNumberString) => {
  if (!phoneNumberString) return null
  return phoneNumberString
    .replace(/\D/g, "")
    .replace(/(\d{3})(\d{3})(\d{4})/, "($1)$2-$3")
}

export default formatPhoneNumber
