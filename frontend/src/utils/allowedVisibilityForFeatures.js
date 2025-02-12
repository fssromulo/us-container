export const isRentalsVisible = (
  isProd,
  accountId,
  rentalsEnabled,
  userEmail
) => {
  return rentalsEnabled
}

const canViewAccessoriesUsers = [
  "andrei@usacontainers.co",
  "tanner.cordovatech@gmail.com",
  "tanner_woodrum@techtanner.net",
  "tanner.woodrum1@gmail.com",
  "isaacbremang@gmail.com",
  "cornelao@gmail.com"
]

export const isAccessoriesVisible = (
  isProd,
  accountId,
  accessoriesEnabled,
  userEmail
) => {
  let isVisible = false
  if (isProd && accountId.toString() === "1") {
    isVisible =
      accessoriesEnabled && canViewAccessoriesUsers.includes(userEmail)
  } else {
    isVisible = accessoriesEnabled
  }
  return isVisible
}
