import { DateTime } from "luxon"
import { Settings } from "luxon"
Settings.defaultZoneName = "America/Denver"

export default class LineItemsService {
  transformDate(date) {
    return DateTime.fromISO(date).toLocaleString(DateTime.DATETIME_MED)
  }

  dtoLineItem(driver) {
    return Object.assign({}, driver, {
      created_at: this.transformDate(driver.created_at),
      modified_at: this.transformDate(driver.modified_at)
    })
  }
}
