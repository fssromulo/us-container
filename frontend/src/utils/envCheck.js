export function envCheck() {
  if (
    window.location.host == "localhost:5173" ||
    window.location.host == "localhost:5174"
  ) {
    return true
  }
  return false
}
