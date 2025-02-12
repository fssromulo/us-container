function toCamelCase(inputString) {
  // Replace spaces and other delimiters with a single space
  const words = inputString.split(/[\s_\-]+/)

  // Capitalize the first letter of each word (except the first one)
  const camelCased = words.map((word, index) => {
    if (index === 0) {
      return word.charAt(0).toLowerCase() + word.slice(1)
    } else {
      return word.charAt(0).toUpperCase() + word.slice(1)
    }
  })

  // Join the words to create the camelCase string
  return camelCased.join("")
}
export default toCamelCase
