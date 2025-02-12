import { $DateTime } from "@/main"

export const dfs = (date) => {
  return $DateTime.fromISO(date).setZone("America/Denver").toFormat("MM/dd")
}

export const dfc = (date) => {
  return $DateTime.fromISO(date).toFormat("M/d/yy")
}

export const formatISODate = (date) => {
  const datetime_obj = $DateTime.fromISO(date, { zone: "UTC" })
  if (datetime_obj.invalid != undefined) {
    return ""
  }
  return $DateTime
    .fromObject({
      year: datetime_obj.year,
      month: datetime_obj.month,
      day: datetime_obj.day
    })
    .toFormat("M/d/yy")
}

export const dfc_without_zone = (date) => {
  return $DateTime.fromISO(date, { zone: "UTC" }).toFormat("M/d/yy")
}

export const dfm = (date) => {
  return $DateTime.fromISO(date).toFormat("MMM d, yyyy")
}

export const dfa = (date) => {
  return $DateTime
    .fromISO(date)
    .setZone("America/Denver")
    .toFormat("L/dd/yy, h:mm a")
}

export const dfl = (date) => {
  return $DateTime
    .fromISO(date)
    .setZone("America/Denver")
    .toLocaleString($DateTime.DATETIME_SHORT)
}

export const df = () => {
  return $DateTime.now().setZone("America/Denver").toFormat("M/d/yy")
}

export const convertDateForPost = (date) => {
  return new Date(
    Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate(), 0)
  )
}

export const convertDateForPostRealDate = (date) => {
  return new Date(
    Date.UTC(date.getFullYear(), date.getMonth(), date.getDate(), 0)
  )
}
